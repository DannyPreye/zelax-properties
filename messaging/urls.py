from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageThreadViewSet, MessageViewSet

router = DefaultRouter()
router.register(r"threads", MessageThreadViewSet, basename="message-thread")

app_name = "messaging"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "threads/<int:thread_id>/messages/",
        MessageViewSet.as_view({"get": "list", "post": "create"}),
        name="thread-messages",
    ),
    path(
        "threads/<int:thread_id>/messages/<int:pk>/",
        MessageViewSet.as_view({"get": "retrieve"}),
        name="message-detail",
    ),
]


