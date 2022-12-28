from allauth.account.adapter import get_adapter
from allauth.account.forms import LoginForm as AllAuthLoginForm
from allauth.utils import set_form_field_order
from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from authentication.models import PortalUser
from authentication.utils import AuthenticationMethod, update_retries_count


class LoginForm(AllAuthLoginForm):
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "class": "form-control"}),
    )
    remember = forms.BooleanField(label=_("Remember Me"), required=False)

    error_messages = {
        "account_inactive": _("This account is currently inactive."),
        "email_password_mismatch": _(
            "The e-mail address and/or password you specified are not correct. "
            "The user will be locked out in case of 3 wrong attempts."
        ),
        "username_password_mismatch": _(
            "The username and/or password you specified are not correct. "
            "The user will be locked out in case of 3 wrong attempts."
        ),
        "locked_out_user": _(
            "The user is locked out. Please contact the admin to unlock the user."
        ),
    }

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        login_widget = forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("E-mail address"),
                "autocomplete": "email",
                "class": "form-control"
            }
        )
        login_field = forms.EmailField(label=_("E-mail"), widget=login_widget)
        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])

    def clean(self):
        super(LoginForm, self).clean()
        if self._errors:
            return
        credentials = self.user_credentials()
        user = get_adapter(self.request).authenticate(self.request, **credentials)
        if user:
            self.check_logged_out_user()
            if user.failed_attempts > 0:
                user.failed_attempts = 0
                user.save()
            self.user = user
        else:
            auth_method = settings.ACCOUNT_AUTHENTICATION_METHOD
            if auth_method == AuthenticationMethod.USERNAME_EMAIL:
                login = self.cleaned_data["login"]
                if self._is_login_email(login):
                    auth_method = AuthenticationMethod.EMAIL
                    update_retries_count(login)
                else:
                    auth_method = AuthenticationMethod.USERNAME
            raise forms.ValidationError(
                self.error_messages["%s_password_mismatch" % auth_method]
            )
        return self.cleaned_data

    def check_logged_out_user(self):
        user = self.user
        if user.failed_attempts > 3:
            raise ValidationError(
                self.error_messages['locked_out_user']
            )

class CustomUserCreationForm(UserCreationForm):
    password1 = None
    password2 = None

    def _post_clean(self):
        super(CustomUserCreationForm, self)._post_clean()

    def save(self, commit=True):
        user = super(forms.ModelForm, self).save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user

    class Meta:
        model = PortalUser
        fields = ('email',)
        field_classes = {}


class CustomPasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
    )

    error_messages = {
        'password_mismatch': 'Please enter enter the new password, both in the password and confirm password field',
        'wrong_old_password': 'Please enter your correct password in the old password field',
        'same_password': 'Please enter a new password which should not be same as the old one'
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        if self.user.has_usable_password():
            self.fields['old_password'] = forms.CharField(
                label=_("Old password"),
                widget=forms.PasswordInput(attrs={"autocomplete": "old-password", "class": "form-control"}),
                strip=False,
            )

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if old_password and not self.user.check_password(old_password):
            raise ValidationError(
                self.error_messages['wrong_old_password']
            )
        return old_password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code="password_mismatch",
            )
        if self.user.check_password(password2):
            raise ValidationError(
                self.error_messages['same_password'],
                code="same_password",
            )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data['new_password2']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
