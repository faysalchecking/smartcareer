from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Client
from .serializers import ClientSerializer, ClientListSerializer

class ClientViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClientListSerializer
        return ClientSerializer
    
    @action(detail=True, methods=['get'])
    def jobs(self, request, pk=None):
        """Get all jobs for a client"""
        from smart_career.apps.jobs.models import Job
        from smart_career.apps.jobs.serializers import JobListSerializer
        
        client = self.get_object()
        jobs = Job.objects.filter(employer=client)
        
        serializer = JobListSerializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Get all invoices for a client"""
        try:
            from smart_career.apps.finance.models import Invoice
            from smart_career.apps.finance.serializers import InvoiceListSerializer
            
            client = self.get_object()
            invoices = Invoice.objects.filter(client=client)
            
            serializer = InvoiceListSerializer(invoices, many=True)
            return Response(serializer.data)
        except ImportError:
            return Response({'error': 'Finance module not available'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get client statistics"""
        from smart_career.apps.jobs.models import Job
        
        client = self.get_object()
        
        return Response({
            'open_jobs': Job.objects.filter(employer=client, status='OPEN').count(),
            'active_jobs': Job.objects.filter(employer=client, status='ACTIVE').count(),
            'payment_terms': client.payment_terms,
            'currency': client.currency,
        })