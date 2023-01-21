import typing
from logging import getLogger

from django.core.cache import cache
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from services import exceptions as service_exceptions
from services.google.common import execute_query
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
        folder: "FileList" = execute_query(self._service.files().list(
            pageSize=1,
            q=q
        ))
        if len(folder.get('files', [])) < 1:
            raise service_exceptions.MissingFolderStructureException(
                message=f'The folder {folder_name} in drive does not exist.'
                        f' Please ensure this folder is not manually deleted or moved to trash')
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
                root_folder: "File" = execute_query(self._service.files().create(body={
                    'name': self.dir_structure['name'],
                    'mimeType': 'application/vnd.google-apps.folder'
                }))
                self.dir_structure['id'] = root_folder['id']

            if self.dir_structure['data_folder']['id'] == '':
                data_folder_metadata = {
                    'name': self.dir_structure['data_folder']['name'],
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [self.dir_structure['id']]
                }
                data_folder: "File" = execute_query(
                    self._service.files().create(body=data_folder_metadata))
                self.dir_structure['data_folder']['id'] = data_folder['id']

            if self.dir_structure['responses_folder']['id'] == '':
                responses_folder_metadata: "File" = {
                    'name': self.dir_structure['responses_folder']['name'],
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [self.dir_structure['id']]
                }
                response_folder: "File" = execute_query(
                    self._service.files().create(body=responses_folder_metadata))
                self.dir_structure['responses_folder']['id'] = response_folder['id']

        except service_exceptions.BaseGoogleServiceException as e:
            raise e
        except Exception as e:
            raise service_exceptions.StructureCreationFailedException(message='An error occurred while creating '
                                                                              f'file structure in the Google Drive'
                                                                              f' for user {self._user.email}') from e

    def delete_folder_structure(self):
        try:
            self.ensure_folder_structure()
        except service_exceptions.MissingFolderStructureException:
            logger.warning(f'Folder structure does not exist for user {self._user.email}. Attempting delete',
                           exc_info=True)
        try:
            if len(self.dir_structure['id']) == 33:
                execute_query(self._service.files().delete(fileId=self.dir_structure['id']))
                return True
            else:
                return False
        except Exception as e:
            raise service_exceptions.StructureDeletionFailedException(
                message=f'An error occurred while deleting file structure'
                        f' in the Google Drive'
                        f' for user {self._user.email}') from e

    def delete_document(self, file_id: str):
        try:
            self.ensure_folder_structure()
            execute_query(self._service.files().update(fileId=file_id, body={
                'trashed': True
            }), raise_404=True)
        except HttpError:
            raise service_exceptions.FileToDeleteNotFoundException(
                message="The file you are trying to delete is not deleted. Is this file present.")

    def upload_spreadsheet_to_drive(self, file: "typing.IO", name: str, content_type: str) -> "File":
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [self.dir_structure['data_folder']['id']]
        }
        media = MediaIoBaseUpload(file, mimetype=content_type, chunksize=1024 * 1024)
        return execute_query(
            self._service.files().create(body=file_metadata, media_body=media, fields=','.join([
                'id', 'name', 'webViewLink'
            ])))

    def create_response_spreadsheet_in_drive(self, name: str) -> "File":
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [self.dir_structure['responses_folder']['id']]
        }
        return execute_query(self._service.files().create(body=file_metadata, fields=','.join([
            'id', 'name', 'webViewLink'
        ])))
