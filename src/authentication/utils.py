from authentication.models import PortalUser


class AuthenticationMethod:
    USERNAME = "username"
    EMAIL = "email"
    USERNAME_EMAIL = "username_email"


def update_retries_count(email):
    try:
        user = PortalUser.objects.get(email=email)
    except PortalUser.DoesNotExist:
        user = None
    if user:
        user.failed_attempts += 1
        user.save()
