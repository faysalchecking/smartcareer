from rest_framework import serializers
from django.utils import timezone
from .models import Candidate, Agent, Recruiter

class CandidateMinimalSerializer(serializers.ModelSerializer):
    """Minimal candidate info for relationships"""
    class Meta:
        model = Candidate
        fields = ['id', 'candidate_id', 'full_name', 'passport_number']
        read_only_fields = ['candidate_id']
        
class AgentSerializer(serializers.ModelSerializer):
    """Serialize agent information"""
    class Meta:
        model = Agent
        fields = ['id', 'agent_id', 'company_name', 'email', 'phone', 'status']

class RecruiterSerializer(serializers.ModelSerializer):
    """Serialize recruiter information"""
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = Recruiter
        fields = ['id', 'employee_id', 'name', 'phone', 'department']
    
    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

class CandidateListSerializer(serializers.ModelSerializer):
    """Serialize candidate for list view"""
    agent_name = serializers.CharField(source='agent.company_name', read_only=True)
    recruiter_name = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    passport_validity_days = serializers.ReadOnlyField()
    is_passport_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidate
        fields = [
            'id', 'candidate_id', 'full_name', 'mobile', 'email',
            'passport_number', 'date_of_birth', 'age', 'nationality',
            'current_status', 'current_stage', 'passport_expiry_date',
            'passport_validity_days', 'is_passport_expired',
            'agent_name', 'recruiter_name', 'created_at'
        ]
        read_only_fields = ['id', 'candidate_id', 'created_at']
    
    def get_recruiter_name(self, obj):
        if obj.recruiter:
            return obj.recruiter.user.get_full_name() or obj.recruiter.user.username
        return None

class CandidateDetailSerializer(serializers.ModelSerializer):
    """Serialize candidate for detail view"""
    agent = AgentSerializer(read_only=True)
    recruiter = RecruiterSerializer(read_only=True)
    age = serializers.ReadOnlyField()
    passport_validity_days = serializers.ReadOnlyField()
    is_passport_expired = serializers.ReadOnlyField()
    is_passport_expiring_soon = serializers.ReadOnlyField()
    
    class Meta:
        model = Candidate
        fields = [
            'id', 'candidate_id',  'full_name', 'surname', 'given_name',
            'date_of_birth', 'age', 'gender', 'nationality', 'mobile',
            'alternative_mobile', 'email', 'address', 'district', 'upazila',
            'nid', 'passport_number', 'passport_issue_date', 'passport_expiry_date',
            'passport_issuing_country', 'passport_validity_days', 'is_passport_expired',
            'is_passport_expiring_soon', 'education', 'experience', 'skills',
            'languages', 'preferred_country', 'preferred_position', 'agent',
            'recruiter', 'source', 'current_stage', 'current_status', 'availability',
            'notes', 'created_at', 'updated_at', 'created_by'
        ]
        read_only_fields = ['id', 'candidate_id', 'created_at', 'updated_at', 'created_by']

class CandidateCreateUpdateSerializer(serializers.ModelSerializer):
    """Serialize candidate for create/update"""
    class Meta:
        model = Candidate
        fields = [
            'full_name', 'surname', 'given_name', 'date_of_birth', 'gender',
            'nationality', 'mobile', 'alternative_mobile', 'email', 'address',
            'district', 'upazila', 'nid', 'passport_number', 'passport_issue_date',
            'passport_expiry_date', 'passport_issuing_country', 'education',
            'experience', 'skills', 'languages', 'preferred_country',
            'preferred_position', 'agent', 'recruiter', 'source', 'current_stage',
            'current_status', 'availability', 'notes'
        ]
    
    def create(self, validated_data):
        # Generate candidate_id
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        candidate_id = f"SC-{timestamp}"
        validated_data['candidate_id'] = candidate_id
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)