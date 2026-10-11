from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskListSerializer, TaskCommentSerializer

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def get_queryset(self):
        # Users only see their own tasks
        return Task.objects.filter(assigned_to=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get current user's tasks"""
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        
        queryset = self.get_queryset()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        queryset = queryset.order_by('-priority', 'due_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get tasks due today"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            due_date__date=today,
            status__in=['PENDING', 'IN_PROGRESS']
        ).order_by('-priority')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        queryset = self.get_queryset().filter(
            status='OVERDUE'
        ).order_by('-priority')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark task as complete"""
        task = self.get_object()
        task.status = 'COMPLETED'
        task.completed_at = timezone.now()
        task.completed_notes = request.data.get('notes', '')
        task.save()
        
        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to task"""
        task = self.get_object()
        comment_text = request.data.get('comment')
        
        if not comment_text:
            return Response(
                {'error': 'Comment is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = TaskComment.objects.create(
            task=task,
            user=request.user,
            comment=comment_text
        )
        
        return Response(
            TaskCommentSerializer(comment).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics"""
        queryset = self.get_queryset()
        
        return Response({
            'total': queryset.count(),
            'pending': queryset.filter(status='PENDING').count(),
            'in_progress': queryset.filter(status='IN_PROGRESS').count(),
            'completed': queryset.filter(status='COMPLETED').count(),
            'overdue': queryset.filter(status='OVERDUE').count(),
            'critical': queryset.filter(priority='CRITICAL').count(),
        })