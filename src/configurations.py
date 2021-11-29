from pydantic import BaseSettings


class Settings(BaseSettings):
    ipf_secret: str = "dd2e9858a739f7e0819b159a5dcc8df1"
    ipf_instance: str = 'https://172.22.183.134'
    ipf_token: str = 'afe045a522a947775e47609937eb7eac'
    PLUGINS: list = ['test']
    PLUGINS_CONFIG: dict = {}


settings = Settings()
