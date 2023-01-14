from django.urls import path, include
from authentication import views
urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name='accounts_users_profile'),
    path("profile/change-password/", views.profile_change_password_url, name='accounts_change_password')
]