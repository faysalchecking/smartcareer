from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from smart_career.apps.candidates.models import Candidate
from smart_career.apps.jobs.models import Job

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('OVERDUE', 'Overdue'),
    ]
    
    task_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Relationships
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks'
    )
    
    # Task metadata
    module = models.CharField(
        max_length=50,
        choices=[
            ('RECRUITMENT', 'Recruitment'),
            ('DOCUMENTS', 'Documents'),
            ('MEDICAL', 'Medical'),
            ('VISA', 'Visa'),
            ('EMBASSY', 'Embassy'),
            ('TICKETS', 'Tickets'),
            ('DEPLOYMENT', 'Deployment'),
            ('FINANCE', 'Finance'),
            ('OTHER', 'Other'),
        ],
        default='OTHER'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Dates
    due_date = models.DateTimeField()
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Audit
    notes = models.TextField(blank=True, null=True)
    completed_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tasks'
        ordering = ['-priority', 'due_date']
        indexes = [
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.task_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.task_id:
            from datetime import datetime
            count = Task.objects.count() + 1
            self.task_id = f"TSK-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        # Auto-mark as overdue
        if self.status != 'COMPLETED' and self.due_date < timezone.now():
            self.status = 'OVERDUE'
        
        super().save(*args, **kwargs)


class TaskComment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.task_id}"