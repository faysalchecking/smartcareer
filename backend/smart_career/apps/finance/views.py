from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Q
from django.utils import timezone
from .models import (
    ServiceCatalog, Vendor, Purchase, Sale, Invoice,
    Payment, Expense, Commission, TaxConfig, LedgerEntry, BankAccount
)
from .serializers import (
    ServiceCatalogSerializer, VendorSerializer, PurchaseSerializer,
    PurchaseListSerializer, SaleSerializer, InvoiceSerializer,
    InvoiceListSerializer, PaymentSerializer, ExpenseSerializer,
    CommissionSerializer, TaxConfigSerializer, LedgerEntrySerializer,
    BankAccountSerializer
)

class ServiceCatalogViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ServiceCatalog.objects.filter(is_active=True)
    serializer_class = ServiceCatalogSerializer

class VendorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Vendor.objects.filter(status='ACTIVE')
    serializer_class = VendorSerializer
    
    @action(detail=True, methods=['get'])
    def purchases(self, request, pk=None):
        vendor = self.get_object()
        purchases = Purchase.objects.filter(vendor=vendor)
        serializer = PurchaseListSerializer(purchases, many=True)
        return Response(serializer.data)

class PurchaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Purchase.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseListSerializer
        return PurchaseSerializer
    
    @action(detail=True, methods=['post'])
    def mark_received(self, request, pk=None):
        purchase = self.get_object()
        purchase.status = 'RECEIVED'
        purchase.received_date = timezone.now().date()
        purchase.save()
        return Response(PurchaseSerializer(purchase).data)

class SaleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Invoice.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    @action(detail=True, methods=['get'])
    def by_client(self, request, pk=None):
        from smart_career.apps.clients.models import Client
        client = Client.objects.get(pk=pk)
        invoices = Invoice.objects.filter(client=client)
        serializer = InvoiceListSerializer(invoices, many=True)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        expense = self.get_object()
        expense.is_approved = True
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.save()
        return Response(ExpenseSerializer(expense).data)

class CommissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    
    @action(detail=True, methods=['get'])
    def by_agent(self, request, agent_id):
        from smart_career.apps.agents.models import Agent
        agent = Agent.objects.get(pk=agent_id)
        commissions = Commission.objects.filter(agent=agent)
        serializer = CommissionSerializer(commissions, many=True)
        return Response(serializer.data)

class TaxConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = TaxConfig.objects.filter(is_active=True)
    serializer_class = TaxConfigSerializer

class LedgerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = LedgerEntry.objects.all()
    serializer_class = LedgerEntrySerializer
    
    @action(detail=False, methods=['get'])
    def by_reference(self, request):
        ref_type = request.query_params.get('ref_type')
        ref_id = request.query_params.get('ref_id')
        
        entries = LedgerEntry.objects.filter(
            reference_type=ref_type,
            reference_id=ref_id
        )
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

class BankAccountViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = BankAccount.objects.filter(is_active=True)
    serializer_class = BankAccountSerializer