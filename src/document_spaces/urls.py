from django.urls import path

from document_spaces import apis
from document_spaces import views

urlpatterns = [
    path("<int:space_id>/file_upload", views.SpaceFileUploadView.as_view(), name='spaces_file_upload'),
    path("<int:space_id>/doc/<int:file_id>/submit", views.SpaceResponseSubmitView.as_view(),
         name='spaces_submit_entry'),
    path("<int:space_id>/followup/<int:file_id>/", views.SpaceFollowUpView.as_view(), name='spaces_follow_up'),
    path("<int:space_id>/followup/<int:file_id>/resolve/<int:student_id>", views.SpaceResolveResponseView.as_view(),
         name='spaces_follow_up_resolve'),
    path("<int:space_id>/followup/<int:file_id>/manage/<int:student_id>", views.SpaceResponseUpdateView.as_view(),
         name='spaces_follow_up_manage'),
    path("<int:space_id>/admin/create/manager", views.create_user_as_manager, name='spaces_create_manager'),
    path("<int:space_id>/admin/create/writer", views.create_user_as_writer, name='spaces_create_writer'),
    path("<int:space_id>/overview", views.SpaceOverviewView.as_view(), name='spaces_overview'),
    path("<int:space_id>/file_delete/<int:file_id>", views.SpaceFileDeleteView.as_view(), name='spaces_file_delete'),
    path("initialize", views.SpaceInitializeView.as_view(), name='spaces_initialize'),
    path("list", views.SpaceListView.as_view(), name='spaces_list'),
    path('api/', apis.spaces_api.urls)
]
