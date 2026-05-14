from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "phishguard"
    MODEL_PATH: str = "app/ml/models/phishing_model.pkl"
    VIRUSTOTAL_API_KEY: str = ""
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
