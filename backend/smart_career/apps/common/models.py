from django.db import models
from django.contrib.auth.models import User
import json

class AuditLog(models.Model):
    """Track sensitive operations"""
    
    ACTION_CHOICES = [
        ('LOGIN', 'User Login'),
        ('LOGOUT', 'User Logout'),
        ('CREATE', 'Create Record'),
        ('UPDATE', 'Update Record'),
        ('DELETE', 'Delete Record'),
        ('DOCUMENT_UPLOAD', 'Document Upload'),
        ('DOCUMENT_DOWNLOAD', 'Document Download'),
        ('DOCUMENT_VIEW', 'Document View'),
        ('DOCUMENT_VERIFY', 'Document Verify'),
        ('CANDIDATE_MERGE', 'Candidate Merge'),
        ('PAYMENT_RECORD', 'Payment Record'),
        ('EXPORT', 'Export Data'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    object_type = models.CharField(max_length=100)  # e.g., 'Document', 'Candidate', 'Payment'
    object_id = models.IntegerField(null=True, blank=True)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['object_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"