from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Alert, AlertRule, AlertEscalation
from .serializers import AlertSerializer, AlertListSerializer, AlertRuleSerializer

class AlertViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Alert.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AlertListSerializer
        return AlertSerializer
    
    def get_queryset(self):
        # Users see alerts assigned to them or critical ones
        return Alert.objects.filter(
            Q(assigned_to=self.request.user) | Q(severity='CRITICAL')
        )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active unacknowledged alerts"""
        queryset = self.get_queryset().filter(
            is_active=True,
            is_acknowledged=False
        ).order_by('-severity', '-alert_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        alert.is_acknowledged = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response(AlertSerializer(alert).data)
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate an alert"""
        alert = self.get_object()
        next_level = request.data.get('level', 2)
        escalated_to_id = request.data.get('escalated_to_id')
        
        if not escalated_to_id:
            return Response(
                {'error': 'escalated_to_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        escalation = AlertEscalation.objects.create(
            alert=alert,
            level=next_level,
            escalated_to_id=escalated_to_id
        )
        
        return Response(
            {'message': 'Alert escalated'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get alert statistics"""
        queryset = self.get_queryset().filter(is_active=True)
        
        return Response({
            'total_active': queryset.count(),
            'critical': queryset.filter(severity='CRITICAL').count(),
            'high': queryset.filter(severity='HIGH').count(),
            'unacknowledged': queryset.filter(is_acknowledged=False).count(),
        })


class AlertRuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    
    def get_queryset(self):
        # Only show active rules
        return AlertRule.objects.filter(is_active=True)