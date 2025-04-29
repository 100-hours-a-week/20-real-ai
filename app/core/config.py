from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Chuni Office Assistant"

settings = Settings()