from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .api_registry import api_registry
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from app.namespace import namespace
from app.config import ConfigClass
from app.commons.data_providers.database import engine
from app.resources.error_handler import APIException


def instrument_app(app) -> None:
    if not ConfigClass.OPEN_TELEMETRY_ENABLED:
        return

    tracer_provider = TracerProvider(
        resource=Resource.create({SERVICE_NAME: namespace}))
    trace.set_tracer_provider(tracer_provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name=ConfigClass.OPEN_TELEMETRY_HOST, agent_port=ConfigClass.OPEN_TELEMETRY_PORT
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
    
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine, service=namespace)
    HTTPXClientInstrumentor().instrument()


def create_app():
    """
    create app function
    """
    app = FastAPI(
        title="BFF CLI",
        description="BFF for cli",
        docs_url="/v1/api-doc",
        version=ConfigClass.version
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins="*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(APIException)
    async def http_exception_handler(request: Request, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.content,
        )

    api_registry(app)
    return app
