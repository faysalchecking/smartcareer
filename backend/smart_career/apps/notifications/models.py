from django.db import models
from django.contrib.auth.models import User

class NotificationTemplate(models.Model):
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('IN_APP', 'In-App'),
        ('WHATSAPP', 'WhatsApp'),
    ]
    
    template_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default='IN_APP'
    )
    
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    
    # Variables like {{candidate_name}}, {{job_title}}, etc.
    variables = models.JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['channel', 'name']
    
    def __str__(self):
        return f"{self.template_id} - {self.name} ({self.channel})"
    
    def save(self, *args, **kwargs):
        if not self.template_id:
            count = NotificationTemplate.objects.count() + 1
            self.template_id = f"TPL-{count:04d}"
        super().save(*args, **kwargs)


class Notification(models.Model):
    # FIX: Define choices BEFORE using them
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'),
        ('BOUNCED', 'Bounced'),
    ]
    
    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('IN_APP', 'In-App'),
        ('WHATSAPP', 'WhatsApp'),
    ]
    
    notification_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # FIX: Use CHANNEL_CHOICES (not STATUS_CHOICES)
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default='IN_APP'
    )
    
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    
    # FIX: Use STATUS_CHOICES
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    failure_reason = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'read_at']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_id} - {self.recipient.username}"
    
    def save(self, *args, **kwargs):
        if not self.notification_id:
            from datetime import datetime
            count = Notification.objects.count() + 1
            self.notification_id = f"NOT-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        super().save(*args, **kwargs)