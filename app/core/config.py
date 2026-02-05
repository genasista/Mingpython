from pydantic import BaseSettings

class Settings(BaseSettings):
    SERVICE_NAME: str = "Genassista-EDU-pythonAPI"
    SERVICE_VERSION: str = "0.1.0"

    # Feature flags / runtime
    SANDBOX_MODE: bool = True
    ENABLE_SUBSCRIBER: bool = False

    # Core API connection
    CORE_BASE_URL: str = "http://localhost:3001"  # Backend runs on 3001
    API_KEY: str = "ADD-X-API-KEY"  # Match backend's API_KEYS
    ADMIN_TOKEN: str = ""  # Optional admin token

    # RabbitMQ (updated from NATS)
    AMQP_URL: str = "amqp://guest:guest@localhost:5672/"
    SUBSCRIBER_EXCHANGE: str = "events"
    EVENT_SUBMISSION_CREATED: str = "submission.created"
    SUBSCRIBER_QUEUE: str = "submission.created"

    # CORS (to match backend)
    CORS_ORIGIN: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
