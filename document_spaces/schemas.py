from ninja import Schema
from pydantic import EmailStr


class UserRequestBody(Schema):
    email: EmailStr

class ManagerRequest(UserRequestBody):
    pass

class WriterRequest(UserRequestBody):
    pass

class ErrorResponse(Schema):
    message: str