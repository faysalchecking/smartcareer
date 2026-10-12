import requests
import json
from abc import ABC, abstractmethod
from datetime import datetime

class AIProviderBase(ABC):
    """Base class for AI providers"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')
        self.model_name = config.get('model_name')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
    
    @abstractmethod
    def complete(self, messages, tools=None):
        """Generate completion"""
        pass
    
    @abstractmethod
    def test_connection(self):
        """Test if provider is working"""
        pass


class OllamaProvider(AIProviderBase):
    """Local Ollama provider"""
    
    def __init__(self, config):
        super().__init__(config)
        if not self.base_url:
            self.base_url = 'http://localhost:11434'
    
    def complete(self, messages, tools=None):
        """Send request to Ollama"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'content': data.get('message', {}).get('content', ''),
                'tokens_used': data.get('eval_count', 0),
                'model': data.get('model'),
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None,
            }
    
    def test_connection(self):
        """Test Ollama connection"""
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            models = response.json().get('models', [])
            return {
                'working': len(models) > 0,
                'available_models': [m.get('name') for m in models],
            }
        except Exception as e:
            return {
                'working': False,
                'error': str(e),
            }


class OpenAIProvider(AIProviderBase):
    """OpenAI API provider"""
    
    def __init__(self, config):
        super().__init__(config)
        if not self.base_url:
            self.base_url = 'https://api.openai.com/v1'
    
    def complete(self, messages, tools=None):
        """Send request to OpenAI"""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        if tools:
            payload["tools"] = tools
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return {
                'success': True,
                'content': data['choices'][0]['message']['content'],
                'tokens_used': data.get('usage', {}).get('total_tokens', 0),
                'model': data.get('model'),
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'content': None,
            }
    
    def test_connection(self):
        """Test OpenAI connection"""
        try:
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return {
                'working': True,
            }
        except Exception as e:
            return {
                'working': False,
                'error': str(e),
            }


class AIProviderFactory:
    """Factory for creating AI provider instances"""
    
    PROVIDERS = {
        'LOCAL_OLLAMA': OllamaProvider,
        'OPENAI': OpenAIProvider,
    }
    
    @staticmethod
    def get_provider(ai_provider_obj):
        """Get provider instance from database object"""
        provider_class = AIProviderFactory.PROVIDERS.get(
            ai_provider_obj.provider_type
        )
        
        if not provider_class:
            raise ValueError(f"Unknown provider: {ai_provider_obj.provider_type}")
        
        config = {
            'api_key': ai_provider_obj.api_key,
            'base_url': ai_provider_obj.base_url,
            'model_name': ai_provider_obj.model_name,
            'temperature': ai_provider_obj.temperature,
            'max_tokens': ai_provider_obj.max_tokens,
        }
        
        return provider_class(config)