from rest_framework import serializers
from .models import MedicalCenter, MedicalExamination

class MedicalCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCenter
        fields = ['id', 'center_id', 'name', 'country', 'city', 'phone', 'email']

class MedicalExaminationSerializer(serializers.ModelSerializer):
    center_name = serializers.CharField(source='medical_center.name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    
    class Meta:
        model = MedicalExamination
        fields = [
            'id', 'medical_exam_id', 'candidate', 'center_name', 'exam_type',
            'scheduled_date', 'scheduled_time', 'status', 'attended_date', 'result',
            'certificate_number', 'certificate_issue_date', 'certificate_expiry_date',
            'is_expired', 'days_until_expiry', 'doctor_notes', 'remarks', 'created_at'
        ]