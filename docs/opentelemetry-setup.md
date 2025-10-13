# OpenTelemetry Integration

The AICL framework includes comprehensive OpenTelemetry instrumentation for distributed tracing and metrics.

## Features

### Distributed Tracing
- **Provider Lifecycle**: Track provider startup, configuration, and shutdown
- **Resource Operations**: Trace resource provisioning, evaluation, and destruction
- **Execution Flow**: Monitor dependency resolution and orchestration
- **Error Tracking**: Automatic exception recording with stack traces

### Metrics
- `aicl.provider.starts`: Counter for provider starts (labels: provider, mode)
- `aicl.resources.operations`: Counter for resource operations (labels: operation, resource)

## Configuration

### Environment Variables

```bash
# Enable/disable telemetry (default: true)
export OTEL_ENABLED=true

# Service identification
export OTEL_SERVICE_NAME="aicl-engine"

# OTLP Exporter (for Grafana/Tempo)
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-gateway-prod-<region>.grafana.net/otlp"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic <base64_credentials>"
```

### Grafana Cloud Setup

1. **Get your OTLP endpoint**:
   - Navigate to your Grafana Cloud instance
   - Go to Connections → Add new connection → OpenTelemetry
   - Copy the OTLP endpoint URL (e.g., `https://otlp-gateway-prod-us-east-0.grafana.net/otlp`)

2. **Generate credentials**:
   - Instance ID: Found in Grafana Cloud settings
   - API Token: Create a new token with "metrics" and "traces" permissions
   - Encode: `echo -n "<instance_id>:<api_token>" | base64`

3. **Configure environment**:
   ```bash
   export OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-gateway-prod-us-east-0.grafana.net/otlp"
   export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic <base64_from_step2>"
   ```

### Self-Hosted Grafana

For local or self-hosted Grafana with Tempo:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT="http://your-tempo-host:4317"
# Headers often not needed for local setups
export OTEL_EXPORTER_OTLP_HEADERS=""
```

## Trace Structure

### Provider Startup Spans
```
start_providers_subprocess (root)
├── start_provider.loader
│   └── provider config evaluation
└── start_provider.splitter
    └── provider config evaluation
```

### Resource Provisioning Spans
```
apply (root)
├── execute_resource.loader_files-docs
│   ├── provision_resource.loader_files-docs
│   │   ├── evaluate_config
│   │   └── provider_apply
└── execute_resource.splitter_text-chunks
    ├── provision_resource.splitter_text-chunks
    │   ├── evaluate_config
    │   └── provider_apply
```

### Resource Destruction Spans
```
destroy (root)
├── destroy_all_resources
│   ├── destroy_resource.loader_files-docs
│   └── destroy_resource.splitter_text-chunks
├── stop_provider.loader
└── stop_provider.splitter
```

## Span Attributes

### Provider Spans
- `provider.name`: Provider identifier
- `provider.count`: Number of providers
- `provider.mode`: "subprocess" or "docker"
- `provider.port`: gRPC port
- `provider.status`: "running" or "failed"

### Resource Spans
- `resource.type`: Resource type (e.g., "loader_files")
- `resource.name`: Resource name from config
- `resource.provider`: Provider handling the resource
- `resource.id`: Generated resource ID
- `resource.status`: "created", "deleted", or "failed"
- `resource.count`: Number of resources

### Execution Spans
- `experiment.id`: Experiment identifier

## Querying in Grafana

### Example Tempo Queries

Find slow resource provisioning:
```
{ service.name="aicl-engine" } | duration > 1s
```

Track provider failures:
```
{ service.name="aicl-engine" span.provider.status="failed" }
```

Analyze resource operations:
```
{ service.name="aicl-engine" resource.type="loader_files" }
```

### Example Prometheus Queries

Provider start rate:
```promql
rate(aicl_provider_starts_total[5m])
```

Resource operation breakdown:
```promql
sum by (operation) (aicl_resources_operations_total)
```

## Local Development

### Console Export (Default)

Without OTLP endpoint configured, telemetry exports to console:

```bash
python run.py your_config.aicl
# Traces and metrics printed to stdout in JSON format
```

### Disable Telemetry

```bash
export OTEL_ENABLED=false
python run.py your_config.aicl
```

## Troubleshooting

### No traces in Grafana

1. **Check endpoint**: Verify `OTEL_EXPORTER_OTLP_ENDPOINT` is reachable
2. **Verify auth**: Ensure `OTEL_EXPORTER_OTLP_HEADERS` has valid credentials
3. **Check console**: Look for "OTLP trace exporter configured" message
4. **Fallback**: If OTLP fails, system falls back to console export

### Spans not showing parent-child relationships

This is automatically handled by OpenTelemetry's context propagation. Verify:
- Using `with tracer.start_as_current_span()` context manager
- Same tracer instance throughout execution
- Not manually manipulating context

### High cardinality warnings

If Grafana shows cardinality warnings:
- Reduce resource names in span names
- Use attributes instead of span names for variable data
- Adjust sampling rate if needed
