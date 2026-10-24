from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AuditLog(models.Model):
    """Comprehensive audit logging for all system activities"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('READ', 'Read'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('DOWNLOAD', 'Download'),
        ('UPLOAD', 'Upload'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('ERROR', 'Error'),
        ('OTHER', 'Other'),
    ]
    
    ENTITY_CHOICES = [
        ('CANDIDATE', 'Candidate'),
        ('JOB', 'Job'),
        ('APPLICATION', 'Application'),
        ('DOCUMENT', 'Document'),
        ('MEDICAL', 'Medical'),
        ('VISA', 'Visa'),
        ('TICKET', 'Ticket'),
        ('DEPLOYMENT', 'Deployment'),
        ('INVOICE', 'Invoice'),
        ('PAYMENT', 'Payment'),
        ('USER', 'User'),
        ('TASK', 'Task'),
        ('ALERT', 'Alert'),
        ('AI_CONVERSATION', 'AI Conversation'),
        ('OTHER', 'Other'),
    ]
    
    log_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # User who performed action
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Action performed
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    # Entity type (what was affected)
    entity_type = models.CharField(
        max_length=50,
        choices=ENTITY_CHOICES,
        db_index=True
    )
    
    # Entity ID (which record)
    entity_id = models.CharField(
        max_length=100,
        db_index=True
    )
    
    # Description
    description = models.TextField(blank=True, null=True)
    
    # HTTP Details
    http_method = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="GET, POST, PATCH, DELETE, etc."
    )
    http_path = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )
    status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text="HTTP response status (200, 400, 404, 500, etc.)"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )
    
    # Change tracking
    old_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Previous value for update operations"
    )
    new_value = models.JSONField(
        null=True,
        blank=True,
        help_text="New value for update operations"
    )
    
    # Additional context
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional JSON context"
    )
    
    # Timestamps
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['action']),
            models.Index(fields=['status_code']),
        ]
    
    def __str__(self):
        return f"{self.log_id} - {self.action} {self.entity_type} by {self.user}"
    
    def save(self, *args, **kwargs):
        if not self.log_id:
            from datetime import datetime
            count = AuditLog.objects.count() + 1
            self.log_id = f"AUL-{datetime.now().strftime('%Y%m%d')}-{count:06d}"
        super().save(*args, **kwargs)