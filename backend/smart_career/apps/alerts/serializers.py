from rest_framework import serializers
from .models import Alert, AlertRule, AlertEscalation
from django.contrib.auth.models import User

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class AlertEscalationSerializer(serializers.ModelSerializer):
    escalated_to = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = AlertEscalation
        fields = ['level', 'escalated_to', 'escalated_at', 'acknowledged']

class AlertSerializer(serializers.ModelSerializer):
    # Change: Use basic info instead of full nested serializer
    candidate_id = serializers.IntegerField(write_only=True, required=False)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True, allow_null=True)
    
    assigned_to = UserMinimalSerializer(read_only=True)
    escalations = AlertEscalationSerializer(many=True, read_only=True)
    
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_id', 'alert_type', 'severity', 'title', 'message',
            'candidate_id', 'candidate_name', 'job', 'assigned_to',
            'is_active', 'is_acknowledged', 'acknowledged_at',
            'alert_date', 'due_date', 'resolved_at',
            'reference_field', 'reference_value',
            'action_required', 'days_until_due', 'escalations'
        ]
    
    def get_days_until_due(self, obj):
        if not obj.due_date:
            return None
        from datetime import datetime
        delta = obj.due_date - datetime.now(obj.due_date.tzinfo)
        return delta.days

class AlertListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True, allow_null=True)
    days_until_due = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_id', 'alert_type', 'severity', 'title',
            'candidate_name', 'is_active', 'is_acknowledged',
            'alert_date', 'due_date', 'days_until_due'
        ]
    
    def get_days_until_due(self, obj):
        if not obj.due_date:
            return None
        from datetime import datetime
        delta = obj.due_date - datetime.now(obj.due_date.tzinfo)
        return delta.days

class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertRule
        fields = [
            'id', 'rule_id', 'name', 'description',
            'trigger_type', 'trigger_value',
            'alert_type', 'alert_severity',
            'is_active', 'auto_escalate', 'escalation_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['rule_id']