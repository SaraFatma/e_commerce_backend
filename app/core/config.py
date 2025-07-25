from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    email_from: str
    email_password: str
    email_server: str
    email_port: int

 
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
