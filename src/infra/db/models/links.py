from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import composite

from domain.links import entities, value_objects
from infra.db.models.base import TimedBaseModel, mapper_registry

LINKS_TABLE = sa.Table(
    "links",
    TimedBaseModel.metadata,
    sa.Column(
        "id",
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=sa.func.uuid_generate_v2(),
    ),
    sa.Column("original", sa.String),
    sa.Column("short", sa.String),
    sa.Column(
        "created_at", sa.DateTime(timezone=True), server_default=sa.text("NULL"), nullable=False
    ),
)

mapper_registry.map_imperatively(
    entities.Link,
    LINKS_TABLE,
    properties={
        "id": composite(value_objects.ID, LINKS_TABLE.c.id),
        "original": composite(value_objects.URL, LINKS_TABLE.c.original),
        "short": composite(value_objects.URL, LINKS_TABLE.c.short),
    },
)
