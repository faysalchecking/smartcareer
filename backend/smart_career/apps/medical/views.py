from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import MedicalCenter, MedicalExamination
from .serializers import MedicalCenterSerializer, MedicalExaminationSerializer

class MedicalExaminationViewSet(viewsets.ModelViewSet):
    """Medical examination CRUD"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['candidate', 'status']
    search_fields = ['candidate__full_name', 'medical_exam_id']
    ordering_fields = ['scheduled_date']
    ordering = ['-scheduled_date']
    
    def get_serializer_class(self):
        return MedicalExaminationSerializer
    
    def get_queryset(self):
        return MedicalExamination.objects.select_related('candidate', 'medical_center').all()
    
    def perform_create(self, serializer):
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        serializer.save(
            medical_exam_id=f"MED-{timestamp}",
            created_by=self.request.user
        )

class MedicalCenterViewSet(viewsets.ReadOnlyModelViewSet):
    """Medical centers reference"""
    
    permission_classes = [IsAuthenticated]
    queryset = MedicalCenter.objects.filter(status='ACTIVE')
    serializer_class = MedicalCenterSerializer