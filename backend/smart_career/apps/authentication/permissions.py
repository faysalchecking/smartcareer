from rest_framework import permissions
from django.contrib.auth.models import User
from smart_career.apps.common.models import AuditLog

class IsAuthenticated(permissions.BasePermission):
    """Custom authenticated check"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class HasCandidatePermission(permissions.BasePermission):
    """Check candidate view/edit permission"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has candidate module access
        # Admin/Manager can access all
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user has permission
        return request.user.has_perm('candidates.view_candidate')
    
    def has_object_permission(self, request, view, obj):
        # Admin can access all
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Agent can only see their own candidates
        if hasattr(obj, 'agent') and obj.agent:
            if obj.agent.id == request.user.id:
                return True
        
        # Recruiter can only see assigned candidates
        if hasattr(obj, 'recruiter') and obj.recruiter:
            if obj.recruiter.id == request.user.id:
                return True
        
        return False

class HasJobPermission(permissions.BasePermission):
    """Check job view/edit permission"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        return request.user.has_perm('jobs.view_job')

class HasDocumentPermission(permissions.BasePermission):
    """Check document access permission"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        return request.user.has_perm('documents.view_document')
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user can access this candidate's documents
        if hasattr(obj, 'candidate'):
            candidate = obj.candidate
            if candidate.recruiter_id == request.user.id:
                return True
            if candidate.agent:
                if candidate.agent.id == request.user.id:
                    return True
        
        return False

class HasFinancePermission(permissions.BasePermission):
    """Check finance access permission"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        return request.user.has_perm('finance.view_invoice')

class CanApproveFinance(permissions.BasePermission):
    """Check if user can approve financial operations"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        return request.user.has_perm('finance.approve_invoice')