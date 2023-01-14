from logging import getLogger
from urllib.parse import urlencode

from allauth.socialaccount.models import SocialAccount
from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView, DetailView, ListView

from document_spaces import forms
from document_spaces.forms import SpaceUploadFileForm, SpaceDeleteFileForm
from leads_data.models import DocumentSpace, ResponseFile, DataFile
from services import exceptions as service_exceptions
from services.google.drive import DriveService

logger = getLogger('portal')


class SpaceInitializeView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = forms.SpaceCreationConfirmationForm
    template_name = 'pages/spaces/initialize.html'

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if not SocialAccount.objects.filter(user=self.request.user).exists():
            messages.error(self.request,
                           'The space cannot be initialized.'
                           ' The owner should login with google to enable document spaces')
            del kwargs['form']
        return kwargs

    def form_valid(self, form):
        drive_service = DriveService(user=self.request.user)
        try:
            drive_service.ensure_folder_structure()
        except service_exceptions.MissingFolderStructure:
            try:
                drive_service.create_folder_structure()
            except service_exceptions.StructureCreationFailed as e:
                logger.exception(f'ErrorId: {e.error_id}: {e.message}')
                messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        except service_exceptions.GoogleAPIHttpError as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        space, _ = DocumentSpace.objects.get_or_create(owner=self.request.user)
        messages.success(self.request, 'The space has been initialized')
        return redirect('spaces_overview', pk=space.id)

    def test_func(self):
        return self.request.user.is_space_owner


class SpaceOverviewView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = DocumentSpace
    context_object_name = 'space'
    template_name = 'pages/spaces/overview.html'

    def test_func(self):
        if self.request.user.is_space_owner:
            return DocumentSpace.objects.filter(id=self.kwargs[self.pk_url_kwarg], owner=self.request.user).exists()
        else:
            return DocumentSpace.objects.filter(
                Q(managers=self.request.user) | Q(writers=self.request.user)).exists()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if self.request.user.is_space_owner or self.object.managers.filter(pk=self.request.user.pk).exists():
            kwargs['fileUploadForm'] = forms.SpaceUploadFileForm(user=self.request.user, space=self.object)
        return kwargs

    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            if request.user.is_space_owner:
                try:
                    drive_service = DriveService(user=request.user)
                    drive_service.ensure_folder_structure()
                except service_exceptions.BaseGoogleServiceException as e:
                    logger.exception(f'ErrorId: {e.error_id}: {e.message}')
                    messages.error(request, f'{e.message} | ErrorId: {e.error_id}')
            return response
        except http.Http404:
            if request.user.is_space_owner:
                messages.warning(request,
                                 'You currently do not have a space created for you. Please initialize your own space')
            else:
                messages.error(request,
                               'This space does not exist or you are not a part of it.')
            return redirect('spaces_initialize')


class SpaceListView(LoginRequiredMixin, ListView):
    model = DocumentSpace
    template_name = 'pages/spaces/list-spaces.html'
    context_object_name = 'space_list'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(managers=self.request.user) | Q(writers=self.request.user))


class SpaceFileUpload(LoginRequiredMixin, UserPassesTestMixin, FormView):
    def test_func(self):
        if self.request.user.is_space_owner:
            return DocumentSpace.objects.filter(pk=self.kwargs['pk'], owner=self.request.user).exists()
        else:
            return DocumentSpace.objects.filter(pk=self.kwargs['pk'], managers=self.request.user).exists()

    form_class = SpaceUploadFileForm
    template_name = 'pages/spaces/space-file-view.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['space'] = DocumentSpace.objects.get(pk=self.kwargs['pk'])
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        uploaded_file: "UploadedFile" = form.files['document']
        drive_service = DriveService(user=form.space.owner)
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

            messages.success(self.request, 'The file has been successfully uploaded')
        except service_exceptions.BaseGoogleServiceException as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        query_param = urlencode({
            "tab": "space-files"
        })
        return HttpResponseRedirect(f"{reverse('spaces_overview', kwargs={'pk':self.kwargs['pk']})}?{query_param}")

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return redirect('spaces_overview', pk=self.kwargs['pk'])

class SpaceFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    def test_func(self):
        return self.request.user.is_space_owner and \
            DataFile.objects.filter(pk=self.kwargs['pk'], space__owner=self.request.user).exists()

    form_class = SpaceDeleteFileForm
    template_name = 'pages/spaces/space-file-delete.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['expected_file_name'] = DataFile.objects.get(pk=self.kwargs['pk']).file_name
        return kwargs

    def form_valid(self, form):
        drive_service = DriveService(user=self.request.user)
        try:
            data_file = DataFile.objects.get(pk=self.kwargs['pk'])
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
        return HttpResponseRedirect(f"{reverse('spaces_overview', kwargs={'pk':self.kwargs['space_pk']})}?{query_param}")

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)
