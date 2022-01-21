from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import ConfigClass
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
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from app.namespace import namespace
from app.config import ConfigClass
from app.commons.data_providers.database import engine
"""
opentelemetry instrument for additional packages could be found here:

https://github.com/open-telemetry/opentelemetry-python-contrib/tree/main/instrumentation

In each folder of above link, open folder src/opentelemetry/instrumentation/{package}, 
in __init__.py there suppose be a Instrumentor, such as Psycopg2Instrumentor
"""

def instrument_app(app):
    if not ConfigClass.OPEN_TELEMETRY_ENABLED:
        return

    tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: namespace}))
    trace.set_tracer_provider(tracer_provider)

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine, service=namespace)
    HTTPXClientInstrumentor().instrument()
    AsyncPGInstrumentor().instrument()

    jaeger_exporter = JaegerExporter(
        agent_host_name=ConfigClass.OPEN_TELEMETRY_HOST, agent_port=ConfigClass.OPEN_TELEMETRY_PORT
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))



def create_app():
    """
    create app function
    """
    app = FastAPI(
        title="BFF VRECLI",
        description="BFF for vrecli",
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
    api_registry(app)
    instrument_app(app)
    return app
