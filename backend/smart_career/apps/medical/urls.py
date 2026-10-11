from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MedicalExaminationViewSet, MedicalCenterViewSet

router = DefaultRouter()
router.register(r'', MedicalExaminationViewSet, basename='medical_exam')
router.register(r'centers', MedicalCenterViewSet, basename='medical_center')

app_name = 'medical'
urlpatterns = [path('', include(router.urls))]