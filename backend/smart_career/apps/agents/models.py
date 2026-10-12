from django.db import models
from django.contrib.auth.models import User

class Agent(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('BLOCKED', 'Blocked'),
    ]
    
    agent_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Basic info
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    
    # Business info
    license_number = models.CharField(max_length=100, unique=True)
    license_expiry = models.DateField()
    agreement_date = models.DateField()
    
    # Financial
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00,
        help_text="Commission percentage"
    )
    payment_terms = models.CharField(
        max_length=100,
        default='Monthly',
        help_text="Payment frequency"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    
    # Relationships
    assigned_user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='agent_profile'
    )
    
    # Metadata
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'agents'
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.agent_id} - {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.agent_id:
            count = Agent.objects.count() + 1
            self.agent_id = f"AGT-{count:05d}"
        super().save(*args, **kwargs)