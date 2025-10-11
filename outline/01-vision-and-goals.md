# Vision and Goals

## Project Vision
tofu-aicl is the "Terraform for AI workflows" - a declarative infrastructure framework that enables ephemeral, just-in-time provisioning of AI systems through Infrastructure-as-Code.

## Core Value Propositions

### 1. Declarative Configuration
- Define AI pipelines in HCL (HashiCorp Configuration Language)
- Version control your AI infrastructure
- Reproducible, auditable workflows

### 2. Test-Driven AI Development
- Matrix experiments for systematic testing
- A/B testing for model selection
- Algorithmic experimentation with metrics
- Compare performance across configurations

### 3. Provider Abstraction
- Unified interface for heterogeneous AI services
- Swap providers without changing workflow logic
- Multi-cloud, multi-vendor support

### 4. Built-in Observability
- OpenTelemetry distributed tracing
- Cost tracking per execution
- Performance metrics (latency, tokens)
- Quality scoring with LLM-as-Judge

### 5. Dual-Tier Business Model
- **Free CLI**: Local execution, in-memory/SQLite storage
- **Paid Web**: Managed SaaS, PostgreSQL, collaboration features

## Target Users

### Primary: AI Engineers
- Building RAG pipelines
- Evaluating LLM providers
- Optimizing prompt templates
- Running systematic experiments

### Secondary: ML Researchers
- Comparing embedding models
- Testing retrieval strategies
- Benchmarking AI systems

### Tertiary: DevOps/Platform Teams
- Deploying AI infrastructure
- Managing API costs
- Enforcing governance policies

## Success Criteria

### Technical
- Parse 100% of valid HCL configurations
- <2 second provider startup time
- Support 10+ concurrent experiments
- 99.9% test coverage

### Business
- Free tier: Acquire 1000+ developers in first 6 months
- Paid tier: 10% conversion rate
- Ecosystem: 20+ community-contributed providers

### User Experience
- Single command to run experiments
- Clear, actionable metrics
- Simple provider addition (drop-in config files)
