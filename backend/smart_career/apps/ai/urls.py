from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIProviderViewSet, AIConversationViewSet, AIToolCallViewSet,
    AIJobViewSet, AILogViewSet
)

router = DefaultRouter()
router.register(r'providers', AIProviderViewSet, basename='ai-provider')
router.register(r'conversations', AIConversationViewSet, basename='ai-conversation')
router.register(r'tools', AIToolCallViewSet, basename='ai-tool')
router.register(r'jobs', AIJobViewSet, basename='ai-job')
router.register(r'logs', AILogViewSet, basename='ai-log')

urlpatterns = [
    path('', include(router.urls)),
]