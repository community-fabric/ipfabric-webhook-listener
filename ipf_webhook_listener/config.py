from pydantic import BaseSettings, BaseModel, Field
from .models import Event
from typing import Optional


class Status(BaseModel):
    started: bool = True
    completed: bool = True
    failed: bool = True
    resumed: bool = True
    stopping: bool = True
    stopped: bool = True


class Action(BaseModel):
    discover: Status = Field(default_factory=Status)
    clone: Status = Field(default_factory=Status)
    delete: Status = Field(default_factory=Status)
    download: Status = Field(default_factory=Status)
    load: Status = Field(default_factory=Status)
    unload: Status = Field(default_factory=Status)


class Alerts(BaseModel):
    snapshot: Action = Field(default_factory=Action)
    intent: Status = Field(default_factory=Status)

    def check_event(self, event: Event):
        status = event.status
        if 'stopping' in status:
            status = 'stopping'
        if event.type == 'snapshot':
            action = getattr(self.snapshot, event.action)
            return getattr(action, status)
        else:
            return getattr(self.intent, status)


class Settings(BaseSettings):
    ipf_secret: str
    ipf_url: str
    ipf_token: str
    ipf_verify: bool = True
    ipf_test: bool = False
    teams_url: Optional[str]
    slack_url: Optional[str]
    ipf_alerts: Alerts = Field(default_factory=Alerts)

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
