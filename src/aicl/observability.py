"""
OpenTelemetry observability configuration for AICL framework.

Supports sending traces and metrics to Grafana via OTLP.
Configure using environment variables:
- OTEL_EXPORTER_OTLP_ENDPOINT: Your Grafana OTLP endpoint (e.g., https://otlp-gateway-prod-us-east-0.grafana.net/otlp)
- OTEL_EXPORTER_OTLP_HEADERS: Auth headers (e.g., Authorization=Basic <base64>)
- OTEL_SERVICE_NAME: Service name (default: aicl-engine)
- OTEL_ENABLED: Set to 'false' to disable telemetry (default: true)
"""

import os
import logging
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION

logger = logging.getLogger(__name__)

_initialized = False
_tracer_provider: Optional[TracerProvider] = None
_meter_provider: Optional[MeterProvider] = None


def is_enabled() -> bool:
    """Check if OpenTelemetry is enabled."""
    return os.getenv('OTEL_ENABLED', 'true').lower() == 'true'


def initialize_observability(
    service_name: Optional[str] = None,
    service_version: str = "1.0.0"
) -> None:
    """
    Initialize OpenTelemetry tracing and metrics.
    
    Args:
        service_name: Name of the service (defaults to OTEL_SERVICE_NAME env var or 'aicl-engine')
        service_version: Version of the service
    """
    global _initialized, _tracer_provider, _meter_provider
    
    if _initialized:
        return
    
    if not is_enabled():
        logger.info("OpenTelemetry is disabled (OTEL_ENABLED=false)")
        return
    
    service_name = service_name or os.getenv('OTEL_SERVICE_NAME', 'aicl-engine')
    
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
    })
    
    _tracer_provider = _setup_tracing(resource)
    _meter_provider = _setup_metrics(resource)
    
    _initialized = True
    logger.info(f"OpenTelemetry initialized for service: {service_name}")


def _setup_tracing(resource: Resource) -> TracerProvider:
    """Setup trace provider with OTLP or console exporter."""
    provider = TracerProvider(resource=resource)
    
    otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            
            headers = {}
            headers_env = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
            if headers_env:
                for header in headers_env.split(','):
                    if '=' in header:
                        key, value = header.split('=', 1)
                        headers[key.strip()] = value.strip()
            
            exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint,
                headers=headers if headers else None
            )
            processor = BatchSpanProcessor(exporter)
            provider.add_span_processor(processor)
            logger.info(f"OTLP trace exporter configured: {otlp_endpoint}")
        except Exception as e:
            logger.warning(f"Failed to setup OTLP trace exporter: {e}. Falling back to console.")
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
    else:
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        logger.info("Console trace exporter configured (no OTEL_EXPORTER_OTLP_ENDPOINT set)")
    
    trace.set_tracer_provider(provider)
    return provider


def _setup_metrics(resource: Resource) -> MeterProvider:
    """Setup meter provider with OTLP or console exporter."""
    otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
            
            headers = {}
            headers_env = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
            if headers_env:
                for header in headers_env.split(','):
                    if '=' in header:
                        key, value = header.split('=', 1)
                        headers[key.strip()] = value.strip()
            
            exporter = OTLPMetricExporter(
                endpoint=otlp_endpoint,
                headers=headers if headers else None
            )
            reader = PeriodicExportingMetricReader(exporter, export_interval_millis=60000)
            provider = MeterProvider(resource=resource, metric_readers=[reader])
            logger.info(f"OTLP metric exporter configured: {otlp_endpoint}")
        except Exception as e:
            logger.warning(f"Failed to setup OTLP metric exporter: {e}. Falling back to console.")
            reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=60000)
            provider = MeterProvider(resource=resource, metric_readers=[reader])
    else:
        reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=60000)
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        logger.info("Console metric exporter configured (no OTEL_EXPORTER_OTLP_ENDPOINT set)")
    
    metrics.set_meter_provider(provider)
    return provider


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer instance.
    
    Args:
        name: Name of the tracer (usually __name__ of the module)
    
    Returns:
        Tracer instance
    """
    if not _initialized and is_enabled():
        initialize_observability()
    
    return trace.get_tracer(name)


def get_meter(name: str) -> metrics.Meter:
    """
    Get a meter instance.
    
    Args:
        name: Name of the meter (usually __name__ of the module)
    
    Returns:
        Meter instance
    """
    if not _initialized and is_enabled():
        initialize_observability()
    
    return metrics.get_meter(name)


def shutdown_observability() -> None:
    """Shutdown observability providers and flush pending telemetry."""
    global _initialized, _tracer_provider, _meter_provider
    
    if not _initialized:
        return
    
    try:
        if _tracer_provider:
            _tracer_provider.shutdown()
        if _meter_provider:
            _meter_provider.shutdown()
        logger.info("OpenTelemetry shutdown complete")
    except Exception as e:
        logger.error(f"Error during OpenTelemetry shutdown: {e}")
    finally:
        _initialized = False
        _tracer_provider = None
        _meter_provider = None
