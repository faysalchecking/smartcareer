from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApplicationViewSet, ScreeningQuestionViewSet, ShortlistViewSet

app_name = 'applications'

router = DefaultRouter()
router.register(r'', ApplicationViewSet, basename='application')
router.register(r'questions', ScreeningQuestionViewSet, basename='screening_question')
router.register(r'shortlists', ShortlistViewSet, basename='shortlist')

urlpatterns = [
    path('', include(router.urls)),
]