from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from infra.db.main import build_session_factory, get_engine
from infra.settings import postgres
from presentation.routers.links import router as links_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with get_engine(postgres) as engine:
        session_factory = build_session_factory(engine)
        app.state.engine = engine
        app.state.session_factory = session_factory
        yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(links_router)
    return app


app = create_app()
