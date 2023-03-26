import re

from pydantic import BaseModel, validator


class StudentInfo(BaseModel):
    name: str
    parent_name: str
    phone_number: str
    education: str

    @validator('phone_number')
    def phone_validation(cls, v):
        regex = r"^\+?[1-9]\d{1,14}$"
        if v and not re.search(regex, v, re.I):
            raise ValueError("Phone Number Invalid.")
        return v

    @classmethod
    def from_tuple(cls, values: tuple | list):
        return cls(name=values[0], parent_name=values[1], phone_number=values[2], education=values[3])


class StudentResponse(StudentInfo):
    response: str
    status: str = 'started'

    @classmethod
    def from_tuple(cls, values: tuple | list):
        """Not Implemented"""
        raise NotImplementedError('StudentResponse does not instantiate from tuple')

    def to_tuple(self):
        return [self.name, self.parent_name, self.phone_number, self.education, self.response, self.status]
