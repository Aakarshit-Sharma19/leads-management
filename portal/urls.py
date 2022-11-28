from django.urls import path

from portal.views import IndexView

urlpatterns = [
    path("", IndexView.as_view(), name='index')
]
