from django.db import models
from django.utils import timezone

class VisaType(models.Model):
    """Visa type configuration"""
    
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    processing_days = models.IntegerField(default=30)
    validity_months = models.IntegerField(default=24)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.country}"


class VisaApplication(models.Model):
    """Visa application record"""
    
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('PREPARING', 'Preparing Documents'),
        ('SUBMITTED', 'Submitted'),
        ('PROCESSING', 'Processing'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Relationships
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='visa_applications')
    job = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True)
    visa_type = models.ForeignKey(VisaType, on_delete=models.PROTECT)
    
    # Application details
    visa_app_id = models.CharField(max_length=20, unique=True, db_index=True)
    application_number = models.CharField(max_length=100, null=True, blank=True)
    
    # Timeline
    application_date = models.DateField(null=True, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(null=True, blank=True)
    visa_issue_date = models.DateField(null=True, blank=True)
    visa_expiry_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    
    # Sponsor
    sponsor_company = models.CharField(max_length=255, null=True, blank=True)
    sponsor_contact = models.CharField(max_length=255, null=True, blank=True)
    
    # Documents
    documents = models.JSONField(null=True, blank=True)  # List of required documents
    
    # Details
    remarks = models.TextField(null=True, blank=True)
    assigned_officer = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='visa_apps_assigned')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submission_date']
        unique_together = [['candidate', 'job']]
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['visa_type', 'status']),
            models.Index(fields=['visa_expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.visa_type.name}"
    
    @property
    def is_expired(self):
        if not self.visa_expiry_date:
            return False
        return self.visa_expiry_date < timezone.now().date()
    
    @property
    def days_pending(self):
        """Days since submission"""
        if not self.submission_date:
            return None
        delta = timezone.now().date() - self.submission_date
        return delta.days


class EmbassyClearance(models.Model):
    """Embassy clearance/approval record"""
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('SUBMITTED', 'Submitted'),
        ('PROCESSING', 'Processing'),
        ('CLEARED', 'Cleared'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Relationships
    visa_application = models.OneToOneField(VisaApplication, on_delete=models.CASCADE, related_name='embassy_clearance')
    
    # Timeline
    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.TimeField(null=True, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    clearance_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    
    # Details
    passport_submitted = models.BooleanField(default=False)
    passport_submission_date = models.DateField(null=True, blank=True)
    passport_return_date = models.DateField(null=True, blank=True)
    
    result = models.CharField(
        max_length=20,
        choices=[('APPROVED', 'Approved'), ('REJECTED', 'Rejected')],
        null=True, blank=True
    )
    
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Embassy - {self.visa_application.candidate.full_name}"


class Ticket(models.Model):
    """Flight ticket record"""
    
    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('CONFIRMED', 'Confirmed'),
        ('TICKET_ISSUED', 'Ticket Issued'),
        ('CHECKED_IN', 'Checked In'),
        ('TRAVELLED', 'Travelled'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Relationships
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='tickets')
    job = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Ticket details
    ticket_id = models.CharField(max_length=20, unique=True, db_index=True)
    pnr = models.CharField(max_length=10, null=True, blank=True)  # Passenger Name Record
    ticket_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Flight details
    airline = models.CharField(max_length=255)
    flight_number = models.CharField(max_length=10)
    
    # Journey
    departure_airport = models.CharField(max_length=10)  # IATA code
    arrival_airport = models.CharField(max_length=10)
    departure_date = models.DateField()
    departure_time = models.TimeField(null=True, blank=True)
    arrival_date = models.DateField(null=True, blank=True)
    arrival_time = models.TimeField(null=True, blank=True)
    
    # Cost
    ticket_cost = models.DecimalField(max_digits=12, decimal_places=2)
    ticket_sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='BOOKED')
    
    # Ticket file
    ticket_file = models.FileField(upload_to='tickets/%Y/%m/%d/', null=True, blank=True)
    
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-departure_date']
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['departure_date']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.flight_number}"


class Deployment(models.Model):
    """Candidate deployment record"""
    
    STATUS_CHOICES = [
        ('READY', 'Ready'),
        ('TICKETED', 'Ticketed'),
        ('TRAVELLING', 'Travelling'),
        ('ARRIVED', 'Arrived'),
        ('DEPLOYED', 'Deployed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Relationships
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='deployments')
    ticket = models.OneToOneField(Ticket, on_delete=models.SET_NULL, null=True, blank=True, related_name='deployment')
    employer = models.ForeignKey('jobs.Employer', on_delete=models.CASCADE)
    job = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Deployment details
    deployment_id = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Timeline
    deployment_date = models.DateField()
    arrival_date = models.DateField(null=True, blank=True)
    onboarding_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='READY')
    
    # Details
    position = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    
    # Contact at destination
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    accommodation_address = models.TextField(null=True, blank=True)
    
    remarks = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-deployment_date']
        indexes = [
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['employer', 'status']),
            models.Index(fields=['deployment_date']),
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.employer.company_name}"