from logging import getLogger

from allauth.socialaccount.models import SocialAccount
from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView, DetailView, ListView

from document_spaces import forms
from leads_data.models import DocumentSpace
from services import exceptions as service_exceptions
from services.google.drive import DriveService

logger = getLogger('portal')


class SpaceInitializeView(LoginRequiredMixin, FormView):
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


class SpaceOverviewView(LoginRequiredMixin, DetailView):
    model = DocumentSpace
    context_object_name = 'space'
    template_name = 'pages/spaces/overview.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_space_owner:
            return queryset.filter(owner=self.request.user)
        return queryset.filter(
            Q(managers=self.request.user) | Q(writers=self.request.user))

    def get(self, request, *args, **kwargs):
        try:
            response = super().get(request, *args, **kwargs)
            if request.user.is_space_owner:
                try:
                    drive_service = DriveService(user=request.user)
                    drive_service.ensure_folder_structure()
                except service_exceptions.GoogleAPIHttpError as e:
                    logger.exception(f'ErrorId: {e.error_id}: {e.message}')
                    messages.error(request, f'{e.message} | ErrorId: {e.error_id}')
            return response
        except http.Http404 as e:
            if request.user.is_space_owner:
                messages.info(request,
                              'You currently do not have a space created for you. Please initialize your own space')
            else:
                raise e

class SpaceListView(LoginRequiredMixin, ListView):
    model = DocumentSpace
    template_name = 'pages/spaces/list-spaces.html'
    context_object_name = 'space_list'
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            Q(managers=self.request.user) | Q(writers=self.request.user))


class SpaceWriterView(LoginRequiredMixin, TemplateView):
    pass


class SpaceHomeView(LoginRequiredMixin, TemplateView):
    pass


class SpaceManagerView(LoginRequiredMixin, TemplateView):
    pass
