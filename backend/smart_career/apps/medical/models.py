from django.db import models
from django.utils import timezone

class MedicalCenter(models.Model):
    """Medical examination center"""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    
    center_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.country}"


class MedicalExamination(models.Model):
    """Medical examination record"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('ATTENDED', 'Attended'),
        ('PENDING_RESULT', 'Pending Result'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    EXAM_TYPE_CHOICES = [
        ('GENERAL', 'General Medical'),
        ('SPECIALIST', 'Specialist'),
        ('FOLLOW_UP', 'Follow-up'),
    ]
    
    # Relationships
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='medical_exams')
    medical_center = models.ForeignKey(MedicalCenter, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Exam details
    medical_exam_id = models.CharField(max_length=20, unique=True, db_index=True)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='GENERAL')
    
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField(null=True, blank=True)
    
    # Results
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    attended_date = models.DateField(null=True, blank=True)
    result = models.CharField(
        max_length=20,
        choices=[('PASS', 'Pass'), ('FAIL', 'Fail')],
        null=True, blank=True
    )
    
    # Certificate
    certificate_number = models.CharField(max_length=100, null=True, blank=True)
    certificate_issue_date = models.DateField(null=True, blank=True)
    certificate_expiry_date = models.DateField(null=True, blank=True)
    certificate_file = models.FileField(upload_to='medical_certificates/%Y/%m/%d/', null=True, blank=True)
    
    # Details
    test_results = models.JSONField(null=True, blank=True)  # {test_name: result, ...}
    doctor_notes = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='medical_exams_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['certificate_expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name} - Medical ({self.medical_exam_id})"
    
    @property
    def is_expired(self):
        """Check if certificate is expired"""
        if not self.certificate_expiry_date:
            return False
        return self.certificate_expiry_date < timezone.now().date()
    
    @property
    def days_until_expiry(self):
        """Days remaining until expiry"""
        if not self.certificate_expiry_date:
            return None
        delta = self.certificate_expiry_date - timezone.now().date()
        return delta.days