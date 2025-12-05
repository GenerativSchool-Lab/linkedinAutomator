from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    mistral_api_key: Optional[str] = None
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None
    rate_limit_delay: int = 30  # seconds between actions (LinkedIn recommends 20-30s minimum)
    followup_days: int = 7  # days to wait before follow-up
    max_connections_per_day: int = 20  # Maximum connection requests per day to avoid rate limiting
    retry_delay_base: int = 60  # Base delay for retries (seconds)
    max_retries: int = 3  # Maximum number of retries for failed actions
    secret_key: str = "your-secret-key-change-in-production"
    allowed_origins: str = "*"  # Comma-separated list of allowed origins, or "*" for all
    company_name: Optional[str] = None  # Your company name
    company_description: Optional[str] = None  # What your company does
    value_proposition: Optional[str] = None  # Your value proposition for personalizing messages
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

