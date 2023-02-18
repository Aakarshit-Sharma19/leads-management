from logging import getLogger
from urllib.parse import urlencode

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from document_spaces.forms import SpaceUploadFileForm, SpaceDeleteFileForm
from leads_data.models import DocumentSpace, ResponseFile, DataFile
from services import exceptions as service_exceptions
from services.google.drive import DriveService
from services.google.sheets import SheetsService

logger = getLogger('portal')


class SpaceFileUploadView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    def test_func(self):
        if self.request.user.is_space_owner:
            return DocumentSpace.objects.filter(pk=self.kwargs['space_id'], owner=self.request.user).exists()
        else:
            return DocumentSpace.objects.filter(pk=self.kwargs['space_id'], managers=self.request.user).exists()

    form_class = SpaceUploadFileForm
    template_name = 'pages/spaces/space-file-view.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['space'] = DocumentSpace.objects.get(pk=self.kwargs['space_id'])
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        uploaded_file: "UploadedFile" = form.files['document']
        drive_service = DriveService(user=form.space.owner)
        sheets_service = SheetsService(user=form.space.owner)
        try:
            drive_service.ensure_folder_structure()
            data_file_response = drive_service.upload_spreadsheet_to_drive(uploaded_file.file, uploaded_file.name,
                                                                           uploaded_file.content_type)
            response_file_response = drive_service.create_response_spreadsheet_in_drive(data_file_response.get('name'))

            data_file = form.space.files.create(file_name=uploaded_file.name,
                                                web_content_link=data_file_response.get('webViewLink'),
                                                file_id=data_file_response.get('id'))
            ResponseFile.objects.create(data_file=data_file, web_content_link=response_file_response.get('webViewLink'),
                                        file_id=response_file_response.get('id'))

            sheets_service.set_response_file_header(response_file_response.get('id'))

            messages.success(self.request, 'The file has been successfully uploaded')
        except service_exceptions.BaseGoogleServiceException as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        query_param = urlencode({
            "tab": "space-files"
        })
        return HttpResponseRedirect(
            f"{reverse('spaces_overview', kwargs={'space_id': self.kwargs['space_id']})}?{query_param}")

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return redirect('spaces_overview', space_id=self.kwargs['space_id'])


class SpaceFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    def test_func(self):
        return self.request.user.is_space_owner and \
            DataFile.objects.filter(pk=self.kwargs['file_id'], space__owner=self.request.user).exists()

    form_class = SpaceDeleteFileForm
    template_name = 'pages/spaces/space-file-delete.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['expected_file_name'] = DataFile.objects.get(pk=self.kwargs['file_id']).file_name
        return kwargs

    def form_valid(self, form):
        drive_service = DriveService(user=self.request.user)
        try:
            data_file = DataFile.objects.get(pk=self.kwargs['file_id'])
            drive_service.ensure_folder_structure()
            drive_service.delete_document(file_id=data_file.file_id)
            drive_service.delete_document(file_id=data_file.response_file.file_id)
            data_file.delete()
            messages.success(self.request, 'The file has been successfully deleted')
        except service_exceptions.BaseGoogleServiceException as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        query_param = urlencode({
            "tab": "space-files"
        })
        return http.HttpResponseRedirect(
            f"{reverse('spaces_overview', kwargs={'space_id': self.kwargs['space_id']})}?{query_param}")

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)
