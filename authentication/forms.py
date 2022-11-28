from django import forms
from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm, UsernameField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from authentication.models import PortalUser


class AuthenticationForm(DjangoAuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True, "class": "form-control"}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "class": "form-control"}),
    )
    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive. The user will be locked out in case of 3 wrong attempts."
        ),
        "locked_out_user": _(
            "The user is locked out. Please contact the admin to unlock the user."
        ),
        "inactive": _("This account is inactive."),
    }

    def get_invalid_login_error(self):
        user = PortalUser.objects.get(email=self.cleaned_data.get("username"))
        if user:
            user.failed_attempts += 1
            user.save()
        return ValidationError(
            self.error_messages["invalid_login"],
            code="invalid_login",
            params={"username": self.username_field.verbose_name},
        )

    def confirm_login_allowed(self, user: PortalUser):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages["inactive"],
                code="inactive",
            )

        if not user.is_superuser and user.failed_attempts > 2:
            raise ValidationError(
                self.error_messages["locked_out_user"],
                code="locked_out_user"
            )
