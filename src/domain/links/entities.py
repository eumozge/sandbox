from dataclasses import dataclass, field
from datetime import datetime

from domain.common.entities import Entity
from domain.links import value_objects as vo


@dataclass
class Link(Entity):
    original_url: vo.URL
    short_code: vo.ShortCode

    id: vo.ID = field(default_factory=vo.ID)
    created_at: datetime = field(default_factory=datetime.now)
