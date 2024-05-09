import pysnooper
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
app.mount(
    "/.files", StaticFiles(directory="app/files"), "files"
)  # reference: https://python.plainenglish.io/file-uploads-and-downloads-in-fastapi-a-comprehensive-guide-06e0b18bb245


# XXX: for debugging check that the openapi schema is generated
@pysnooper.snoop(max_variable_length=None)
def debugging_openapi():
    # reference: https://fastapi.tiangolo.com/how-to/extending-openapi/#overriding-the-defaults
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        terms_of_service=app.terms_of_service,
        contact=app.contact,
        license_info=app.license_info,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = debugging_openapi
