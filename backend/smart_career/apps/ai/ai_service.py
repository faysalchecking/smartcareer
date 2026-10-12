"""Main AI service"""

from .ai_provider import AIProviderFactory
from .models import (
    AIConversation, AIMessage, AIToolCall, AIJob, AILog,
    AIProvider
)
from django.utils import timezone
import json

class AIService:
    """Main AI service"""
    
    def __init__(self, user):
        self.user = user
        self.provider = self._get_active_provider()
    
    def _get_active_provider(self):
        """Get active AI provider"""
        try:
            provider = AIProvider.objects.filter(
                is_active=True
            ).first()
            
            if not provider:
                return None
            
            return AIProviderFactory.get_provider(provider)
        except Exception as e:
            print(f"Error loading AI provider: {e}")
            return None
    
    def create_conversation(self, title="", candidate=None, job=None):
        """Create new conversation"""
        conversation = AIConversation.objects.create(
            user=self.user,
            title=title,
            candidate=candidate,
            job=job,
            provider=self._get_active_provider_obj(),
        )
        return conversation
    
    def _get_active_provider_obj(self):
        """Get active provider object"""
        return AIProvider.objects.filter(is_active=True).first()
    
    def send_message(self, conversation, user_message):
        """Send message to AI"""
        if not self.provider:
            return {
                'success': False,
                'error': 'AI provider not configured',
            }
        
        # Save user message
        user_msg = AIMessage.objects.create(
            conversation=conversation,
            role='USER',
            content=user_message,
        )
        
        # Get conversation history
        messages = self._build_message_history(conversation)
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message,
        })
        
        # Get AI response
        response = self.provider.complete(messages)
        
        if not response['success']:
            # Log error
            AILog.objects.create(
                user=self.user,
                activity_type='ERROR',
                description=f"AI error: {response.get('error')}",
                details={'error': response.get('error')},
            )
            return response
        
        # Save assistant message
        assistant_msg = AIMessage.objects.create(
            conversation=conversation,
            role='ASSISTANT',
            content=response['content'],
            tokens_used=response.get('tokens_used', 0),
        )
        
        # Update conversation
        conversation.total_messages += 2
        conversation.total_tokens_used += response.get('tokens_used', 0)
        conversation.save()
        
        # Log activity
        AILog.objects.create(
            user=self.user,
            activity_type='CONVERSATION',
            description=f"Message exchange in conversation {conversation.conversation_id}",
            conversation=conversation,
        )
        
        return {
            'success': True,
            'message': assistant_msg,
            'content': response['content'],
            'tokens_used': response.get('tokens_used', 0),
        }

    
    
    def _build_message_history(self, conversation):
        """Build message history for context"""
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self._get_system_prompt(conversation),
        })
        
        # Add recent messages
        recent_messages = AIMessage.objects.filter(
            conversation=conversation
        ).order_by('-created_at')[:10]
        
        for msg in reversed(recent_messages):
            messages.append({
                "role": msg.role,
                "content": msg.content,
            })
        
        return messages
    
    def _get_system_prompt(self, conversation):
        """Build system prompt"""
        prompt = """You are SMART AI, an intelligent assistant for the SMART CAREER recruitment management system.

Your responsibilities:
- Help with candidate management and recruitment operations
- Search for candidates and jobs
- Generate CVs and match candidates to positions
- Provide financial and operational summaries
- Answer questions about the system

IMPORTANT RULES:
- Never invent or fabricate candidate data
- Never assume missing information is true
- Never bypass security or permissions
- Be honest about what you don't know
- Ask for clarification when needed
- Provide confident answers only when based on verified data

When providing information:
- State confidence level (high/medium/low)
- Cite your sources (which candidates/jobs you checked)
- Explain your reasoning
- Suggest next steps"""
        
        return prompt
    
    def test_provider(self):
        """Test AI provider connection"""
        if not self.provider:
            return {'working': False, 'error': 'No provider configured'}
        
        return self.provider.test_connection(),
def generate_cv(self, candidate_id, job_id=None, language='English'):
    """Generate CV for candidate using AI"""
    from smart_career.apps.candidates.models import Candidate
    from smart_career.apps.jobs.models import Job
    
    if not self.provider:
        return {
            'success': False,
            'error': 'AI provider not configured',
        }
    
    # Get candidate
    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        return {
            'success': False,
            'error': f'Candidate {candidate_id} not found',
        }
    
    # Get job if provided
    job = None
    if job_id:
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            pass
    
    # Create AI job record
    ai_job = AIJob.objects.create(
        user=self.user,
        job_type='CV_GENERATION',
        candidate=candidate,
        job=job,
        input_params={
            'candidate_id': candidate_id,
            'job_id': job_id,
            'language': language,
        },
        status='PROCESSING'
    )
    
    try:
        # Build CV generation prompt
        prompt = self._build_cv_prompt(candidate, job, language)
        
        # Get AI response
        messages = [
            {
                "role": "system",
                "content": "You are a professional CV writer. Generate a well-formatted, professional CV based on the provided candidate information."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self.provider.complete(messages)
        
        if not response['success']:
            ai_job.status = 'FAILED'
            ai_job.error_message = response.get('error')
            ai_job.save()
            
            AILog.objects.create(
                user=self.user,
                activity_type='ERROR',
                description=f"CV generation failed for candidate {candidate.candidate_id}",
                details={'error': response.get('error')},
                ai_job=ai_job,
            )
            
            return {
                'success': False,
                'error': response.get('error'),
            }
        
        # Save result
        ai_job.status = 'COMPLETED'
        ai_job.result = {
            'cv_content': response['content'],
            'language': language,
            'tokens_used': response.get('tokens_used', 0),
        }
        ai_job.completed_at = timezone.now()
        ai_job.save()
        
        # Log activity
        AILog.objects.create(
            user=self.user,
            activity_type='JOB_RUN',
            description=f"CV generated for candidate {candidate.candidate_id}",
            ai_job=ai_job,
        )
        
        return {
            'success': True,
            'cv_content': response['content'],
            'tokens_used': response.get('tokens_used', 0),
            'ai_job_id': ai_job.ai_job_id,
        }
    
    except Exception as e:
        ai_job.status = 'FAILED'
        ai_job.error_message = str(e)
        ai_job.save()
        
        return {
            'success': False,
            'error': str(e),
        }


def _build_cv_prompt(self, candidate, job, language):
    """Build prompt for CV generation"""
    
    prompt = f"""Generate a professional CV in {language} for the following candidate:

CANDIDATE INFORMATION:
- Name: {candidate.full_name}
- Passport: {candidate.passport_number}
- Date of Birth: {candidate.date_of_birth}
- Nationality: {candidate.nationality}
- Email: {candidate.email}
- Phone: {candidate.phone}

EDUCATION:
"""
    
    # Add education
    education = candidate.education_set.all()
    if education.exists():
        for edu in education:
            prompt += f"- {edu.degree} in {edu.field_of_study} from {edu.institution} ({edu.graduation_year})\n"
    else:
        prompt += "- Not specified\n"
    
    prompt += "\nEXPERIENCE:\n"
    
    # Add experience
    experience = candidate.experience_set.all()
    if experience.exists():
        for exp in experience:
            prompt += f"- {exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date})\n"
            if exp.description:
                prompt += f"  {exp.description}\n"
    else:
        prompt += "- Not specified\n"
    
    prompt += "\nSKILLS:\n"
    
    # Add skills
    skills = candidate.skills.all() if hasattr(candidate, 'skills') else []
    if skills:
        for skill in skills:
            prompt += f"- {skill.name}\n"
    else:
        prompt += "- Not specified\n"
    
    prompt += "\nLANGUAGES:\n"
    
    # Add languages
    languages = candidate.languages.all() if hasattr(candidate, 'languages') else []
    if languages:
        for lang in languages:
            prompt += f"- {lang.name}\n"
    else:
        prompt += "- Not specified\n"
    
    # Add job context if provided
    if job:
        prompt += f"\nTHIS CV IS FOR POSITION:\n"
        prompt += f"- Job Title: {job.position}\n"
        prompt += f"- Company: {job.employer.company_name if job.employer else 'Unknown'}\n"
        prompt += f"- Country: {job.country}\n"
        prompt += f"- Requirements: {job.requirements if job.requirements else 'Not specified'}\n"
        prompt += f"\nTailor the CV to highlight relevant skills and experience for this position.\n"
    
    prompt += f"""
INSTRUCTIONS:
1. Create a professional, well-formatted CV
2. Use clear sections (Summary, Experience, Education, Skills, Languages)
3. Keep language and style professional
4. Highlight relevant qualifications
5. Use bullet points for clarity
6. Include a professional summary at the top
7. Format in {language}
8. Make it suitable for international recruitment
"""
    
    return prompt


def match_candidates_to_job(self, job_id, limit=10):
    """Find candidates matching a job"""
    from smart_career.apps.jobs.models import Job
    from smart_career.apps.candidates.models import Candidate
    
    if not self.provider:
        return {
            'success': False,
            'error': 'AI provider not configured',
        }
    
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return {
            'success': False,
            'error': f'Job {job_id} not found',
        }
    
    # Get eligible candidates
    candidates = Candidate.objects.filter(
        current_status__in=['AVAILABLE', 'APPLIED', 'SHORTLISTED']
    )[:20]
    
    if not candidates.exists():
        return {
            'success': True,
            'matches': [],
            'message': 'No candidates found',
        }
    
    # Build matching prompt
    prompt = self._build_matching_prompt(job, candidates)
    
    messages = [
        {
            "role": "system",
            "content": "You are an expert recruiter. Analyze candidates and rank them by fit for the job. Return JSON array with matches."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    response = self.provider.complete(messages)
    
    if not response['success']:
        return {
            'success': False,
            'error': response.get('error'),
        }
    
    # Parse and return matches
    return {
        'success': True,
        'job_id': job_id,
        'matches': response['content'],
        'tokens_used': response.get('tokens_used', 0),
    }


def _build_matching_prompt(self, job, candidates):
    """Build prompt for job matching"""
    
    prompt = f"""Analyze the following candidates and their fit for this job position.

JOB DETAILS:
- Position: {job.position}
- Country: {job.country}
- Salary: {job.salary} {job.currency if hasattr(job, 'currency') else 'USD'}
- Requirements: {job.requirements}
- Skills Required: {job.required_skills if hasattr(job, 'required_skills') else 'Not specified'}
- Experience Required: {job.years_of_experience if hasattr(job, 'years_of_experience') else 'Not specified'} years

CANDIDATES:
"""
    
    for i, candidate in enumerate(candidates, 1):
        prompt += f"\n{i}. {candidate.full_name} (ID: {candidate.candidate_id})\n"
        prompt += f"   - Nationality: {candidate.nationality}\n"
        prompt += f"   - Age: {candidate.age}\n"
        
        # Education
        education = candidate.education_set.first()
        if education:
            prompt += f"   - Education: {education.degree} in {education.field_of_study}\n"
        
        # Experience
        experience = candidate.experience_set.first()
        if experience:
            prompt += f"   - Experience: {experience.job_title}\n"
        
        prompt += f"   - Preferred Country: {candidate.preferred_country}\n"
    
    prompt += """
INSTRUCTIONS:
1. Analyze each candidate's fit for the position
2. Rate match percentage (0-100%)
3. List matching qualifications
4. List gaps or concerns
5. Return as JSON array with this format:
[
  {
    "candidate_name": "Name",
    "candidate_id": "ID",
    "match_percentage": 85,
    "strengths": ["skill1", "skill2"],
    "gaps": ["missing_skill"],
    "recommendation": "Strong match" or "Consider" or "Not recommended"
  }
]
"""
    
    return prompt