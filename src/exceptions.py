from django.http import HttpResponse


class NonDefaultResponse(Exception):
    def __init__(self, response: HttpResponse):
        self.response = response
