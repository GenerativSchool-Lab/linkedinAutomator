from mistralai import Mistral
from typing import Optional
from app.config import settings
from app.models.profile import Profile
from app.models.message import Message


class MessageGenerator:
    def __init__(self):
        if not settings.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        self.client = Mistral(api_key=settings.mistral_api_key)

    def generate_connection_message(self, profile: Profile) -> str:
        """Generate a personalized connection message"""
        prompt = f"""Generate a professional, personalized LinkedIn connection request message (max 300 characters) for:

Name: {profile.name}
Title: {profile.title or 'Not specified'}
Company: {profile.company or 'Not specified'}
Notes: {profile.notes or 'None'}

The message should be:
- Professional but friendly
- Personalized based on their profile
- Brief and engaging
- Not overly salesy
- Under 300 characters

Return only the message text, no additional commentary."""

        try:
            response = self.client.chat.complete(
                model="mistral-medium-latest",
                messages=[
                    {"role": "system", "content": "You are a professional networking assistant that creates personalized LinkedIn connection messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating message: {e}")
            # Fallback to template
            return self._fallback_connection_message(profile)

    def generate_followup_message(self, profile: Profile, previous_messages: list[Message]) -> str:
        """Generate a follow-up message based on conversation history"""
        previous_content = "\n".join([f"- {msg.content}" for msg in previous_messages])
        
        prompt = f"""Generate a professional LinkedIn follow-up message (max 300 characters) for:

Name: {profile.name}
Title: {profile.title or 'Not specified'}
Company: {profile.company or 'Not specified'}

Previous messages sent:
{previous_content}

The follow-up should be:
- Professional and friendly
- Reference the previous connection/message
- Provide value or ask a thoughtful question
- Not pushy or salesy
- Under 300 characters

Return only the message text, no additional commentary."""

        try:
            response = self.client.chat.complete(
                model="mistral-medium-latest",
                messages=[
                    {"role": "system", "content": "You are a professional networking assistant that creates personalized LinkedIn follow-up messages."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating follow-up: {e}")
            # Fallback to template
            return self._fallback_followup_message(profile)

    def _fallback_connection_message(self, profile: Profile) -> str:
        """Fallback template message"""
        if profile.company:
            return f"Hi {profile.name.split()[0] if profile.name else 'there'}, I noticed your work at {profile.company} and thought we might have some mutual interests. Would love to connect!"
        return f"Hi {profile.name.split()[0] if profile.name else 'there'}, I'd like to connect and learn more about your experience. Looking forward to connecting!"

    def _fallback_followup_message(self, profile: Profile) -> str:
        """Fallback follow-up template"""
        return f"Hi {profile.name.split()[0] if profile.name else 'there'}, I wanted to follow up on my previous message. Would love to hear your thoughts when you have a moment!"


# Lazy initialization - only create when needed
_message_generator_instance = None

def get_message_generator():
    """Get or create the message generator instance"""
    global _message_generator_instance
    if _message_generator_instance is None:
        _message_generator_instance = MessageGenerator()
    return _message_generator_instance

# For backward compatibility, create a proxy object
class MessageGeneratorProxy:
    def generate_connection_message(self, profile: Profile) -> str:
        return get_message_generator().generate_connection_message(profile)
    
    def generate_followup_message(self, profile: Profile, previous_messages: list[Message]) -> str:
        return get_message_generator().generate_followup_message(profile, previous_messages)

message_generator = MessageGeneratorProxy()

