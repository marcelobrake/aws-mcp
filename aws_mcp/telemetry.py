"""OpenTelemetry instrumentation for AWS MCP Server.

Provides distributed tracing for every tool invocation. Traces are exported
to an OTLP endpoint when OTEL_EXPORTER_OTLP_ENDPOINT is set, otherwise
tracing is initialized with a no-op exporter to keep overhead minimal.
"""
import logging
import os
import sys
import time
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor

logger = logging.getLogger("aws_mcp")

_tracer: trace.Tracer | None = None


def init_telemetry() -> trace.Tracer:
    """Initialize OpenTelemetry tracing.

    Configures an OTLP exporter if OTEL_EXPORTER_OTLP_ENDPOINT is set,
    otherwise falls back to a file-based span exporter writing to stderr.
    """
    global _tracer

    resource = Resource.create(
        {
            "service.name": "aws-mcp",
            "service.version": "0.1.0",
        }
    )
    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info(
                f"OTLP tracing enabled: endpoint={otlp_endpoint}",
                extra={"tool_name": "telemetry"},
            )
        except ImportError:
            logger.warning(
                "opentelemetry-exporter-otlp not installed; OTLP tracing disabled",
                extra={"tool_name": "telemetry"},
            )
    else:
        # Minimal console exporter to stderr (does not interfere with MCP stdio)
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter

        exporter = ConsoleSpanExporter(out=sys.stderr)
        provider.add_span_processor(SimpleSpanProcessor(exporter))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer("aws-mcp", "0.1.0")
    return _tracer


def get_tracer() -> trace.Tracer:
    """Return the application tracer, initializing if needed."""
    if _tracer is None:
        return init_telemetry()
    return _tracer


@contextmanager
def trace_tool_call(tool_name: str, **attributes):
    """Context manager that wraps a tool call in an OpenTelemetry span.

    Usage::

        with trace_tool_call("aws_ec2_describe_instances", profile="dev"):
            result = await handler(args)

    Attributes such as ``profile``, ``region``, ``service`` are attached to
    the span for filtering in your observability backend.
    """
    tracer = get_tracer()
    with tracer.start_as_current_span(f"tool.{tool_name}") as span:
        span.set_attribute("tool.name", tool_name)
        for key, value in attributes.items():
            if value is not None:
                span.set_attribute(f"aws.{key}", str(value))

        start = time.monotonic()
        try:
            yield span
        except Exception as exc:
            span.set_status(trace.StatusCode.ERROR, str(exc))
            span.record_exception(exc)
            raise
        finally:
            duration_ms = (time.monotonic() - start) * 1000
            span.set_attribute("duration_ms", round(duration_ms, 2))
