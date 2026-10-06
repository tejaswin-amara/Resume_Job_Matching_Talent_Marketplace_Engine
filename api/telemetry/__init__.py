"""OpenTelemetry instrumentation package for talent marketplace engine."""

from api.telemetry.tracing import setup_telemetry

__all__ = ["setup_telemetry"]
