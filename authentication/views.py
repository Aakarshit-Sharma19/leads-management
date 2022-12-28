from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from authentication.forms import CustomPasswordChangeForm


class ProfileView(TemplateView, LoginRequiredMixin):
    template_name = 'account/users-profile.html'

    def get_context_data(self, **kwargs):
        kwargs = super(ProfileView, self).get_context_data(**kwargs)
        kwargs['password_change_form'] = CustomPasswordChangeForm(self.request.user)
        return kwargs


@require_http_methods(['POST'])
@sensitive_post_parameters()
def profile_change_password_url(request: HttpRequest):
    form = CustomPasswordChangeForm(request.user, request.POST)
    if form.is_valid():
        form.save()
        update_session_auth_hash(request, form.user)
        messages.success(request, 'The password has been changed successfully')
    else:
        for message in form.non_field_errors():
            messages.error(request, message)
        for message in form.errors.values():
            messages.error(request, message)
    return redirect('accounts_users_profile')
