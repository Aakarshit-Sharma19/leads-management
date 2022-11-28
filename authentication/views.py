from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.http import HttpRequest, HttpResponse

from authentication.forms import AuthenticationForm


# Create your views here.
class LoginView(DjangoLoginView):
    form_class = AuthenticationForm
    template_name = 'authentication/login.html'


class LogoutView(DjangoLogoutView):
    pass


def abc(request: HttpRequest):
    print(request.POST)
    return HttpResponse(content="hello world")
