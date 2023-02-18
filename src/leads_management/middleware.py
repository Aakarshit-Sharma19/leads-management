from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from exceptions import NonDefaultResponse


class HealthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.META["PATH_INFO"].startswith('/health'):
            return HttpResponse("UP")


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            response = self.get_response(request)
            return response
        except NonDefaultResponse as e:
            return e.response
