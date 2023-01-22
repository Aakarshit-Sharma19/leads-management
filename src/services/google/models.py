import re

from pydantic import BaseModel, validator


class StudentInfo(BaseModel):
    sno: str
    name: str
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
        return cls(sno=values[0], name=values[1], phone_number=values[2], education=values[3])


class StudentResponse(StudentInfo):
    response = str

    @classmethod
    def from_tuple(cls, values: tuple | list):
        """Not Implemented"""
        raise NotImplementedError('StudentResponse does not instantiation from tuple')

    def to_tuple(self):
        return [self.sno, self.name, self.phone_number, self.education, self.response]