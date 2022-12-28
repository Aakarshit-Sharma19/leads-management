from django.urls import path

from document_spaces import views
from document_spaces import apis

urlpatterns = [
    path("<int:pk>/overview", views.SpaceOverviewView.as_view(), name='spaces_overview'),
    path("initialize", views.SpaceInitializeView.as_view(), name='spaces_initialize'),
    path("list", views.SpaceListView.as_view(), name='spaces_list'),
    path('api/', apis.spaces_api.urls)
]
