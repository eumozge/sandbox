from uuid import uuid4

import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models.links import LINKS_TABLE


async def test_redirect_by_short_code__unknown(client: AsyncClient) -> None:
    response = await client.get("/foo")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers.get("location") == "/"


async def test_redirect_by_short_code__success(client: AsyncClient, session: AsyncSession) -> None:
    await session.execute(
        sa.insert(LINKS_TABLE).values(
            id=uuid4(),
            original_url="https://example.com",
            short_code="foo",
        )
    )
    await session.commit()

    response = await client.get("/foo")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers.get("location") == "https://example.com"
