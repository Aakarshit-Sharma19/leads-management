import uuid


class BaseGoogleServiceException(Exception):
    def __init__(self, message):
        self.error_id = uuid.uuid4()
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}: (errorId: f{self.error_id}) {self.message}'


class GoogleAPIHttpError(BaseGoogleServiceException):
    pass


class MissingFolderStructure(BaseGoogleServiceException):
    pass


class StructureCreationFailed(BaseGoogleServiceException):
    pass


class StructureDeletionFailed(BaseGoogleServiceException):
    pass

class DocumentDeletionFailed(BaseGoogleServiceException):
    pass

class SocialTokenNotFound(BaseGoogleServiceException):
    pass

class FileToDeleteNotFound(BaseGoogleServiceException):
    pass
