from allauth.socialaccount.models import SocialToken, SocialApp
from django.core.cache import cache
from google.oauth2.credentials import Credentials

from services import exceptions as service_exceptions


def format_user_id_creds_key(user_id):
    return f'google_credentials_for_{user_id}'


def _build_credentials(token: str, refresh: str, client_id: str, client_secret: str,
                       token_uri: str = 'https://oauth2.googleapis.com/token'):
    return Credentials(
        token=token,
        refresh_token=refresh,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret
    )


def get_user_credentials(user, override=False):
    creds = cache.get(format_user_id_creds_key(user.id))
    if override or not creds:
        try:
            token = SocialToken.objects.get(account__user=user)
        except SocialToken.DoesNotExist as e:
            raise service_exceptions.SocialTokenNotFoundException(
                message=f'SocialToken for user {user} does not exist') from e
        provider_app: SocialApp = SocialApp.objects.last()
        creds = {
            "token": token.token,
            "refresh": token.token_secret,
            "client_id": provider_app.client_id,
            "client_secret": provider_app.secret
        }
        cache.set(format_user_id_creds_key(user.id), creds, 60 * 15)
    return _build_credentials(**creds)
