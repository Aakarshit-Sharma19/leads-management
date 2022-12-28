import typing
from io import BytesIO
from logging import getLogger

from django.core.cache import cache
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from httplib2 import HttpLib2Error

from services import exceptions as service_exceptions
from services.google.oauth2 import get_user_credentials

logger = getLogger('drive')

if typing.TYPE_CHECKING:
    from googleapiclient._apis.drive.v3.resources import DriveResource
    from googleapiclient._apis.drive.v3.schemas import FileList, File


def format_user_id_dir_struct_key(user_id):
    return f'drive_structure_for_{user_id}'


class DriveService:
    def __init__(self, user):
        self._user = user
        self._service: "DriveResource" = build('drive', 'v3', credentials=get_user_credentials(self._user))
        self.dir_structure = {
            'id': '',
            'name': 'leads_management',
            'data_folder': {
                'id': '',
                'name': 'data'
            },
            'responses_folder': {
                'id': '',
                'name': 'responses'
            }
        }

    def _ensure_folder_exists(self, folder_name, parent_id=None):
        q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
        try:
            folder: "FileList" = self._service.files().list(
                pageSize=1,
                q=q
            ).execute()
        except HttpError as e:
            if e.resp.status == 401:
                raise service_exceptions.GoogleAPIHttpError(
                    message='Google credentials have expired.'
                            ' The owner of the space should be notified to re-login to the portal with Google.') from e
            elif e.resp.status == 403:
                raise service_exceptions.GoogleAPIHttpError(
                    message='No valid permissions to access the user\'s space at Google.'
                            ' The owner of the space should be notified to re-login to the portal with Google'
                            ' by checking all the checkboxes of Google Permissions') from e
            raise service_exceptions.GoogleAPIHttpError(message='Invalid response from google API while communicating.'
                                                                ' Please notify portal admin') from e
        except HttpLib2Error as e:
            raise service_exceptions.GoogleAPIHttpError(
                message='The server could not communicate with the google API. '
                        'Retry after some time or contact portal admin') from e
        if len(folder.get('files', [])) < 1:
            raise service_exceptions.MissingFolderStructure(message=f'The folder {folder_name} in drive does not exist')
        return folder

    def ensure_folder_structure(self):
        dir_structure = cache.get(format_user_id_dir_struct_key(self._user.id))
        if dir_structure:
            self.dir_structure = dir_structure
            return self.dir_structure

        doc_folder = self._ensure_folder_exists(self.dir_structure['name'])
        self.dir_structure['id'] = doc_folder.get('files')[0]['id']

        data_folder = self._ensure_folder_exists(self.dir_structure['data_folder']['name'],
                                                 parent_id=self.dir_structure['id'])
        self.dir_structure['data_folder']['id'] = data_folder.get('files')[0]['id']

        responses_folder = self._ensure_folder_exists(self.dir_structure['responses_folder']['name'],
                                                      parent_id=self.dir_structure['id'])
        self.dir_structure['responses_folder']['id'] = responses_folder.get('files')[0]['id']

        cache.set(format_user_id_dir_struct_key(self._user.id), self.dir_structure, 60 * 60)
        return self.dir_structure

    def create_folder_structure(self):
        try:
            if self.dir_structure['id'] == '':
                root_folder: "File" = self._service.files().create(body={
                    'name': self.dir_structure['name'],
                    'mimeType': 'application/vnd.google-apps.folder'
                }).execute()
                self.dir_structure['id'] = root_folder['id']
            if self.dir_structure['data_folder']['id'] == '':
                data_folder_metadata: "File" = {
                    'name': self.dir_structure['data_folder']['name'],
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [self.dir_structure['id']]
                }
                data_folder = self._service.files().create(body=data_folder_metadata).execute()
                self.dir_structure['data_folder']['id'] = data_folder['id']
            if self.dir_structure['responses_folder']['id'] == '':
                responses_folder_metadata: "File" = {
                    'name': self.dir_structure['responses_folder']['name'],
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [self.dir_structure['id']]
                }
                response_folder = self._service.files().create(body=responses_folder_metadata).execute()
                self.dir_structure['responses_folder']['id'] = response_folder['id']
        except HttpError as e:
            if e.resp.status == 401:
                raise service_exceptions.GoogleAPIHttpError(
                    message='Google credentials have expired.'
                            ' The owner of the space should be notified to re-login to the portal with Google.') from e
            elif e.resp.status == 403:
                raise service_exceptions.GoogleAPIHttpError(
                    message='No valid permissions to access the user\'s space at Google.'
                            ' The owner of the space should be notified to re-login to the portal with Google'
                            ' by checking all the checkboxes of Google Permissions') from e
            raise service_exceptions.GoogleAPIHttpError(
                message='Invalid response from google API while communicating.'
                        ' Please notify portal admin') from e
        except HttpLib2Error as e:
            raise service_exceptions.GoogleAPIHttpError(
                message='The server could not communicate with the google API. '
                        'Retry after some time or contact portal admin') from e
        except Exception as e:
            raise service_exceptions.StructureCreationFailed(message='An error occurred while creating '
                                                                     f'file structure in the Google Drive'
                                                                     f' for user {self._user.email}') from e

    def delete_folder_structure(self):
        try:
            self.ensure_folder_structure()
        except service_exceptions.MissingFolderStructure:
            logger.warning(f'Folder structure does not exist for user {self._user.email}. Attempting delete',
                           exc_info=True)
        try:
            if len(self.dir_structure['id']) == 33:
                self._service.files().delete(fileId=self.dir_structure['id']).execute()
                return True
            else:
                return False
        except HttpError as e:
            if e.resp.status == 401:
                raise service_exceptions.GoogleAPIHttpError(
                    message='Google credentials have expired.'
                            ' The owner of the space should be notified to re-login to the portal with Google.') from e
            elif e.resp.status == 403:
                raise service_exceptions.GoogleAPIHttpError(
                    message='No valid permissions to access the user\'s space at Google.'
                            ' The owner of the space should be notified to re-login to the portal with Google'
                            ' by checking all the checkboxes of Google Permissions') from e
            raise service_exceptions.GoogleAPIHttpError(
                message='Invalid response from google API while communicating.'
                        ' Please notify portal admin') from e
        except HttpLib2Error as e:
            raise service_exceptions.GoogleAPIHttpError(
                message='The server could not communicate with the google API. '
                        'Retry after some time or contact portal admin') from e
        except Exception as e:
            raise service_exceptions.StructureDeletionFailed(message=f'An error occurred while deleting file structure'
                                                                     f' in the Google Drive'
                                                                     f' for user {self._user.email}') from e

    def upload_spreadsheet_to_data(self, file: BytesIO, name: str, content_type: str):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [self.dir_structure['data_folder']['id']]
        }
        media = MediaIoBaseUpload(file, mimetype=content_type, chunksize=1024 * 1024)
        created_file = self._service.files().create(body=file_metadata, media_body=media).execute()
        return created_file.get('id')
