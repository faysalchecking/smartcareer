from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Agent
from .serializers import AgentSerializer, AgentListSerializer

class AgentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Agent.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgentListSerializer
        return AgentSerializer
    
    @action(detail=True, methods=['get'])
    def candidates(self, request, pk=None):
        """Get all candidates for an agent"""
        from smart_career.apps.candidates.models import Candidate
        from smart_career.apps.candidates.serializers import CandidateListSerializer
        
        agent = self.get_object()
        candidates = Candidate.objects.filter(agent=agent)
        
        serializer = CandidateListSerializer(candidates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get agent statistics"""
        from smart_career.apps.candidates.models import Candidate
        
        agent = self.get_object()
        candidates = Candidate.objects.filter(agent=agent)
        
        return Response({
            'total_candidates': candidates.count(),
            'available': candidates.filter(current_status='AVAILABLE').count(),
            'applied': candidates.filter(current_status='APPLIED').count(),
            'selected': candidates.filter(current_status='SELECTED').count(),
            'deployed': candidates.filter(current_status='DEPLOYED').count(),
            'commission_rate': float(agent.commission_rate),
        })