from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from application.links.use_cases import CreateLinkUseCase, GetLinkByShortCodeUseCase
from presentation.dependencies import create_link_use_case, get_link_by_short_code_use_case
from presentation.models.links import CreateLinkModel, ReadLinkModel

router = APIRouter()


@router.get("/{short_code}")
async def redirect_by_short_code(
    short_code: str,
    use_case: Annotated[GetLinkByShortCodeUseCase, Depends(get_link_by_short_code_use_case)],
) -> RedirectResponse:
    link = await use_case.execute(short_code)
    if link is None:
        return RedirectResponse(url="/")
    return RedirectResponse(url=link.original_url.value)


@router.post("/links")
async def create_link(
    payload: CreateLinkModel,
    use_case: Annotated[CreateLinkUseCase, Depends(create_link_use_case)],
) -> ReadLinkModel:
    link = await use_case.execute(str(payload.original_url), payload.short_code)
    return ReadLinkModel(
        id=str(link.id.value),
        original_url=link.original_url.value,
        short_code=link.short_code.value,
        created_at=link.created_at,
    )
