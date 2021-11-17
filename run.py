import uvicorn
from app.config import ConfigClass
from app.main import create_app
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
# from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from app.namespace import namespace
from app.config import ConfigClass
from trace import get_additional_instrument

app = create_app()

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: namespace})
    )
)
jaeger_exporter = JaegerExporter(
    agent_host_name=ConfigClass.OPEN_TELEMETRY_HOST, agent_port=ConfigClass.OPEN_TELEMETRY_PORT
    # agent_host_name='0.0.0.0', agent_port=6831
    )
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
FastAPIInstrumentor.instrument_app(app)
get_additional_instrument()


if __name__ == "__main__":
    uvicorn.run("run:app", host=ConfigClass.settings.host, port=ConfigClass.settings.port, log_level="info", reload=True)
