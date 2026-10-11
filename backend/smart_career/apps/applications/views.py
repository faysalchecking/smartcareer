from django.db import models
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from importlib import import_module

try:
    DjangoFilterBackend = import_module(
        'django_filters.rest_framework'
    ).DjangoFilterBackend
except ModuleNotFoundError:
    # Keep the API usable when django-filter is not installed.
    DjangoFilterBackend = filters.BaseFilterBackend
from .models import Application, ScreeningQuestion, ScreeningAnswer, ScreeningResult, Shortlist
from .serializers import (
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationCreateSerializer,
    ScreeningQuestionSerializer,
    ScreeningAnswerSubmitSerializer,
    ScreeningResultSerializer,
    ShortlistSerializer,
)

class ApplicationViewSet(viewsets.ModelViewSet):
    """Application CRUD and screening"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job', 'candidate', 'status', 'screening_result__result']
    search_fields = ['candidate__full_name', 'job__title', 'application_id']
    ordering_fields = ['applied_at', 'screening_score']
    ordering = ['-applied_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ApplicationDetailSerializer
        elif self.action == 'create':
            return ApplicationCreateSerializer
        return ApplicationListSerializer
    
    def get_queryset(self):
        return Application.objects.select_related(
            'candidate', 'job', 'screening_result'
        ).prefetch_related('screening_answers').all()
    
    def create(self, request, *args, **kwargs):
        """Create new application"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Run screening
        app = serializer.instance
        self._run_screening(app)
        
        return Response(
            ApplicationDetailSerializer(app).data,
            status=status.HTTP_201_CREATED
        )
    
    def _run_screening(self, application):
        """Run automated screening"""
        job = application.job
        candidate = application.candidate
        
        # Check hard criteria
        hard_criteria_passed = application.is_eligible_by_criteria
        
        # Get screening answers
        total_answer_score = 0
        answered_questions = application.screening_answers.count()
        
        if answered_questions > 0:
            total_answer_score = application.screening_answers.aggregate(
                models.Sum('score')
            )['score__sum'] or 0
            max_score = ScreeningQuestion.objects.filter(job=job).aggregate(
                models.Sum('points')
            )['points__sum'] or 100
            screening_percentage = (total_answer_score / max_score * 100) if max_score > 0 else 0
        else:
            screening_percentage = 0
        
        # Simple AI matching (can be enhanced)
        ai_match_score = 75.0  # Placeholder
        
        # Overall score
        total_score = (screening_percentage * 0.6) + (ai_match_score * 0.4)
        
        # Determine result
        if not hard_criteria_passed:
            result = 'INELIGIBLE'
            reasoning = "Candidate does not meet hard eligibility criteria"
        elif total_score >= 80:
            result = 'ELIGIBLE'
            reasoning = f"High screening score: {total_score:.1f}/100"
        elif total_score >= 60:
            result = 'MANUAL_REVIEW'
            reasoning = f"Moderate screening score: {total_score:.1f}/100. Manual review recommended."
        else:
            result = 'INELIGIBLE'
            reasoning = f"Low screening score: {total_score:.1f}/100"
        
        # Create screening result
        ScreeningResult.objects.update_or_create(
            application=application,
            defaults={
                'hard_criteria_passed': hard_criteria_passed,
                'total_score': total_score,
                'screening_questions_score': screening_percentage,
                'ai_match_score': ai_match_score,
                'result': result,
                'reasoning': reasoning,
                'ai_confidence': 0.85,
            }
        )
        
        # Update application
        application.screening_score = total_score
        application.screening_status = result
        application.status = 'SCREENING'
        application.save()
    
    @action(detail=True, methods=['post'])
    def submit_screening_answers(self, request, pk=None):
        """Submit screening answers"""
        application = self.get_object()
        answers_data = request.data.get('answers', [])
        
        for answer in answers_data:
            serializer = ScreeningAnswerSubmitSerializer(data=answer)
            serializer.is_valid(raise_exception=True)
            serializer.save(application=application)
        
        # Re-run screening
        self._run_screening(application)
        
        return Response(ApplicationDetailSerializer(application).data)
    
    @action(detail=True, methods=['post'])
    def shortlist(self, request, pk=None):
        """Shortlist candidate"""
        application = self.get_object()
        
        shortlist, created = Shortlist.objects.get_or_create(
            application=application,
            job=application.job,
            defaults={
                'shortlist_reason': request.data.get('reason', ''),
                'shortlisted_by': request.user,
            }
        )
        
        application.status = 'SHORTLISTED'
        application.save()
        
        return Response(ShortlistSerializer(shortlist).data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject application"""
        application = self.get_object()
        application.status = 'REJECTED'
        application.screening_notes = request.data.get('reason', '')
        application.save()
        
        return Response(ApplicationDetailSerializer(application).data)

class ScreeningQuestionViewSet(viewsets.ModelViewSet):
    """Screening questions for a job"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ScreeningQuestionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job']
    
    def get_queryset(self):
        return ScreeningQuestion.objects.all()

class ShortlistViewSet(viewsets.ReadOnlyModelViewSet):
    """Shortlist management"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ShortlistSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['job', 'application__candidate']
    
    def get_queryset(self):
        return Shortlist.objects.select_related('job', 'application', 'application__candidate').all()