from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    # Notification list and detail
    path("", views.NotificationListView.as_view(), name="list"),
    path("<uuid:pk>/", views.NotificationDetailView.as_view(), name="detail"),
    # Actions
    path("<uuid:notification_id>/mark-read/", views.mark_notification_as_read, name="mark_read"),
    path("mark-all-read/", views.mark_all_as_read, name="mark_all_read"),
    # API endpoints
    path("api/unread-count/", views.get_unread_count, name="api_unread_count"),
    path("api/recent/", views.get_recent_notifications, name="api_recent"),
]
