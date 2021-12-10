from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, Field


class Snapshot(BaseModel):
    id: str
    name: Optional[str]
    clone_id: Optional[str] = Field(alias='cloneId')
    file: Optional[str]


class Event(BaseModel):
    type: str
    action: str
    status: str
    test: Optional[bool] = False
    requester: str
    snapshot: Optional[Snapshot] = None
    timestamp: datetime
    report_id: Optional[Union[str, list]] = Field(alias='reportId')
    snapshot_id: Optional[str] = Field(alias='snapshotId')
