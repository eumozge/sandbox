from datetime import datetime

from pydantic import BaseModel, HttpUrl


class CreateLinkModel(BaseModel):
    original_url: HttpUrl
    short_code: str


class ReadLinkModel(BaseModel):
    id: str
    original_url: str
    short_code: str
    created_at: datetime
