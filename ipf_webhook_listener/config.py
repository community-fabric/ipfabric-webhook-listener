from pydantic import BaseSettings


class Settings(BaseSettings):
    ipf_secret: str
    ipf_url: str
    ipf_token: str
    ipf_verify: bool = True
    ipf_test: bool = False
    email_user: str
    email_pass: str
    mail_from: str
    mail_to: str
    smtp_server: str
    smtp_port: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
