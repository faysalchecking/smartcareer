from django.db import models
from django.contrib.auth.models import User
from smart_career.apps.candidates.models import Candidate
from smart_career.apps.jobs.models import Job

class AIProvider(models.Model):
    """AI service provider configuration"""
    PROVIDER_TYPE_CHOICES = [
        ('LOCAL_OLLAMA', 'Local Ollama'),
        ('OPENAI', 'OpenAI API'),
        ('ANTHROPIC', 'Anthropic Claude'),
        ('HUGGINGFACE', 'Hugging Face'),
    ]
    
    provider_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    
    name = models.CharField(max_length=255)
    provider_type = models.CharField(
        max_length=50,
        choices=PROVIDER_TYPE_CHOICES
    )
    
    # Configuration
    api_key = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="API key for cloud providers"
    )
    base_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Base URL (e.g., http://localhost:11434 for Ollama)"
    )
    model_name = models.CharField(
        max_length=255,
        help_text="Model name (e.g., llama2, gpt-4)"
    )
    
    # Settings
    temperature = models.FloatField(
        default=0.7,
        help_text="Creativity level (0-1)"
    )
    max_tokens = models.IntegerField(
        default=2000,
        help_text="Maximum tokens in response"
    )
    
    # Status
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    # Testing
    last_tested = models.DateTimeField(null=True, blank=True)
    is_working = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_providers'
        ordering = ['-is_default', '-is_active']
    
    def __str__(self):
        return f"{self.provider_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.provider_id:
            count = AIProvider.objects.count() + 1
            self.provider_id = f"AIP-{count:04d}"
        super().save(*args, **kwargs)


class AIConversation(models.Model):
    """AI chat conversation history"""
    conversation_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_conversations'
    )
    
    # Context
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    title = models.CharField(max_length=255, blank=True)
    
    # Provider used
    provider = models.ForeignKey(
        AIProvider,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # Metadata
    total_messages = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_conversations'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.conversation_id} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.conversation_id:
            from datetime import datetime
            count = AIConversation.objects.count() + 1
            self.conversation_id = f"AICONV-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        super().save(*args, **kwargs)


class AIMessage(models.Model):
    """Individual AI messages in conversation"""
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('ASSISTANT', 'Assistant'),
        ('SYSTEM', 'System'),
    ]
    
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )
    
    content = models.TextField()
    
    # Token usage
    tokens_used = models.IntegerField(default=0)
    
    # Tool use
    tool_calls = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON array of tool invocations"
    )
    
    # Confidence/metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context (confidence, sources, etc.)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.conversation_id} - {self.role}"


class AIToolCall(models.Model):
    """Log of AI tool invocations"""
    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('EXECUTED', 'Executed'),
        ('FAILED', 'Failed'),
        ('DENIED', 'Denied'),
    ]
    
    tool_call_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    
    message = models.ForeignKey(
        AIMessage,
        on_delete=models.CASCADE,
        related_name='tool_invocations'
    )
    
    tool_name = models.CharField(max_length=100)
    tool_description = models.TextField(blank=True)
    
    # Parameters
    parameters = models.JSONField(
        default=dict,
        help_text="Tool parameters"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REQUESTED'
    )
    
    # Result
    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Tool execution result"
    )
    error_message = models.TextField(blank=True)
    
    # Security
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_ai_tool_calls'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ai_tool_calls'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tool_call_id} - {self.tool_name}"
    
    def save(self, *args, **kwargs):
        if not self.tool_call_id:
            from datetime import datetime
            count = AIToolCall.objects.count() + 1
            self.tool_call_id = f"AITC-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        super().save(*args, **kwargs)


class AIJob(models.Model):
    """AI background jobs (CV generation, matching, etc.)"""
    JOB_TYPE_CHOICES = [
        ('CV_GENERATION', 'CV Generation'),
        ('JOB_MATCHING', 'Job Matching'),
        ('DOCUMENT_ANALYSIS', 'Document Analysis'),
        ('CANDIDATE_SUMMARY', 'Candidate Summary'),
        ('SCREENING', 'Candidate Screening'),
        ('SEARCH', 'Smart Search'),
        ('REPORT_GENERATION', 'Report Generation'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    # FIX: Renamed from job_id to ai_job_id to avoid clash
    ai_job_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        editable=False
    )
    
    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPE_CHOICES
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_jobs'
    )
    
    # Reference
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Input parameters
    input_params = models.JSONField(default=dict)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Result
    result = models.JSONField(
        null=True,
        blank=True,
        help_text="Job result/output"
    )
    error_message = models.TextField(blank=True)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['user', 'job_type']),
        ]
    
    def __str__(self):
        return f"{self.ai_job_id} - {self.job_type}"
    
    def save(self, *args, **kwargs):
        if not self.ai_job_id:
            from datetime import datetime
            count = AIJob.objects.count() + 1
            self.ai_job_id = f"AIJOB-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        super().save(*args, **kwargs)

class AILog(models.Model):
    """Audit log for all AI activities"""
    ACTIVITY_CHOICES = [
        ('CONVERSATION', 'Conversation'),
        ('TOOL_CALL', 'Tool Call'),
        ('JOB_RUN', 'Job Run'),
        ('ERROR', 'Error'),
        ('DENIAL', 'Access Denial'),
    ]
    
    log_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_logs'
    )
    
    activity_type = models.CharField(
        max_length=50,
        choices=ACTIVITY_CHOICES
    )
    
    description = models.TextField()
    
    # Reference
    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    tool_call = models.ForeignKey(
        AIToolCall,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ai_job = models.ForeignKey(
        AIJob,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Details
    details = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.log_id} - {self.activity_type}"
    
    def save(self, *args, **kwargs):
        if not self.log_id:
            from datetime import datetime
            count = AILog.objects.count() + 1
            self.log_id = f"AILOG-{datetime.now().strftime('%Y%m%d')}-{count:04d}"
        super().save(*args, **kwargs)