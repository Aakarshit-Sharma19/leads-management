from logging import getLogger
from typing import Optional
from urllib.parse import urlencode

from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from document_spaces.forms import SpaceResponseSubmitForm, ResolveEntryForm, SpaceResponseUpdateForm
from exceptions import NonDefaultResponse
from leads_data.models import DocumentSpace, DataFile, Student
from services import exceptions as service_exceptions
from services.google.models import StudentResponse
from services.google.sheets import SheetsService

logger = getLogger('portal')


class SpaceResponseSubmitView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = SpaceResponseSubmitForm
    template_name = 'pages/spaces/response-submit.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.space: 'Optional[DocumentSpace]' = None
        self.data_file: 'Optional[DataFile]' = None

    def test_func(self):
        try:
            if self.request.user.is_space_owner:
                self.space = DocumentSpace.objects.get(id=self.kwargs['space_id'], owner=self.request.user)
            else:
                self.space = DocumentSpace.objects.get(Q(id=self.kwargs['space_id']) &
                                                       (Q(managers=self.request.user) | Q(writers=self.request.user)))
            return True
        except DocumentSpace.DoesNotExist:
            return False

    def get(self, request, *args, **kwargs):
        try:
            data = DataFile.objects.get(id=self.kwargs['file_id'], space_id=self.kwargs['space_id'])
            self.data_file = data
            return super().get(request, *args, **kwargs)
        except DataFile.DoesNotExist:
            raise http.Http404()

    def post(self, request, *args, **kwargs):
        try:
            data = DataFile.objects.get(id=self.kwargs['file_id'], space_id=self.kwargs['space_id'])
            self.data_file = data
            return super().post(request, *args, **kwargs)
        except DataFile.DoesNotExist:
            raise http.Http404()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update((('data_file', self.data_file), ('space', self.space)))
        sheets_service = SheetsService(user=self.space.owner)
        student_info = None
        try:
            student_info = sheets_service.read_student_info_from_row(self.data_file.file_id, self.data_file.current_row)
        except service_exceptions.EmptyRowException:
            try:
                row, student_info = sheets_service.get_next_populated_row(self.data_file.file_id,
                                                                          self.data_file.current_row,
                                                                          self.data_file.current_row + 100)
            except service_exceptions.EndOfFileException:
                messages.info(self.request,
                              f"No more entries left in the file. If you think that is a mistake,"
                              f" please contact {self.space.owner} and"
                              f" provide row number as {self.data_file.current_row}")
                query_param = urlencode({"tab": "space-files"})
                self.data_file.completed = True
                self.data_file.save()
                raise NonDefaultResponse(HttpResponseRedirect(
                    f"{reverse('spaces_overview', kwargs={'space_id': self.kwargs['space_id']})}?{query_param}"))
            self.data_file.current_row = row
            self.data_file.save()
        except service_exceptions.BaseGoogleServiceException as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        if student_info:
            kwargs.update({
                'valid': True,
                'name': student_info.name,
                'phone_number': student_info.phone_number,
                'education': student_info.education,
            })
        return kwargs

    def form_valid(self, form):
        form_response = form.cleaned_data['response']
        sheets_service = SheetsService(user=self.space.owner)

        try:
            response_file_id = self.data_file.response_file.file_id
            if self.data_file.completed:
                return http.HttpResponseBadRequest()
            student_info = sheets_service.read_student_info_from_row(self.data_file.file_id, self.data_file.current_row)
            individual = self.data_file.approached_individuals.create(row_no=self.data_file.current_row,
                                                                      name=student_info.name,
                                                                      phone_number=student_info.phone_number,
                                                                      education=student_info.education,
                                                                      status=form.cleaned_data['status'])
            individual.responses.create(content=form_response)
            # sheets_service.set_response_file_header(spreadsheet_id=response_file_id)
            sheets_service.set_row_from_student_response(spreadsheet_id=response_file_id,
                                                         row_index=self.data_file.current_row,
                                                         student_response=StudentResponse(**student_info.dict(),
                                                                                          response=form_response,
                                                                                          status=form.cleaned_data['status']))
            self.data_file.current_row += 1
            self.data_file.save()
            messages.success(self.request, f'The entry for the person {student_info.name} has been saved. '
                                           f'You can check follow-up section'
                                           f' to add updates for the interaction with this person.')
        except service_exceptions.BaseGoogleServiceException as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        return redirect(self.request.path)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


class SpaceResponseUpdateView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = SpaceResponseUpdateForm
    template_name = "pages/spaces/response-update.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.space: 'Optional[DocumentSpace]' = None
        self.data_file: 'Optional[DataFile]' = None
        self.student: 'Optional[Student]' = None

    def test_func(self):
        try:
            if self.request.user.is_space_owner:
                self.space = DocumentSpace.objects.get(id=self.kwargs['space_id'], owner=self.request.user)
            else:
                self.space = DocumentSpace.objects.get(Q(id=self.kwargs['space_id']) &
                                                       (Q(managers=self.request.user) | Q(writers=self.request.user)))
            return True
        except DocumentSpace.DoesNotExist:
            return False

    def get(self, request, *args, **kwargs):
        try:
            self.data_file = DataFile.objects.get(id=self.kwargs['file_id'], space_id=self.kwargs['space_id'])
            self.student = self.data_file.approached_individuals.get(pk=self.kwargs['student_id'])
            return super().get(request, *args, **kwargs)
        except (DataFile.DoesNotExist, Student.DoesNotExist):
            raise http.Http404()

    def post(self, request, *args, **kwargs):
        try:
            self.data_file = DataFile.objects.get(id=self.kwargs['file_id'], space_id=self.kwargs['space_id'])
            self.student = self.data_file.approached_individuals.get(pk=self.kwargs['student_id'])
            return super().post(request, *args, **kwargs)
        except (DataFile.DoesNotExist, Student.DoesNotExist):
            raise http.Http404()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['student'] = self.student
        kwargs['data_file'] = self.data_file
        kwargs['space'] = self.space
        return kwargs

    def form_valid(self, form):
        sheets_service = SheetsService(user=self.space.owner)

        try:
            student_info = sheets_service.read_student_info_from_row(spreadsheet_id=self.data_file.file_id,
                                                                     row_index=self.student.row_no)
            sheets_service.set_row_from_student_response(
                spreadsheet_id=self.data_file.response_file.file_id, row_index=self.student.row_no,
                student_response=StudentResponse(**student_info.dict(), response=form.cleaned_data['response'],
                                                 status=form.cleaned_data['status']))
            self.student.status = form.cleaned_data['status']
            self.student.save()
            self.student.responses.create(content=form.cleaned_data['response'])
            messages.success(self.request, f'New entry added for person {student_info.name}.')
        except service_exceptions.BaseGoogleServiceException as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        return redirect(self.request.path)


class SpaceResolveResponseView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "pages/spaces/space-follow-up-resolve-view.html"
    form_class = ResolveEntryForm

    def test_func(self):
        try:
            if self.request.user.is_space_owner:
                self.space = DocumentSpace.objects.get(id=self.kwargs['space_id'], owner=self.request.user)
            else:
                self.space = DocumentSpace.objects.get(Q(id=self.kwargs['space_id']) &
                                                       (Q(managers=self.request.user) | Q(writers=self.request.user)))
            return True
        except DocumentSpace.DoesNotExist:
            return False

    def form_valid(self, form):
        try:
            student = Student.objects.get(id=self.kwargs['student_id'])
        except Student.DoesNotExist:
            return http.HttpResponseNotFound()

        if not student.is_resolvable:
            return http.HttpResponseBadRequest()
        student.resolved = True
        student.save()

        messages.success(self.request,
                         f"The student {student.name} has been resolved and finalized, no more responses will be "
                         f"allowed.")

        return redirect("spaces_follow_up", space_id=self.kwargs['space_id'], file_id=self.kwargs['file_id'])

    def form_invalid(self, form):
        return redirect("spaces_follow_up", space_id=self.kwargs['space_id'], file_id=self.kwargs['file_id'])
