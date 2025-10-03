from fastapi import FastAPI

from contextlib import asynccontextmanager

from app.tasks.routers import router as app_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Startup")
    yield
    print("Application Shutdown")

app = FastAPI(
    title="Simple Todo App Api",
    description="this is a simple blog app with minimal usage of authentication and post managing",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Reza Hosseini",
        "email": "hosseini.reza65@gmail.com",
    },
    license_info={"name": "MIT"},
    docs_url="/docs",
    lifespan=lifespan
    )

app.include_router(app_router)
