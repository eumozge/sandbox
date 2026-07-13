from dataclasses import dataclass, field
from datetime import datetime

from domain.common.entities import Entity
from domain.links.value_objects.id import ID
from domain.links.value_objects.url import URL


@dataclass
class Link(Entity):
    id: ID
    original: URL
    short: URL
    created_at: datetime = field(default_factory=datetime.now)

