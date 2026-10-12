from django.db import models
from django.contrib.auth.models import User
from smart_career.apps.candidates.models import Candidate
from smart_career.apps.jobs.models import Job
from smart_career.apps.agents.models import Agent
from smart_career.apps.clients.models import Client

class AgentPortalAccess(models.Model):
    """Track agent portal login and activity"""
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='portal_accesses'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'agent_portal_accesses'
        unique_together = ['agent', 'user']


class ClientPortalAccess(models.Model):
    """Track client portal login and activity"""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='portal_accesses'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'client_portal_accesses'
        unique_together = ['client', 'user']


class SharedDocument(models.Model):
    """Track documents shared with clients"""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='shared_documents'
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE
    )
    
    shared_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    
    shared_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'shared_documents'
        unique_together = ['client', 'document']