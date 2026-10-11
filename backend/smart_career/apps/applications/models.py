from django.db import models
from django.utils import timezone

class Application(models.Model):
    """Job application from candidate"""
    
    STATUS_CHOICES = [
        ('SUBMITTED', 'Submitted'),
        ('SCREENING', 'Screening'),
        ('SHORTLISTED', 'Shortlisted'),
        ('REJECTED', 'Rejected'),
        ('INTERVIEW', 'Interview'),
        ('SELECTED', 'Selected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    # Relationships
    candidate = models.ForeignKey('candidates.Candidate', on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='applications')
    
    # Application info
    application_id = models.CharField(max_length=20, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    
    # Screening
    screening_score = models.FloatField(null=True, blank=True)  # 0-100
    screening_status = models.CharField(
        max_length=50,
        choices=[('ELIGIBLE', 'Eligible'), ('INELIGIBLE', 'Ineligible'), ('MANUAL_REVIEW', 'Manual Review')],
        null=True, blank=True
    )
    screening_notes = models.TextField(null=True, blank=True)
    
    # Metadata
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    applied_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='applications_created')
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = [['candidate', 'job']]
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['candidate', 'status']),
            models.Index(fields=['screening_status']),  # ✅ NEW NAME
        ]
    
    def __str__(self):
        return f"{self.candidate.full_name} - {self.job.title}"
    
    @property
    def is_eligible_by_criteria(self):
        """Check hard eligibility criteria"""
        job = self.job
        candidate = self.candidate
        
        # Age check
        if job.age_min and candidate.age < job.age_min:
            return False
        if job.age_max and candidate.age > job.age_max:
            return False
        
        # Experience check
        if job.experience_years:
            # Parse experience from text (simplified)
            try:
                import re
                match = re.search(r'(\d+)', candidate.experience)
                exp = int(match.group(1)) if match else 0
                if exp < job.experience_years:
                    return False
            except:
                pass
        
        # Passport validity
        if job.passport_validity_months:
            if candidate.passport_validity_days < (job.passport_validity_months * 30):
                return False
        
        return True


class ScreeningQuestion(models.Model):
    """Screening questions for a job"""
    
    QUESTION_TYPE_CHOICES = [
        ('TEXT', 'Text Answer'),
        ('MULTIPLE_CHOICE', 'Multiple Choice'),
        ('YES_NO', 'Yes/No'),
        ('FILE_UPLOAD', 'File Upload'),
    ]
    
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='screening_questions')
    question_number = models.IntegerField()
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='TEXT')
    is_required = models.BooleanField(default=True)
    
    # For multiple choice
    options = models.JSONField(null=True, blank=True)  # ["Option 1", "Option 2", ...]
    
    # Scoring
    points = models.IntegerField(default=0)  # Points for correct answer
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['job', 'question_number']
        unique_together = [['job', 'question_number']]
    
    def __str__(self):
        return f"{self.job.title} - Q{self.question_number}"


class ScreeningAnswer(models.Model):
    """Candidate's answer to screening question"""
    
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='screening_answers')
    question = models.ForeignKey(ScreeningQuestion, on_delete=models.CASCADE)
    
    # Answer
    answer_text = models.TextField(null=True, blank=True)
    answer_file = models.FileField(upload_to='screening_answers/%Y/%m/%d/', null=True, blank=True)
    answer_selected = models.CharField(max_length=255, null=True, blank=True)  # For multiple choice
    
    # Scoring
    score = models.IntegerField(default=0)
    is_correct = models.BooleanField(null=True, blank=True)
    
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['application', 'question']]
    
    def __str__(self):
        return f"{self.application.candidate.full_name} - {self.question.question_text[:50]}"


class ScreeningResult(models.Model):
    """AI/Manual screening result"""
    
    RESULT_CHOICES = [
        ('ELIGIBLE', 'Eligible'),
        ('INELIGIBLE', 'Ineligible'),
        ('MANUAL_REVIEW', 'Manual Review Required'),
    ]
    
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='screening_result_data')
    
    # Hard criteria
    hard_criteria_passed = models.BooleanField()
    
    # Scoring
    total_score = models.FloatField()  # 0-100
    screening_questions_score = models.FloatField(default=0)
    ai_match_score = models.FloatField(default=0)
    
    # Result
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    reasoning = models.TextField()
    
    # AI confidence
    ai_confidence = models.FloatField(default=0)  # 0-1
    
    # Manual review
    reviewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.application} - {self.result}"


class Shortlist(models.Model):
    """Shortlisted candidates for interview"""
    
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='shortlists')
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='shortlist')
    
    # Shortlist info
    shortlist_date = models.DateTimeField(auto_now_add=True)
    shortlist_reason = models.TextField()
    interview_scheduled = models.BooleanField(default=False)
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_location = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata
    shortlisted_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='shortlists_created')
    
    class Meta:
        ordering = ['-shortlist_date']
        unique_together = [['job', 'application']]
    
    def __str__(self):
        return f"{self.application.candidate.full_name} - {self.job.title}"