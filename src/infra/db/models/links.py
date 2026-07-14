from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import composite

from domain.links import entities, value_objects
from infra.db.models.base import BaseModel, mapper_registry

LINKS_TABLE = sa.Table(
    "links",
    BaseModel.metadata,
    sa.Column(
        "id",
        sa.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=sa.func.gen_random_uuid(),
    ),
    sa.Column("original_url", sa.String),
    sa.Column("short_code", sa.String),
    sa.Column(
        "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    ),
)

mapper_registry.map_imperatively(
    entities.Link,
    LINKS_TABLE,
    properties={
        "id": composite(value_objects.ID, LINKS_TABLE.c.id),
        "original_url": composite(value_objects.URL, LINKS_TABLE.c.original_url),
        "short_code": composite(value_objects.ShortCode, LINKS_TABLE.c.short_code),
    },
    column_prefix="_",
)
