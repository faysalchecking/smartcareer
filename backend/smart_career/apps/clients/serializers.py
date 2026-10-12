from rest_framework import serializers
from .models import Client
from django.contrib.auth.models import User

class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class ClientSerializer(serializers.ModelSerializer):
    assigned_user = UserMinimalSerializer(read_only=True)
    assigned_user_id = serializers.IntegerField(write_only=True, required=False)
    
    open_jobs = serializers.SerializerMethodField()
    total_deployed = serializers.SerializerMethodField()
    outstanding_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'client_id', 'company_name', 'industry',
            'contact_person', 'email', 'phone', 'alternative_phone',
            'address', 'city', 'country', 'postal_code',
            'registration_number', 'tax_id',
            'payment_terms', 'credit_limit', 'currency',
            'status', 'assigned_user', 'assigned_user_id',
            'contract_start', 'contract_end',
            'notes', 'created_at', 'updated_at',
            'open_jobs', 'total_deployed', 'outstanding_balance'
        ]
        read_only_fields = ['client_id', 'created_at', 'updated_at']
    
    def get_open_jobs(self, obj):
        from smart_career.apps.jobs.models import Job
        return Job.objects.filter(
            employer=obj,
            status__in=['OPEN', 'ACTIVE']
        ).count()
    
    def get_total_deployed(self, obj):
        from smart_career.apps.deployment.models import Deployment
        return Deployment.objects.filter(
            employer=obj,
            status='DEPLOYED'
        ).count()
    
    def get_outstanding_balance(self, obj):
        from smart_career.apps.finance.models import Invoice
        from django.db.models import Sum
        invoices = Invoice.objects.filter(client=obj)
        total_invoiced = invoices.aggregate(Sum('total'))['total__sum'] or 0
        total_paid = invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        return total_invoiced - total_paid
    
    def create(self, validated_data):
        assigned_user_id = validated_data.pop('assigned_user_id', None)
        client = Client.objects.create(**validated_data)
        if assigned_user_id:
            client.assigned_user_id = assigned_user_id
            client.save()
        return client

class ClientListSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.SerializerMethodField()
    
    class Meta:
        model = Client
        fields = [
            'id', 'client_id', 'company_name', 'country',
            'contact_person', 'email', 'status',
            'outstanding_balance'
        ]
    
    def get_outstanding_balance(self, obj):
        from smart_career.apps.finance.models import Invoice
        from django.db.models import Sum
        invoices = Invoice.objects.filter(client=obj)
        total_invoiced = invoices.aggregate(Sum('total'))['total__sum'] or 0
        total_paid = invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        return total_invoiced - total_paid