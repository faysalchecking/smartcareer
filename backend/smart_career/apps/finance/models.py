from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from decimal import Decimal

class ServiceCatalog(models.Model):
    """Products/Services we offer"""
    SERVICE_CATEGORY_CHOICES = [
        ('RECRUITMENT', 'Recruitment Service'),
        ('VISA', 'Visa Processing'),
        ('MEDICAL', 'Medical Examination'),
        ('TRAINING', 'Training'),
        ('TICKET', 'Ticket Booking'),
        ('ACCOMMODATION', 'Accommodation'),
        ('TRANSPORTATION', 'Transportation'),
        ('DOCUMENTATION', 'Documentation'),
        ('OTHER', 'Other Service'),
    ]
    
    service_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=50,
        choices=SERVICE_CATEGORY_CHOICES
    )
    
    # Pricing
    default_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Standard cost for this service"
    )
    default_sale_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Standard sale price"
    )
    currency = models.CharField(max_length=3, default='BDT')
    
    # Tax
    is_taxable = models.BooleanField(default=True)
    tax_category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Tax classification"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'service_catalog'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.service_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.service_id:
            count = ServiceCatalog.objects.count() + 1
            self.service_id = f"SRV-{count:05d}"
        super().save(*args, **kwargs)


class Vendor(models.Model):
    """Suppliers/Vendors we buy from"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('BLOCKED', 'Blocked'),
    ]
    
    vendor_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    
    # Business info
    registration_number = models.CharField(max_length=100, blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    
    # Payment terms
    payment_terms = models.CharField(
        max_length=100,
        default='30 days',
        help_text="Payment due period"
    )
    
    # Services provided
    services = models.ManyToManyField(
        ServiceCatalog,
        blank=True,
        related_name='vendors'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vendors'
        ordering = ['company_name']
    
    def __str__(self):
        return f"{self.vendor_id} - {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.vendor_id:
            count = Vendor.objects.count() + 1
            self.vendor_id = f"VND-{count:05d}"
        super().save(*args, **kwargs)


class Purchase(models.Model):
    """Purchase orders/invoices from vendors"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ORDERED', 'Ordered'),
        ('RECEIVED', 'Received'),
        ('PAID', 'Paid'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    purchase_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Vendor
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='purchases'
    )
    
    # Reference
    candidate = models.ForeignKey(
        'candidates.Candidate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchases'
    )
    
    # Service
    service = models.ForeignKey(
        ServiceCatalog,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Dates
    purchase_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)
    
    # Amount
    quantity = models.IntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    currency = models.CharField(max_length=3, default='BDT')
    
    # Payment
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    
    # Reference
    vendor_invoice_number = models.CharField(max_length=100, blank=True)
    reference_notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_purchases'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'purchases'
        ordering = ['-purchase_date']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['purchase_date']),
        ]
    
    def __str__(self):
        return f"{self.purchase_id} - {self.vendor.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.purchase_id:
            from datetime import datetime
            count = Purchase.objects.count() + 1
            self.purchase_id = f"PUR-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        # Calculate totals
        self.subtotal = Decimal(self.quantity) * self.unit_cost
        self.total_cost = self.subtotal + self.tax_amount
        
        super().save(*args, **kwargs)
    
    @property
    def outstanding(self):
        return self.total_cost - self.paid_amount
    
    @property
    def is_fully_paid(self):
        return self.outstanding <= 0


class Sale(models.Model):
    """Sales to customers (clients)"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('INVOICED', 'Invoiced'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    sale_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Customer
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='sales'
    )
    
    # Reference
    candidate = models.ForeignKey(
        'candidates.Candidate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sales'
    )
    
    # Service
    service = models.ForeignKey(
        ServiceCatalog,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Dates
    sale_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Amount
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    currency = models.CharField(max_length=3, default='BDT')
    
    # Payment
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    
    # Reference
    reference_notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sales'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales'
        ordering = ['-sale_date']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['sale_date']),
        ]
    
    def __str__(self):
        return f"{self.sale_id} - {self.client.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.sale_id:
            from datetime import datetime
            count = Sale.objects.count() + 1
            self.sale_id = f"SAL-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        # Calculate totals
        self.subtotal = Decimal(self.quantity) * self.unit_price
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        super().save(*args, **kwargs)
    
    @property
    def outstanding(self):
        return self.total_amount - self.paid_amount
    
    @property
    def is_fully_paid(self):
        return self.outstanding <= 0


class Invoice(models.Model):
    """Customer invoices"""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    invoice_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Customer
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    # Items
    sales = models.ManyToManyField(
        Sale,
        related_name='invoices'
    )
    
    # Dates
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    sent_date = models.DateTimeField(null=True, blank=True)
    
    # Amount
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Payment
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    
    # Reference
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invoices'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'invoices'
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['invoice_date']),
        ]
    
    def __str__(self):
        return f"{self.invoice_id} - {self.client.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_id:
            from datetime import datetime
            count = Invoice.objects.count() + 1
            self.invoice_id = f"INV-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def outstanding(self):
        return self.total - self.paid_amount


class Payment(models.Model):
    """Payment records"""
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Transfer'),
        ('CHECK', 'Check'),
        ('CARD', 'Card'),
        ('MFS', 'Mobile Financial Service'),
        ('OTHER', 'Other'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('INVOICE', 'Invoice Payment'),
        ('PURCHASE', 'Purchase Payment'),
        ('ADVANCE', 'Advance Payment'),
        ('REFUND', 'Refund'),
        ('ADJUSTMENT', 'Adjustment'),
    ]
    
    payment_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Type
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES
    )
    
    # Related entity
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payments'
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='payments'
    )
    
    # Amount
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    
    # Method
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Check/TXN/Reference number"
    )
    
    # Dates
    payment_date = models.DateField()
    received_date = models.DateField(null=True, blank=True)
    
    # User
    received_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_payments'
    )
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_type', 'payment_date']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"{self.payment_id} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            from datetime import datetime
            count = Payment.objects.count() + 1
            self.payment_id = f"PAY-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        super().save(*args, **kwargs)


class Expense(models.Model):
    """Operating expenses"""
    EXPENSE_CATEGORY_CHOICES = [
        ('OFFICE', 'Office'),
        ('SALARIES', 'Salaries'),
        ('UTILITIES', 'Utilities'),
        ('MARKETING', 'Marketing'),
        ('TRAVEL', 'Travel'),
        ('COMMUNICATIONS', 'Communications'),
        ('EQUIPMENT', 'Equipment'),
        ('LEGAL', 'Legal & Compliance'),
        ('OTHER', 'Other'),
    ]
    
    expense_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    category = models.CharField(
        max_length=50,
        choices=EXPENSE_CATEGORY_CHOICES
    )
    description = models.CharField(max_length=255)
    
    # Amount
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='BDT')
    
    # Date
    expense_date = models.DateField()
    
    # Reference
    vendor_name = models.CharField(max_length=255, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_expenses'
    )
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_expenses'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expenses'
        ordering = ['-expense_date']
        indexes = [
            models.Index(fields=['category', 'expense_date']),
        ]
    
    def __str__(self):
        return f"{self.expense_id} - {self.description}"
    
    def save(self, *args, **kwargs):
        if not self.expense_id:
            from datetime import datetime
            count = Expense.objects.count() + 1
            self.expense_id = f"EXP-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        super().save(*args, **kwargs)


class Commission(models.Model):
    """Agent commissions"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    commission_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Agent
    agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.CASCADE,
        related_name='commissions'
    )
    
    # Reference
    candidate = models.ForeignKey(
        'candidates.Candidate',
        on_delete=models.SET_NULL,
        null=True,
        related_name='commissions'
    )
    job = models.ForeignKey(
        'jobs.Job',
        on_delete=models.SET_NULL,
        null=True,
        related_name='commissions'
    )
    sale = models.ForeignKey(
        Sale,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commissions'
    )
    
    # Calculation
    base_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Amount on which commission is calculated"
    )
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Commission percentage"
    )
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Currency
    currency = models.CharField(max_length=3, default='BDT')
    
    # Period
    from_date = models.DateField()
    to_date = models.DateField()
    
    # Payment
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    payment_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_commissions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'commissions'
        ordering = ['-from_date']
        indexes = [
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['from_date']),
        ]
    
    def __str__(self):
        return f"{self.commission_id} - {self.agent.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.commission_id:
            from datetime import datetime
            count = Commission.objects.count() + 1
            self.commission_id = f"COM-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        # Auto-calculate commission amount
        if not self.commission_amount:
            self.commission_amount = (self.base_amount * self.commission_rate) / 100
        
        super().save(*args, **kwargs)


class TaxConfig(models.Model):
    """Tax configuration"""
    tax_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Rate
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Tax percentage"
    )
    
    # Type
    tax_type = models.CharField(
        max_length=50,
        choices=[
            ('VAT', 'Value Added Tax'),
            ('GST', 'Goods & Services Tax'),
            ('INCOME', 'Income Tax'),
            ('WITHHOLDING', 'Withholding Tax'),
            ('OTHER', 'Other'),
        ]
    )
    
    # Scope
    is_inclusive = models.BooleanField(
        default=False,
        help_text="Is tax included in price?"
    )
    applicable_services = models.ManyToManyField(
        ServiceCatalog,
        blank=True
    )
    
    # Effective date
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tax_configs'
        ordering = ['-effective_from']
    
    def __str__(self):
        return f"{self.name} ({self.rate}%)"
    
    def save(self, *args, **kwargs):
        if not self.tax_id:
            count = TaxConfig.objects.count() + 1
            self.tax_id = f"TAX-{count:04d}"
        super().save(*args, **kwargs)


class LedgerEntry(models.Model):
    """Financial ledger for audit trail"""
    ENTRY_TYPE_CHOICES = [
        ('SALE', 'Sale'),
        ('PURCHASE', 'Purchase'),
        ('PAYMENT', 'Payment'),
        ('EXPENSE', 'Expense'),
        ('COMMISSION', 'Commission'),
        ('REFUND', 'Refund'),
        ('ADJUSTMENT', 'Adjustment'),
        ('TAX', 'Tax'),
    ]
    
    ACCOUNT_CHOICES = [
        ('RECEIVABLE', 'Accounts Receivable'),
        ('PAYABLE', 'Accounts Payable'),
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
        ('CASH', 'Cash'),
        ('BANK', 'Bank'),
        ('COMMISSION', 'Commission Expense'),
        ('TAX', 'Tax Payable'),
    ]
    
    entry_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    # Type
    entry_type = models.CharField(max_length=50, choices=ENTRY_TYPE_CHOICES)
    account = models.CharField(max_length=50, choices=ACCOUNT_CHOICES)
    
    # Reference
    reference_id = models.CharField(max_length=50)
    reference_type = models.CharField(max_length=50)
    
    # Amount
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='BDT')
    
    # Date
    transaction_date = models.DateField(db_index=True)
    
    # Description
    description = models.TextField()
    
    # Audit
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_ledger_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ledger_entries'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['reference_id', 'reference_type']),
            models.Index(fields=['account', 'transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.entry_id} - {self.entry_type}"
    
    def save(self, *args, **kwargs):
        if not self.entry_id:
            from datetime import datetime
            count = LedgerEntry.objects.count() + 1
            self.entry_id = f"LED-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        
        super().save(*args, **kwargs)


class BankAccount(models.Model):
    """Bank/Cash accounts"""
    ACCOUNT_TYPE_CHOICES = [
        ('CASH', 'Cash'),
        ('BANK', 'Bank Account'),
        ('MFS', 'Mobile Financial Service'),
        ('CREDIT_CARD', 'Credit Card'),
    ]
    
    account_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=50,
        choices=ACCOUNT_TYPE_CHOICES
    )
    
    # Bank details
    bank_name = models.CharField(max_length=255, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    routing_number = models.CharField(max_length=50, blank=True)
    
    # Balance
    opening_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    currency = models.CharField(max_length=3, default='BDT')
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank_accounts'
        ordering = ['account_name']
    
    def __str__(self):
        return f"{self.account_name} ({self.account_type})"
    
    def save(self, *args, **kwargs):
        if not self.account_id:
            count = BankAccount.objects.count() + 1
            self.account_id = f"ACC-{count:05d}"
        super().save(*args, **kwargs)