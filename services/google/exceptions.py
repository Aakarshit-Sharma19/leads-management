import uuid


class GoogleAPIHttpError(Exception):

    def __init__(self, message):
        self.error_id = uuid.uuid4()
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}: (errorId: f{self.error_id}) {self.message}'


class MissingFolderStructure(Exception):
    def __init__(self, message):
        self.error_id = uuid.uuid4()
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}: (errorId: f{self.error_id}) {self.message}'


class StructureCreationFailed(Exception):
    def __init__(self, message):
        self.error_id = uuid.uuid4()
        self.message = message


class StructureDeletionFailed(Exception):
    def __init__(self, message):
        self.error_id = uuid.uuid4()
        self.message = message


class SocialTokenNotFound(Exception):
    def __init__(self, message):
        self.error_id = uuid.uuid4()
        self.message = message
