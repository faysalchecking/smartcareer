from rest_framework import serializers
from .models import Notification, NotificationTemplate
from django.contrib.auth.models import User

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'template_id', 'name', 'description',
            'channel', 'subject', 'body', 'variables',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['template_id']

class NotificationSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_id', 'recipient_name', 'template_name',
            'channel', 'subject', 'body', 'status',
            'sent_at', 'delivered_at', 'read_at',
            'failure_reason', 'retry_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['notification_id', 'sent_at', 'delivered_at']

class NotificationListSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_id', 'recipient_name', 'channel',
            'subject', 'status', 'read_at', 'created_at'
        ]