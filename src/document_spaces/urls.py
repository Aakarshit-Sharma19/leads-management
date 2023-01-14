from django.urls import path

from document_spaces import views
from document_spaces import apis

urlpatterns = [
    path("<int:pk>/overview", views.SpaceOverviewView.as_view(), name='spaces_overview'),
    path("initialize", views.SpaceInitializeView.as_view(), name='spaces_initialize'),
    path("list", views.SpaceListView.as_view(), name='spaces_list'),
    path("<int:pk>/file_upload", views.SpaceFileUpload.as_view(), name='spaces_file_upload'),
    path("<int:space_pk>/file_delete/<int:pk>", views.SpaceFileDeleteView.as_view(), name='spaces_file_delete'),
    path('api/', apis.spaces_api.urls)
]
