from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Mapped, mapped_column

from domain.common.entities import Entity
from domain.links.value_objects.id import ID
from domain.links.value_objects.url import URL
from infra.db.models.base import mapper_registry
from infra.db.models.types import IDColumn, URLColumn


@mapper_registry.mapped_as_dataclass
class Link(Entity):
    __tablename__ = "links"

    id: Mapped[ID] = mapped_column(IDColumn, primary_key=True, default_factory=uuid4, init=False)
    original: Mapped[URL] = mapped_column(URLColumn, nullable=False)
    short: Mapped[URL] = mapped_column(URLColumn, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default="now()",
        default_factory=datetime.now,
        init=False,
    )
