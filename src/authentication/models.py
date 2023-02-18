from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.management.utils import get_random_string
from django.db import models
from django.utils.translation import gettext_lazy as _

from auditlog.registry import auditlog

def get_random_string_60():
    return get_random_string(60)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a PortalUser with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class PortalUser(AbstractUser):
    username = None
    # Identifiable Information
    first_name = models.CharField(
        'First Name', unique=False, blank=False, max_length=50)
    last_name = models.CharField(
        'Last Name', unique=False, blank=False, max_length=20)
    email = models.EmailField('Email Address', unique=True, blank=False)

    is_space_owner = models.BooleanField('Is Space Owner', default=False, blank=False,
                                         help_text=_("Designates whether the user will have their own space or not"),
                                         )
    failed_attempts = models.IntegerField(default=0)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

auditlog.register(PortalUser)