import typing
from logging import getLogger

from googleapiclient.discovery import build
from pydantic import ValidationError

from services import exceptions as service_exceptions
from services.google.common import execute_query
from services.google.models import StudentInfo, StudentResponse
from services.google.oauth2 import get_user_credentials

logger = getLogger('service')

if typing.TYPE_CHECKING:
    from googleapiclient._apis.sheets.v4.resources import SheetsResource
    from googleapiclient._apis.sheets.v4.schemas import ValueRange


class SheetsService:
    def __init__(self, user):
        self._user = user
        self._service: "SheetsResource" = build('sheets', 'v4', credentials=get_user_credentials(self._user))

    def read_student_info_from_row(self, spreadsheet_id: str, row_index: int) -> 'StudentInfo':
        if row_index == 0:
            row_index = row_index + 1
        row_range = f"A{row_index}:D{row_index}"
        result: "ValueRange" = execute_query(
            self._service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=row_range))
        rows = result.get('values')
        row = rows[0]
        if len(row) == 0:
            raise service_exceptions.EmptyRowException(message='Row is empty')
        if len(row) != 4:
            raise service_exceptions.InvalidDataException(
                message=f'The data present in the file is invalid.'
                        f' Please notify {self._user.get_full_name()} to check row number: {row_index}')
        try:
            return StudentInfo.from_tuple(row)
        except ValidationError as e:
            raise service_exceptions.InvalidDataException(message=f'The data present in the file is invalid.'
                                                                  f' Error: {e.errors()[0]["msg"]}.'
                                                                  f' Please notify {self._user.get_full_name()} to check'
                                                                  f' row number: {row_index}') from e

    def get_next_populated_row(self, spreadsheet_id: str, start_index: int, end_index: int) -> \
            'typing.Tuple[int, StudentInfo]':
        if start_index == 0:
            start_index = start_index + 1
        row_range = f"A{start_index}:D{end_index}"
        result: "ValueRange" = execute_query(
            self._service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=row_range))
        rows = result.get('values')
        for i, row in enumerate(rows):
            if len(row) > 0:
                if len(row) != 4:
                    raise service_exceptions.InvalidDataException(
                        message=f'The data present in the file is invalid.'
                                f' Please notify {self._user.get_full_name()} to check row number: {start_index + i}')
                try:
                    return start_index + i, StudentInfo.from_tuple(row)
                except ValidationError as e:
                    raise service_exceptions.InvalidDataException(message=f'The data present in the file is invalid.'
                                                                          f' Error: {e.errors()[0]["msg"]}.'
                                                                          f' Please notify {self._user.get_full_name()}'
                                                                          f' to check row number: {start_index + i}') \
                        from e

        raise service_exceptions.EndOfFileException()

    def set_response_file_header(self, spreadsheet_id):
        try:
            execute_query(self._service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range='A1:F1',
                                                                       valueInputOption='USER_ENTERED',
                                                                       body={
                                                                           'majorDimension': 'ROWS',
                                                                           'values': [[
                                                                               'S.No',
                                                                               'Name',
                                                                               'Phone Number',
                                                                               'Education',
                                                                               'Latest Response',
                                                                               'Current Status'
                                                                           ]]
                                                                       }))
        except ValidationError as e:
            raise service_exceptions.InvalidDataException(
                message='The data to be input from the data is invalid') from e

    def set_row_from_student_response(self, spreadsheet_id: str, row_index: int, student_response: StudentResponse):
        row_index += 1
        row_range = f"A{row_index}:F{row_index}"
        try:
            execute_query(self._service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=row_range,
                                                                       valueInputOption='USER_ENTERED',
                                                                       body={
                                                                           'majorDimension': 'ROWS',
                                                                           'values': [student_response.to_tuple()]
                                                                       }))
        except ValidationError as e:
            raise service_exceptions.InvalidDataException(
                message='The data to be input from the data is invalid') from e
