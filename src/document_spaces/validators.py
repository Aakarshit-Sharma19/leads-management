from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from humanize import naturalsize

error_messages = {
    'wrong_file_type': 'The file should be an Excel file'
}


def validate_google_xlsx_type(file: UploadedFile):
    content_types = [
        'text/tab-separated-values',
        'application/vnd.ms-excel.sheet.macroenabled.12',
        'application/vnd.ms-excel',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/x-vnd.oasis.opendocument.spreadsheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        'application/vnd.ms-excel.template.macroenabled.12',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
    ]
    if file.content_type not in content_types:
        raise ValidationError(message=error_messages['wrong_file_type'], code='wrong_file_type')


def get_max_size_validator(limit: int):
    def size_validator(file: UploadedFile):
        if file.size > limit:
            raise ValidationError(
                f'File size should not exceed {naturalsize(limit, binary=True)}.')

    return size_validator
