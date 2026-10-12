from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BLOCKED', 'Blocked'),
    ]
    
    PAYMENT_TERM_CHOICES = [
        ('ADVANCE', 'Advance'),
        ('ON_PLACEMENT', 'On Placement'),
        ('ON_COMPLETION', 'On Completion'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    ]
    
    client_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Basic info
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
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
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    
    # Financial
    payment_terms = models.CharField(
        max_length=20,
        choices=PAYMENT_TERM_CHOICES,
        default='ON_PLACEMENT'
    )
    credit_limit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Maximum credit allowed"
    )
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text="Default currency for transactions"
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
        related_name='client_profile'
    )
    
    # Contract
    contract_start = models.DateField(null=True, blank=True)
    contract_end = models.DateField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'clients'
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['country']),
        ]
    
    def __str__(self):
        return f"{self.client_id} - {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.client_id:
            count = Client.objects.count() + 1
            self.client_id = f"CLT-{count:05d}"
        super().save(*args, **kwargs)