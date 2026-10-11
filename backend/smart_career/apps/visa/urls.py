from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VisaApplicationViewSet, EmbassyClearanceViewSet, VisaTypeViewSet

router = DefaultRouter()
router.register(r'applications', VisaApplicationViewSet, basename='visa_app')
router.register(r'embassy', EmbassyClearanceViewSet, basename='embassy')
router.register(r'types', VisaTypeViewSet, basename='visa_type')

app_name = 'visa'
urlpatterns = [path('', include(router.urls))]