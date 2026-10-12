from rest_framework import serializers
from .models import Agent
from django.contrib.auth.models import User

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class AgentSerializer(serializers.ModelSerializer):
    assigned_user = UserMinimalSerializer(read_only=True)
    assigned_user_id = serializers.IntegerField(write_only=True, required=False)
    
    candidate_count = serializers.SerializerMethodField()
    total_deployed = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'agent_id', 'company_name', 'contact_person',
            'email', 'phone', 'alternative_phone',
            'address', 'city', 'country', 'postal_code',
            'license_number', 'license_expiry', 'agreement_date',
            'commission_rate', 'payment_terms',
            'status', 'assigned_user', 'assigned_user_id',
            'notes', 'created_at', 'updated_at',
            'candidate_count', 'total_deployed'
        ]
        read_only_fields = ['agent_id', 'created_at', 'updated_at']
    
    def get_candidate_count(self, obj):
        return obj.candidate_set.filter(status='ACTIVE').count()
    
    def get_total_deployed(self, obj):
        from smart_career.apps.candidates.models import Candidate
        return Candidate.objects.filter(
            agent=obj,
            current_status='DEPLOYED'
        ).count()
    
    def create(self, validated_data):
        assigned_user_id = validated_data.pop('assigned_user_id', None)
        agent = Agent.objects.create(**validated_data)
        if assigned_user_id:
            agent.assigned_user_id = assigned_user_id
            agent.save()
        return agent

class AgentListSerializer(serializers.ModelSerializer):
    candidate_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Agent
        fields = [
            'id', 'agent_id', 'company_name', 'contact_person',
            'email', 'phone', 'country', 'status',
            'candidate_count'
        ]
    
    def get_candidate_count(self, obj):
        return obj.candidate_set.filter(status='ACTIVE').count()