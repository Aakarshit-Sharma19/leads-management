from django.urls import path

from portal.views import IndexView, RecentActivityView

urlpatterns = [
    path("", IndexView.as_view(), name='portal_index'),
    path("recent-activity/", RecentActivityView.as_view(), name='portal_recent_activity')
]
