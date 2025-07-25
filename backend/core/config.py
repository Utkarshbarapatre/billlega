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
    
    # Railway Configuration - Get actual domain from Railway
    railway_environment: str = os.getenv("RAILWAY_ENVIRONMENT", "development")
    railway_service_name: str = os.getenv("RAILWAY_SERVICE_NAME", "legal-billing-summarizer")
    
    # Railway provides these automatically
    railway_static_url: str = os.getenv("RAILWAY_STATIC_URL", "")
    railway_public_domain: str = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
    
    @property
    def railway_domain(self) -> str:
        """Get the actual Railway domain"""
        # Try Railway's automatic environment variables first
        if self.railway_static_url:
            return self.railway_static_url.replace("https://", "").replace("http://", "")
        elif self.railway_public_domain:
            return self.railway_public_domain
        # Fallback to manual override
        return os.getenv("RAILWAY_DOMAIN", "localhost:8080")
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the application"""
        if self.is_production:
            return f"https://{self.railway_domain}"
        return f"http://localhost:{self.port}"
    
    # Clio Configuration - Use dynamic domain
    clio_client_id: str = os.getenv("CLIO_CLIENT_ID", "")
    clio_client_secret: str = os.getenv("CLIO_CLIENT_SECRET", "")
    clio_base_url: str = os.getenv("CLIO_BASE_URL", "https://app.clio.com")
    
    @property
    def clio_redirect_uri(self) -> str:
        """Get Clio redirect URI with actual domain"""
        return f"{self.base_url}/callback"
    
    # Application Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    port: int = int(os.getenv("PORT", 8080))
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./legal_billing.db")
    
    @property
    def is_production(self) -> bool:
        return self.railway_environment == "production" or not self.debug

settings = Settings()
