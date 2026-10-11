from rest_framework import serializers
from .models import Application, ScreeningQuestion, ScreeningAnswer, ScreeningResult, Shortlist

class ScreeningQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningQuestion
        fields = ['id', 'question_number', 'question_text', 'question_type', 'is_required', 'options', 'points']

class ScreeningAnswerSerializer(serializers.ModelSerializer):
    question = ScreeningQuestionSerializer(read_only=True)
    
    class Meta:
        model = ScreeningAnswer
        fields = ['id', 'question', 'answer_text', 'answer_selected', 'score', 'is_correct', 'answered_at']

class ScreeningResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningResult
        fields = [
            'id', 'hard_criteria_passed', 'total_score', 'screening_questions_score',
            'ai_match_score', 'result', 'reasoning', 'ai_confidence', 'reviewed_at', 'review_notes'
        ]

class ApplicationListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    screening_result = ScreeningResultSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'application_id', 'candidate_name', 'job_title', 'status',
            'screening_score', 'screening_result_data', 'applied_at'  # changed
        ]

class ApplicationDetailSerializer(serializers.ModelSerializer):
    candidate = serializers.SerializerMethodField()
    job = serializers.SerializerMethodField()
    screening_answers = ScreeningAnswerSerializer(many=True, read_only=True)
    screening_result = ScreeningResultSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'application_id', 'candidate', 'job', 'status',
            'screening_score', 'screening_result', 'screening_notes',
            'screening_answers', 'is_eligible_by_criteria', 'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'application_id', 'is_eligible_by_criteria', 'applied_at', 'updated_at']
    
    def get_candidate(self, obj):
        from smart_career.apps.candidates.serializers import CandidateListSerializer
        return CandidateListSerializer(obj.candidate).data
    
    def get_job(self, obj):
        from smart_career.apps.jobs.serializers import JobListSerializer
        return JobListSerializer(obj.job).data

class ShortlistSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='application.candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = Shortlist
        fields = [
            'id', 'candidate_name', 'job_title', 'shortlist_date',
            'shortlist_reason', 'interview_scheduled', 'interview_date', 'interview_location'
        ]

class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['candidate', 'job']
    
    def create(self, validated_data):
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        validated_data['application_id'] = f"APP-{timestamp}"
        validated_data['applied_by'] = self.context['request'].user
        return super().create(validated_data)

class ScreeningAnswerSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScreeningAnswer
        fields = ['question', 'answer_text', 'answer_selected', 'answer_file']