from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.db import connection

from exceptions import NonDefaultResponse


class HealthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.META["PATH_INFO"].startswith('/health'):
            connection.ensure_connection()
            return HttpResponse("UP")


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            return self.get_response(request)
        except NonDefaultResponse as e:
            return e.response
