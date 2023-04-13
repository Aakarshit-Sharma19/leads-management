import typing

from google.auth.exceptions import RefreshError
from googleapiclient.errors import HttpError
from httplib2 import HttpLib2Error

from services import exceptions as service_exceptions

if typing.TYPE_CHECKING:
    from googleapiclient.http import HttpRequest

    APIRequest: typing.TypeAlias = HttpRequest


def execute_query(request: "HttpRequest", raise_404=False):
    try:
        return request.execute()
    except (HttpError, RefreshError) as e:
        if isinstance(e, RefreshError):
            raise service_exceptions.GoogleAPIHttpException(
                message='Google credentials have expired.'
                        ' The owner of the space should be notified to re-login to the portal with Google.'
                        'If the issue persists, contact the portal admin.') from e
        if e.resp.status == 404 and raise_404:
            raise e
        if e.resp.status == 401:
            raise service_exceptions.GoogleAPIHttpException(
                message='Google credentials have expired.'
                        ' The owner of the space should be notified to re-login to the portal with Google.') from e
        elif e.resp.status == 403:
            raise service_exceptions.GoogleAPIHttpException(
                message='No valid permissions to access the user\'s space at Google.'
                        ' The owner of the space should be notified to re-login to the portal with Google'
                        ' by checking all the checkboxes of Google Permissions') from e
        raise service_exceptions.GoogleAPIHttpException(message='Invalid response from google API while communicating.'
                                                                ' Please notify portal admin') from e
    except HttpLib2Error as e:
        raise service_exceptions.GoogleAPIHttpException(
            message='The server could not communicate with the google API. '
                    'Retry after some time or contact portal admin') from e
