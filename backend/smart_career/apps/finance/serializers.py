from rest_framework import serializers
from .models import (
    ServiceCatalog, Vendor, Purchase, Sale, Invoice,
    Payment, Expense, Commission, TaxConfig, LedgerEntry, BankAccount
)
from django.contrib.auth.models import User

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

# SERVICE CATALOG
class ServiceCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCatalog
        fields = [
            'id', 'service_id', 'name', 'description', 'category',
            'default_cost', 'default_sale_price', 'currency',
            'is_taxable', 'tax_category', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['service_id']

# VENDOR
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'id', 'vendor_id', 'company_name', 'contact_person',
            'email', 'phone', 'address', 'city', 'country',
            'registration_number', 'tax_id', 'payment_terms',
            'status', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['vendor_id']

# PURCHASE
class PurchaseSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    outstanding = serializers.SerializerMethodField()
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'purchase_id', 'vendor', 'vendor_name', 'service', 'service_name',
            'candidate', 'job', 'purchase_date', 'due_date', 'received_date',
            'quantity', 'unit_cost', 'subtotal', 'tax_amount', 'total_cost',
            'currency', 'paid_amount', 'status', 'vendor_invoice_number',
            'reference_notes', 'created_by', 'created_at', 'updated_at',
            'outstanding'
        ]
        read_only_fields = ['purchase_id', 'subtotal', 'total_cost']
    
    def get_outstanding(self, obj):
        return obj.outstanding

class PurchaseListSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.company_name', read_only=True)
    
    class Meta:
        model = Purchase
        fields = [
            'id', 'purchase_id', 'vendor_name', 'purchase_date',
            'total_cost', 'paid_amount', 'status'
        ]

# SALE
class SaleSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    outstanding = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'sale_id', 'client', 'client_name', 'service', 'service_name',
            'candidate', 'job', 'sale_date', 'due_date',
            'quantity', 'unit_price', 'subtotal', 'tax_amount', 'discount_amount',
            'total_amount', 'currency', 'paid_amount', 'status',
            'reference_notes', 'created_by', 'created_at', 'updated_at',
            'outstanding', 'profit_margin'
        ]
        read_only_fields = ['sale_id', 'subtotal', 'total_amount']
    
    def get_outstanding(self, obj):
        return obj.outstanding
    
    def get_profit_margin(self, obj):
        # Will calculate from related purchase
        return 0

# INVOICE
class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    outstanding = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_id', 'client', 'client_name',
            'invoice_date', 'due_date', 'sent_date',
            'subtotal', 'tax_amount', 'discount_amount', 'total',
            'paid_amount', 'status', 'notes',
            'created_by', 'created_at', 'updated_at',
            'outstanding'
        ]
        read_only_fields = ['invoice_id']
    
    def get_outstanding(self, obj):
        return obj.outstanding

class InvoiceListSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.company_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_id', 'client_name', 'invoice_date',
            'total', 'paid_amount', 'status'
        ]

# PAYMENT
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_id', 'payment_type', 'invoice', 'purchase',
            'amount', 'currency', 'payment_method', 'reference_number',
            'payment_date', 'received_date', 'received_by', 'notes',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['payment_id']

# EXPENSE
class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_id', 'category', 'description', 'amount',
            'currency', 'expense_date', 'vendor_name', 'reference_number',
            'is_approved', 'approved_by', 'approved_at',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['expense_id']

# COMMISSION
class CommissionSerializer(serializers.ModelSerializer):
    agent_name = serializers.CharField(source='agent.company_name', read_only=True)
    outstanding = serializers.SerializerMethodField()
    
    class Meta:
        model = Commission
        fields = [
            'id', 'commission_id', 'agent', 'agent_name',
            'candidate', 'job', 'sale',
            'base_amount', 'commission_rate', 'commission_amount',
            'currency', 'from_date', 'to_date', 'paid_amount', 'payment_date',
            'status', 'created_by', 'created_at', 'updated_at',
            'outstanding'
        ]
        read_only_fields = ['commission_id']
    
    def get_outstanding(self, obj):
        return obj.commission_amount - obj.paid_amount

# TAX CONFIG
class TaxConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxConfig
        fields = [
            'id', 'tax_id', 'name', 'description', 'rate', 'tax_type',
            'is_inclusive', 'effective_from', 'effective_to', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['tax_id']

# LEDGER
class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = [
            'id', 'entry_id', 'entry_type', 'account',
            'reference_id', 'reference_type',
            'debit', 'credit', 'balance', 'currency',
            'transaction_date', 'description',
            'created_by', 'created_at'
        ]
        read_only_fields = ['entry_id']

# BANK ACCOUNT
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            'id', 'account_id', 'account_name', 'account_type',
            'bank_name', 'account_number', 'routing_number',
            'opening_balance', 'current_balance', 'currency',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['account_id']