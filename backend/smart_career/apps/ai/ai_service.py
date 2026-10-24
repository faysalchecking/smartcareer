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
            provider_obj = AIProvider.objects.filter(
                is_active=True
            ).first()
            
            if not provider_obj:
                return None
            
            return AIProviderFactory.get_provider(provider_obj)
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
                'error': 'AI provider not configured. Please configure an AI provider in settings.',
            }
        
        try:
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
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing message: {str(e)}',
            }
    
    def _build_message_history(self, conversation):
        """Build message history for context"""
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": self._get_system_prompt(conversation),
        })
        
        # Add recent messages (last 5 exchanges)
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
        
        return self.provider.test_connection()