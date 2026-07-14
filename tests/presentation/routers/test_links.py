from uuid import uuid4

import sqlalchemy as sa
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models.links import LINKS_TABLE


async def test_redirect_by_short_code__unknown(client: AsyncClient) -> None:
    response = await client.get("/mycode")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers.get("location") == "/"


async def test_redirect_by_short_code__success(client: AsyncClient, session: AsyncSession) -> None:
    await session.execute(
        sa.insert(LINKS_TABLE).values(
            id=uuid4(),
            original_url="https://example.com",
            short_code="mycode",
        )
    )
    await session.commit()

    response = await client.get("/mycode")
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers.get("location") == "https://example.com"


async def test_create_link__success(client: AsyncClient, session: AsyncSession) -> None:
    payload = {"original_url": "https://example.com", "short_code": "mycode"}

    response = await client.post("/links", json=payload)

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] is not None
    assert body["original_url"] == "https://example.com/"
    assert body["short_code"] == "mycode"
    assert body["created_at"] is not None

    result = await session.execute(
        sa.select(LINKS_TABLE).where(LINKS_TABLE.c.short_code == "mycode")
    )
    row = result.one()
    assert row.original_url == "https://example.com/"


async def test_create_link__invalid_url(client: AsyncClient) -> None:
    payload = {"original_url": "not-a-url", "short_code": "x"}

    response = await client.post("/links", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
