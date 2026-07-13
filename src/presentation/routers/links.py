from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from application.links.use_cases import GetLinkByShortCodeUseCase
from presentation.dependencies import get_link_by_short_code_use_case

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
