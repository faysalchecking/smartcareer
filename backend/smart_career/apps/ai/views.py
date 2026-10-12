from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import (
    AIProvider, AIConversation, AIMessage, AIToolCall, AIJob, AILog
)
from .serializers import (
    AIProviderSerializer, AIConversationSerializer, AIConversationListSerializer,
    AIMessageSerializer, AIToolCallSerializer, AIJobSerializer, AILogSerializer
)
from .ai_service import AIService

class AIProviderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AIProvider.objects.all()
    serializer_class = AIProviderSerializer
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test provider connection"""
        provider_obj = self.get_object()
        service = AIService(request.user)
        
        # Temporarily set provider for testing
        from .ai_provider import AIProviderFactory
        try:
            provider = AIProviderFactory.get_provider(provider_obj)
            result = provider.test_connection()
            
            # Update provider status
            provider_obj.is_working = result.get('working', False)
            provider_obj.last_tested = timezone.now()
            provider_obj.save()
            
            return Response(result)
        except Exception as e:
            return Response({
                'working': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class AIConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIConversation.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AIConversationListSerializer
        return AIConversationSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send message to AI"""
        conversation = self.get_object()
        user_message = request.data.get('message')
        
        if not user_message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = AIService(request.user)
        result = service.send_message(conversation, user_message)
        
        if not result['success']:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'message': AIMessageSerializer(result['message']).data,
            'tokens_used': result.get('tokens_used', 0),
        })

class AIToolCallViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AIToolCall.objects.all()
    serializer_class = AIToolCallSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve AI tool call"""
        tool_call = self.get_object()
        tool_call.status = 'APPROVED'
        tool_call.approved_by = request.user
        tool_call.save()
        
        return Response(AIToolCallSerializer(tool_call).data)

class AIJobViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIJob.objects.filter(user=self.request.user)
    
    serializer_class = AIJobSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate_cv(self, request):
        """Generate CV using AI"""
        candidate_id = request.data.get('candidate_id')
        job_id = request.data.get('job_id')
        language = request.data.get('language', 'English')
        
        if not candidate_id:
            return Response(
                {'error': 'candidate_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = AIService(request.user)
        result = service.generate_cv(candidate_id, job_id, language)
        
        if not result['success']:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def match_candidates(self, request):
        """Find candidates matching a job"""
        job_id = request.data.get('job_id')
        limit = request.data.get('limit', 10)
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = AIService(request.user)
        result = service.match_candidates_to_job(job_id, limit)
        
        if not result['success']:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(result)
class AILogViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AILog.objects.filter(user=self.request.user)
    
    serializer_class = AILogSerializer