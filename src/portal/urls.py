from django.urls import path

from portal.views import IndexView, health_view

urlpatterns = [
    path("", IndexView.as_view(), name='portal_index'),
    path("health/", health_view, name='health')
]
