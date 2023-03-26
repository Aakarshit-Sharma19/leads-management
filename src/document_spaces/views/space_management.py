from logging import getLogger

from allauth.socialaccount.models import SocialAccount
from django import http
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.views.generic import FormView, DetailView, ListView

from document_spaces import forms
from leads_data.models import DocumentSpace
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
        except service_exceptions.MissingFolderStructureException:
            try:
                drive_service.create_folder_structure()
            except service_exceptions.StructureCreationFailedException as e:
                logger.exception(f'ErrorId: {e.error_id}: {e.message}')
                messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        except service_exceptions.GoogleAPIHttpException as e:
            logger.exception(f'ErrorId: {e.error_id}: {e.message}')
            messages.error(self.request, f'{e.message} | ErrorId: {e.error_id}')
        space, _ = DocumentSpace.objects.get_or_create(owner=self.request.user)
        messages.success(self.request, 'The space has been initialized')
        return redirect('spaces_overview', space_id=space.id)

    def test_func(self):
        return self.request.user.is_space_owner


class SpaceOverviewView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = DocumentSpace
    context_object_name = 'space'
    template_name = 'pages/spaces/overview.html'
    pk_url_kwarg = 'space_id'

    def test_func(self):
        if self.request.user.is_space_owner:
            return DocumentSpace.objects.filter(id=self.kwargs[self.pk_url_kwarg], owner=self.request.user).exists()
        else:
            return DocumentSpace.objects.filter(Q(id=self.kwargs[self.pk_url_kwarg]) &
                                                (Q(managers=self.request.user) | Q(writers=self.request.user))).exists()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        if self.request.user.is_space_owner or self.object.managers.filter(pk=self.request.user.pk).exists():
            kwargs['fileUploadForm'] = forms.SpaceUploadFileForm(user=self.request.user, space=self.object)
            kwargs['can_manage'] = True
        if self.request.user.is_space_owner:
            kwargs.update({
                'createUserAsManagerForm': forms.CreateUserAsManagerForm(space=self.object),
                'createUserAsWriterForm': forms.CreateUserAsWriterForm(space=self.object)
            })
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
