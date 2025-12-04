from mistralai import Mistral
from typing import Optional
from app.config import settings as config_settings
from app.models.profile import Profile
from app.models.message import Message
from app.database import SessionLocal
from app.models.settings import AppSettings


class MessageGenerator:
    def __init__(self):
        if not config_settings.mistral_api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        self.client = Mistral(api_key=config_settings.mistral_api_key)
    
    def _get_company_context(self) -> str:
        """Get company context from database settings"""
        db = SessionLocal()
        try:
            app_settings = db.query(AppSettings).filter(AppSettings.id == 1).first()
            if not app_settings:
                return ""
            
            context = ""
            if app_settings.company_name:
                context += f"\n\nÀ propos de notre entreprise ({app_settings.company_name}):"
                if app_settings.company_description:
                    context += f"\n{app_settings.company_description}"
                if app_settings.value_proposition:
                    context += f"\n\nNotre proposition de valeur: {app_settings.value_proposition}"
            
            return context
        finally:
            db.close()

    def generate_connection_message(self, profile: Profile) -> str:
        """Generate a personalized connection message in French"""
        # Get company context from database
        company_context = self._get_company_context()
        
        prompt = f"""Génère un message de demande de connexion LinkedIn professionnel et personnalisé (max 300 caractères) en français pour:

Profil du contact:
- Nom: {profile.name}
- Titre: {profile.title or 'Non spécifié'}
- Entreprise: {profile.company or 'Non spécifiée'}
- Informations supplémentaires: {profile.notes or 'Aucune'}{company_context}

Le message doit être:
- Professionnel mais amical
- Personnalisé selon leur profil et leur contexte professionnel
- Mentionner subtilement notre proposition de valeur si pertinente
- Court et engageant
- Pas trop commercial ou pushy
- En français
- Moins de 300 caractères
- Créer un lien naturel entre leur profil et notre entreprise

Retourne uniquement le texte du message, sans commentaire supplémentaire."""

        try:
            response = self.client.chat.complete(
                model="mistral-medium-latest",
                messages=[
                    {"role": "system", "content": "Tu es un assistant de networking professionnel qui crée des messages de demande de connexion LinkedIn personnalisés en français."},
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
        """Generate a follow-up message in French based on conversation history"""
        previous_content = "\n".join([f"- {msg.content}" for msg in previous_messages])
        
        # Get company context from database
        company_context = self._get_company_context()
        
        prompt = f"""Génère un message de suivi LinkedIn professionnel (max 300 caractères) en français pour:

Profil du contact:
- Nom: {profile.name}
- Titre: {profile.title or 'Non spécifié'}
- Entreprise: {profile.company or 'Non spécifiée'}

Messages précédents envoyés:
{previous_content}{company_context}

Le message de suivi doit être:
- Professionnel et amical
- Faire référence à la connexion/message précédent
- Apporter de la valeur ou poser une question pertinente liée à notre proposition de valeur
- Pas trop insistant ou commercial
- En français
- Moins de 300 caractères
- Créer un intérêt naturel pour notre entreprise sans être pushy

Retourne uniquement le texte du message, sans commentaire supplémentaire."""

        try:
            response = self.client.chat.complete(
                model="mistral-medium-latest",
                messages=[
                    {"role": "system", "content": "Tu es un assistant de networking professionnel qui crée des messages de suivi LinkedIn personnalisés en français."},
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
        """Fallback template message in French"""
        first_name = profile.name.split()[0] if profile.name and ' ' in profile.name else (profile.name if profile.name else 'Bonjour')
        if profile.company:
            return f"Bonjour {first_name}, j'ai remarqué votre travail chez {profile.company} et je pense que nous pourrions avoir des intérêts communs. J'aimerais beaucoup nous connecter !"
        return f"Bonjour {first_name}, j'aimerais me connecter et en apprendre davantage sur votre expérience. Au plaisir de vous connecter !"

    def _fallback_followup_message(self, profile: Profile) -> str:
        """Fallback follow-up template in French"""
        first_name = profile.name.split()[0] if profile.name and ' ' in profile.name else (profile.name if profile.name else 'Bonjour')
        return f"Bonjour {first_name}, je souhaitais faire un suivi sur mon message précédent. J'aimerais beaucoup avoir votre avis quand vous aurez un moment !"


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

