import uuid


class BaseGoogleServiceException(Exception):
    def __init__(self, message):
        self.error_id = uuid.uuid4()
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}: (errorId: f{self.error_id}) {self.message}'


class GoogleAPIHttpException(BaseGoogleServiceException):
    pass


# Drive API
class MissingFolderStructureException(BaseGoogleServiceException):
    pass


class StructureCreationFailedException(BaseGoogleServiceException):
    pass


class StructureDeletionFailedException(BaseGoogleServiceException):
    pass


class DocumentDeletionFailedException(BaseGoogleServiceException):
    pass


class SocialTokenNotFoundException(BaseGoogleServiceException):
    pass


class FileToDeleteNotFoundException(BaseGoogleServiceException):
    pass


# Sheets API
class InvalidDataException(BaseGoogleServiceException):
    pass


class EmptyRowException(BaseGoogleServiceException):
    pass


class EndOfFileException(Exception):
    pass
