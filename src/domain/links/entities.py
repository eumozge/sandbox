from dataclasses import dataclass, field
from datetime import datetime

from domain.common.entities import Entity
from domain.links.value_objects.id import ID
from domain.links.value_objects.short_code import ShortCode
from domain.links.value_objects.url import URL


@dataclass
class Link(Entity):
    id: ID
    original_url: URL
    short_code: ShortCode
    created_at: datetime = field(default_factory=datetime.now)
