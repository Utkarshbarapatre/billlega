import os
from typing import List

class Settings:
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Google/Gmail Configuration
    google_client_secret_file: str = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")
    google_scopes: str = os.getenv("GOOGLE_SCOPES", "https://www.googleapis.com/auth/gmail.readonly")
    
    @property
    def google_scopes_list(self) -> List[str]:
        return [scope.strip() for scope in self.google_scopes.split(",")]
    
    # Clio Configuration
    clio_client_id: str = os.getenv("CLIO_CLIENT_ID", "")
    clio_client_secret: str = os.getenv("CLIO_CLIENT_SECRET", "")
    clio_redirect_uri: str = os.getenv("CLIO_REDIRECT_URI", "https://gracious-celebration.railway.internal/callback")
    clio_base_url: str = os.getenv("CLIO_BASE_URL", "https://app.clio.com")
    
    # Application Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    port: int = int(os.getenv("PORT", 8000))
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./legal_billing.db")
    
    # Railway Configuration
    railway_environment: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    railway_service_name: str = os.getenv("RAILWAY_SERVICE_NAME", "legal-billing-summarizer")
    
    @property
    def is_production(self) -> bool:
        return self.railway_environment == "production" or not self.debug

settings = Settings()
