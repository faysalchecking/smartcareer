from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document, DocumentType, PassportScan
from .serializers import (
    DocumentSerializer,
    DocumentTypeSerializer,
    PassportScanSerializer,
    PassportUploadSerializer,
)
from .services import PassportOCRService
from django.http import FileResponse
from django.core.exceptions import PermissionDenied
from rest_framework import status

class DocumentViewSet(viewsets.ModelViewSet):
    """Document CRUD operations"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['candidate', 'document_type', 'status']
    search_fields = ['original_filename', 'candidate__full_name']
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        if self.action == 'upload_passport':
            return PassportUploadSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        return Document.objects.select_related('candidate', 'document_type', 'verified_by').all()
    
    @action(detail=False, methods=['post'], parser_classes=(MultiPartParser, FormParser))
    def upload_passport(self, request):
        """Upload and extract passport data"""
        serializer = PassportUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        candidate_id = serializer.validated_data['candidate']
        image = serializer.validated_data['image']
        
        try:
            from smart_career.apps.candidates.models import Candidate
            candidate = Candidate.objects.get(id=candidate_id)
        except Candidate.DoesNotExist:
            return Response(
                {'error': 'Candidate not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Save document first
        doc_type = DocumentType.objects.get(name='PASSPORT')
        document = Document.objects.create(
            candidate=candidate,
            document_type=doc_type,
            file=image,
            original_filename=image.name,
            file_size=image.size,
            mime_type=image.content_type,
            uploaded_by=request.user,
            status='UPLOADED'
        )
        
        # Extract passport data
        ocr_service = PassportOCRService()
        ocr_result = ocr_service.extract_from_image(document.file.path)
        
        # Create/update passport scan record
        passport_scan, created = PassportScan.objects.update_or_create(
            candidate=candidate,
            defaults={
                'document': document,
                'status': 'EXTRACTED',
                'mrz_data': ocr_result.get('mrz_data'),
                'passport_number': ocr_result.get('passport_number'),
                'surname': ocr_result.get('surname'),
                'given_name': ocr_result.get('given_name'),
                'nationality': ocr_result.get('nationality'),
                'date_of_birth': ocr_result.get('date_of_birth'),
                'gender': ocr_result.get('gender'),
                'issue_date': ocr_result.get('issue_date'),
                'expiry_date': ocr_result.get('expiry_date'),
                'issuing_country': ocr_result.get('issuing_country'),
                'passport_number_confidence': ocr_result.get('passport_number_confidence', 0),
                'date_of_birth_confidence': ocr_result.get('date_of_birth_confidence', 0),
                'expiry_date_confidence': ocr_result.get('expiry_date_confidence', 0),
                'mrz_valid': ocr_result.get('mrz_valid', False),
            }
        )
        
        return Response({
            'document': DocumentSerializer(document).data,
            'passport_scan': PassportScanSerializer(passport_scan).data,
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify document"""
        document = self.get_object()
        document.status = 'VERIFIED'
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.verification_notes = request.data.get('notes', '')
        document.save()
        
        return Response(DocumentSerializer(document).data)

class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Document type reference"""
    
    permission_classes = [IsAuthenticated]
    queryset = DocumentType.objects.filter(is_active=True)
    serializer_class = DocumentTypeSerializer

class PassportScanViewSet(viewsets.ReadOnlyModelViewSet):
    """Passport scan data (read-only)"""
    
    permission_classes = [IsAuthenticated]
    queryset = PassportScan.objects.all()
    serializer_class = PassportScanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['candidate', 'status']
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Secure document download with permission check"""
        document = self.get_object()
        
        # Permission check
        if not self._can_access_document(request.user, document):
            raise PermissionDenied("You don't have permission to download this document")
        
        # Log download
        AuditLog.objects.create(
            user=request.user,
            action='DOCUMENT_DOWNLOAD',
            object_type='Document',
            object_id=document.id,
            details={
                'candidate': document.candidate.full_name,
                'document_type': document.document_type.name,
                'file_name': document.original_filename,
                'ip_address': self._get_client_ip(request),
            }
        )
        
        # Return file
        response = FileResponse(document.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{document.original_filename}"'
        return response
    
    def _can_access_document(self, user, document):
        """Check if user can access this document"""
        # Admin can see all
        if user.is_superuser or user.is_staff:
            return True
        
        # Candidate can see own documents
        if hasattr(user, 'candidate_profile') and user.candidate_profile.candidate == document.candidate:
            return True
        
        # Recruiter can see assigned candidates
        if hasattr(user, 'recruiter_profile'):
            if user.recruiter_profile in [document.candidate.recruiter]:
                return True
        
        # Agent can see own candidates
        if hasattr(user, 'agent_profile'):
            if user.agent_profile == document.candidate.agent:
                return True
        
        return False
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip