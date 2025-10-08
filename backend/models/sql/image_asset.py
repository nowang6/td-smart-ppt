from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field

from utils.datetime_utils import get_current_utc_datetime


class ImageAsset(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    is_uploaded: bool = Field(default=False)
    path: str
    extras: Optional[dict] = Field(default=None)
