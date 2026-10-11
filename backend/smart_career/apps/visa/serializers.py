from rest_framework import serializers
from .models import VisaType, VisaApplication, EmbassyClearance

class VisaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisaType
        fields = ['id', 'name', 'country', 'processing_days', 'validity_months']

class VisaApplicationSerializer(serializers.ModelSerializer):
    visa_type_name = serializers.CharField(source='visa_type.name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_pending = serializers.ReadOnlyField()
    
    class Meta:
        model = VisaApplication
        fields = [
            'id', 'visa_app_id', 'candidate', 'job_title', 'visa_type_name',
            'application_number', 'submission_date', 'approval_date', 'visa_issue_date',
            'visa_expiry_date', 'status', 'is_expired', 'days_pending', 'remarks', 'created_at'
        ]

class EmbassyClearanceSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='visa_application.candidate.full_name', read_only=True)
    
    class Meta:
        model = EmbassyClearance
        fields = [
            'id', 'candidate_name', 'appointment_date', 'appointment_time',
            'submission_date', 'clearance_date', 'status', 'passport_submitted',
            'passport_submission_date', 'passport_return_date', 'result', 'remarks'
        ]