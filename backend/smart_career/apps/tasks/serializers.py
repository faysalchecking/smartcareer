from rest_framework import serializers
from .models import Task, TaskComment
from django.contrib.auth.models import User

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class TaskCommentSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = ['id', 'user', 'comment', 'created_at']
        read_only_fields = ['created_at']

class TaskSerializer(serializers.ModelSerializer):
    # Change: Use basic info instead of full nested serializer
    candidate_id = serializers.IntegerField(write_only=True, required=False)
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    job_title = serializers.CharField(source='job.position', read_only=True, allow_null=True)
    
    assigned_to = UserMinimalSerializer(read_only=True)
    created_by = UserMinimalSerializer(read_only=True)
    comments = TaskCommentSerializer(many=True, read_only=True)
    
    assigned_to_id = serializers.IntegerField(write_only=True, required=False)
    
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'task_id', 'title', 'description',
            'candidate_id', 'candidate_name', 'job_title',
            'job', 'module',
            'assigned_to', 'assigned_to_id', 'created_by',
            'priority', 'status',
            'due_date', 'scheduled_date', 'completed_at',
            'notes', 'completed_notes',
            'created_at', 'updated_at',
            'days_until_due', 'is_overdue', 'comments'
        ]
        read_only_fields = ['task_id', 'created_at', 'updated_at', 'completed_at']
    
    def get_days_until_due(self, obj):
        from datetime import datetime
        if obj.status == 'COMPLETED':
            return None
        delta = obj.due_date - datetime.now(obj.due_date.tzinfo)
        return delta.days
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        return obj.status != 'COMPLETED' and obj.due_date < timezone.now()
    
    def create(self, validated_data):
        assigned_to_id = validated_data.pop('assigned_to_id', None)
        candidate_id = validated_data.pop('candidate_id', None)
        
        task = Task.objects.create(**validated_data)
        
        if assigned_to_id:
            task.assigned_to_id = assigned_to_id
        if candidate_id:
            task.candidate_id = candidate_id
        
        task.save()
        return task


class TaskListSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'task_id', 'title', 'candidate_name', 'module',
            'assigned_to_name', 'priority', 'status', 'due_date',
            'days_until_due', 'is_overdue'
        ]
    
    def get_days_until_due(self, obj):
        from datetime import datetime
        if obj.status == 'COMPLETED':
            return None
        delta = obj.due_date - datetime.now(obj.due_date.tzinfo)
        return delta.days
    
    def get_is_overdue(self, obj):
        from django.utils import timezone
        return obj.status != 'COMPLETED' and obj.due_date < timezone.now()