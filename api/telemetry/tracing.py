"""OpenTelemetry tracing setup and FastAPI instrumentation."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def setup_telemetry(app: Any = None) -> bool:
    """Configures OpenTelemetry tracer provider and instruments the FastAPI app.

    Returns True if OpenTelemetry was successfully initialized, False otherwise.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import SERVICE_NAME, Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

        service_name = os.getenv("OTEL_SERVICE_NAME", "talent-marketplace-engine")
        resource = Resource.create({SERVICE_NAME: service_name})
        provider = TracerProvider(resource=resource)

        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (  # type: ignore
                    OTLPSpanExporter,
                )

                exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
                provider.add_span_processor(BatchSpanProcessor(exporter))
                logger.info("Configured OTLP gRPC SpanExporter at %s", otlp_endpoint)
            except Exception as e:
                logger.warning(
                    "Failed to initialize OTLP exporter, falling back to ConsoleSpanExporter: %s",
                    e,
                )
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        elif os.getenv("OTEL_DEBUG_CONSOLE"):
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(provider)

        if app is not None:
            try:
                from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

                FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
                logger.info("FastAPI application instrumented with OpenTelemetry")
            except Exception as inst_err:
                logger.warning("Could not instrument FastAPI application: %s", inst_err)

        return True
    except ImportError as e:
        logger.info("OpenTelemetry packages not installed; skipping instrumentation: %s", e)
        return False
    except Exception as e:
        logger.warning("Unexpected error configuring OpenTelemetry: %s", e)
        return False
