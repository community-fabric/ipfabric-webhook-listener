from pydantic import BaseSettings


class Settings(BaseSettings):
    ipf_secret: str
    ipf_url: str
    ipf_token: str
    ipf_verify: bool = True
    ipf_test: bool = False
    tableau_server: str
    tableau_site: str
    tableau_project: str = 'Default'
    tableau_token_name: str
    tableau_token: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
