from logging import getLogger
from urllib.parse import urlencode

from django import http
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from document_spaces import forms
from leads_data.models import DocumentSpace

logger = getLogger('portal')


def create_user_as_manager(request, space_id):
    if not request.user.is_authenticated or not request.user.is_space_owner:
        return http.HttpResponseForbidden()
    try:
        space = DocumentSpace.objects.get(id=space_id, owner=request.user)
        if request.POST:
            form = forms.CreateUserAsManagerForm(request.POST, space=space)
            if form.is_valid():
                form.save()
                messages.success(request, "New User has been created and been added to the space as a manager")
            else:
                messages.error(request, "Form is Invalid")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
            query_param = urlencode({
                "tab": "space-managers"
            })
            return HttpResponseRedirect(
                f"{reverse('spaces_overview', kwargs={'space_id': space_id})}?{query_param}")
        else:
            return http.HttpResponseNotAllowed(permitted_methods=['POST'])
    except DocumentSpace.DoesNotExist:
        return http.HttpResponseForbidden()


def create_user_as_writer(request, space_id):
    if not request.user.is_authenticated or not request.user.is_space_owner:
        return http.HttpResponseForbidden()
    try:
        space = DocumentSpace.objects.get(id=space_id, owner=request.user)
        if request.POST:
            form = forms.CreateUserAsWriterForm(request.POST, space=space)
            if form.is_valid():
                form.save()
                messages.success(request, "New User has been created and been added to the space as a writer")
            else:
                messages.error(request, "Form is Invalid")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
            query_param = urlencode({
                "tab": "space-writers"
            })
            return HttpResponseRedirect(
                f"{reverse('spaces_overview', kwargs={'space_id': space_id})}?{query_param}")
        else:
            return http.HttpResponseNotAllowed(permitted_methods=['POST'])
    except DocumentSpace.DoesNotExist:
        return http.HttpResponseForbidden()
