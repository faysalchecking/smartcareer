from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import VisaType, VisaApplication, EmbassyClearance
from .serializers import VisaTypeSerializer, VisaApplicationSerializer, EmbassyClearanceSerializer

class VisaApplicationViewSet(viewsets.ModelViewSet):
    """Visa application CRUD"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['candidate', 'status', 'visa_type']
    search_fields = ['candidate__full_name', 'visa_app_id']
    ordering_fields = ['submission_date']
    ordering = ['-submission_date']
    
    def get_serializer_class(self):
        return VisaApplicationSerializer
    
    def get_queryset(self):
        return VisaApplication.objects.select_related('candidate', 'job', 'visa_type').all()
    
    def perform_create(self, serializer):
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        serializer.save(visa_app_id=f"VISA-{timestamp}")

class EmbassyClearanceViewSet(viewsets.ModelViewSet):
    """Embassy clearance tracking"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']
    
    def get_serializer_class(self):
        return EmbassyClearanceSerializer
    
    def get_queryset(self):
        return EmbassyClearance.objects.select_related('visa_application', 'visa_application__candidate').all()

class VisaTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Visa types reference"""
    
    permission_classes = [IsAuthenticated]
    queryset = VisaType.objects.filter(is_active=True)
    serializer_class = VisaTypeSerializer