from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from smart_career.apps.candidates.models import Candidate
from smart_career.apps.jobs.models import Job

class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('PASSPORT_EXPIRY', 'Passport Expiry'),
        ('DOCUMENT_EXPIRY', 'Document Expiry'),
        ('MEDICAL_DUE', 'Medical Due'),
        ('VISA_PENDING', 'Visa Pending'),
        ('VISA_EXPIRY', 'Visa Expiry'),
        ('EMBASSY_DUE', 'Embassy Due'),
        ('TICKET_DEPARTURE', 'Ticket Departure'),
        ('PAYMENT_DUE', 'Payment Due'),
        ('TASK_OVERDUE', 'Task Overdue'),
        ('SLA_BREACH', 'SLA Breach'),
        ('CANDIDATE_PENDING', 'Candidate Pending'),
        ('MISSING_DOCUMENT', 'Missing Document'),
        ('OTHER', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
        ('INFO', 'Info'),
    ]
    
    alert_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    alert_type = models.CharField(
        max_length=50,
        choices=ALERT_TYPE_CHOICES
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='MEDIUM'
    )
    
    # Relationships
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    
    # Content
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_required = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Dates
    alert_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Reference data
    reference_field = models.CharField(max_length=100, blank=True)
    reference_value = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'alerts'
        ordering = ['-severity', '-alert_date']
        indexes = [
            models.Index(fields=['is_active', 'severity']),
            models.Index(fields=['assigned_to', 'is_acknowledged']),
            models.Index(fields=['alert_date']),
        ]
    
    def __str__(self):
        return f"{self.alert_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.alert_id:
            from datetime import datetime
            count = Alert.objects.count() + 1
            self.alert_id = f"ALR-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        super().save(*args, **kwargs)


class AlertRule(models.Model):
    TRIGGER_CHOICES = [
        ('PASSPORT_DAYS_BEFORE_EXPIRY', 'Passport Days Before Expiry'),
        ('DOCUMENT_DAYS_BEFORE_EXPIRY', 'Document Days Before Expiry'),
        ('MEDICAL_DAYS_BEFORE_DUE', 'Medical Days Before Due'),
        ('VISA_DAYS_PENDING', 'Visa Days Pending'),
        ('PAYMENT_DAYS_OVERDUE', 'Payment Days Overdue'),
        ('TASK_DAYS_OVERDUE', 'Task Days Overdue'),
        ('CANDIDATE_DAYS_IN_STAGE', 'Candidate Days In Stage'),
    ]
    
    rule_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_CHOICES)
    trigger_value = models.IntegerField(help_text="Number of days")
    
    alert_type = models.CharField(max_length=50)
    alert_severity = models.CharField(
        max_length=20,
        choices=Alert.SEVERITY_CHOICES,
        default='MEDIUM'
    )
    
    is_active = models.BooleanField(default=True)
    auto_escalate = models.BooleanField(default=False)
    escalation_days = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_rules'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.rule_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.rule_id:
            count = AlertRule.objects.count() + 1
            self.rule_id = f"RULE-{count:04d}"
        super().save(*args, **kwargs)


class AlertEscalation(models.Model):
    ESCALATION_LEVEL_CHOICES = [
        (1, 'Level 1 - Assigned User'),
        (2, 'Level 2 - Manager'),
        (3, 'Level 3 - Admin'),
    ]
    
    alert = models.ForeignKey(
        Alert,
        on_delete=models.CASCADE,
        related_name='escalations'
    )
    level = models.IntegerField(choices=ESCALATION_LEVEL_CHOICES)
    escalated_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='escalated_alerts'
    )
    escalated_at = models.DateTimeField(auto_now_add=True)
    acknowledged = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'alert_escalations'
        unique_together = ['alert', 'level']