from rest_framework import serializers
from .models import (
    AIProvider, AIConversation, AIMessage, AIToolCall, AIJob, AILog
)
from django.contrib.auth.models import User

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class AIProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIProvider
        fields = [
            'id', 'provider_id', 'name', 'provider_type',
            'model_name', 'temperature', 'max_tokens',
            'is_active', 'is_default', 'is_working',
            'last_tested', 'created_at'
        ]
        read_only_fields = ['provider_id']

class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = [
            'id', 'role', 'content', 'tokens_used',
            'tool_calls', 'metadata', 'created_at'
        ]
        read_only_fields = ['created_at']

class AIConversationSerializer(serializers.ModelSerializer):
    messages = AIMessageSerializer(many=True, read_only=True)
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = AIConversation
        fields = [
            'id', 'conversation_id', 'user', 'title',
            'candidate', 'job', 'total_messages', 'total_tokens_used',
            'messages', 'created_at', 'updated_at'
        ]
        read_only_fields = ['conversation_id', 'total_messages', 'total_tokens_used']

class AIConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversation
        fields = [
            'id', 'conversation_id', 'title',
            'total_messages', 'total_tokens_used',
            'created_at', 'updated_at'
        ]

class AIToolCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIToolCall
        fields = [
            'id', 'tool_call_id', 'tool_name', 'tool_description',
            'parameters', 'status', 'result', 'error_message',
            'requires_approval', 'approved_by', 'created_at', 'executed_at'
        ]
        read_only_fields = ['tool_call_id']

class AIJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIJob
        fields = [
            'id', 'ai_job_id', 'job_type', 'user', 'candidate', 'job',
            'input_params', 'status', 'result', 'error_message',
            'started_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['ai_job_id']

        
class AILogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AILog
        fields = [
            'id', 'log_id', 'user_name', 'activity_type',
            'description', 'details', 'created_at'
        ]
        read_only_fields = ['log_id', 'created_at']