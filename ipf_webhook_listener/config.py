from pydantic import BaseSettings


class Settings(BaseSettings):
    ipf_secret: str
    ipf_url: str
    ipf_token: str
    ipf_verify: bool = True
    ipf_test: bool = False
    postgres_user: str
    postgres_pass: str
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = 'ipfabric'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
