# AICL Documentation

Complete documentation for tofu-aicl - Declarative AI Infrastructure Framework

## 📚 Quick Navigation

### Getting Started
- **[Setup Guide](SETUP.md)** - Installation, dependencies, API keys
- **[CLI Usage](CLI_USAGE.md)** - Command-line flags and examples
- **[Quick Start](../README.md)** - 5-minute introduction

### Core Concepts
- **[Declarative AI Workflows](concepts/declarative_ai_workflows.md)** - Infrastructure as Code for AI
- **[Test-Driven AI](concepts/test_driven_ai.md)** - Systematic experimentation

### Guides
- **[Experiment Builder](EXPERIMENT_BUILDER_GUIDE.md)** - Create custom experiments
- **[Experiment Testing](guides/EXPERIMENT_TESTING_GUIDE.md)** - Testing methodology
- **[Performance Optimization](guides/PERFORMANCE_OPTIMIZATIONS.md)** - Tuning and efficiency
- **[Provider Selection](guides/PROVIDER_SELECTION_ROADMAP.md)** - Choosing providers

### Architecture
- **[Overview](architecture/01_overview.md)** - System design
- **[Provider Protocol](architecture/02_provider_protocol.md)** - gRPC communication
- **[Core Engine](architecture/03_core_engine_design.md)** - Engine internals
- **[ADRs](adr/)** - Architecture decision records

### Integrations
- **[Azure OpenAI](AZURE_TERRAFORM_INTEGRATION.md)** - Enterprise integration
- **[Redmine](REDMINE_INTEGRATION.md)** - Project management
- **[OpenTelemetry](opentelemetry-setup.md)** - Observability

### Reference
- **[Experiment Status](EXPERIMENT_STATUS.md)** - Current experiments
- **[Integration Validation](INTEGRATION_VALIDATION.md)** - Provider testing
- **[Version 0.2.0 Summary](VERSION_0.2.0_SUMMARY.md)** - Latest release

## 📋 Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── SETUP.md                     # Installation and setup
├── CLI_USAGE.md                 # CLI reference
├── VERSION_0.2.0_SUMMARY.md     # Release notes
│
├── guides/                      # User guides
│   ├── EXPERIMENT_TESTING_GUIDE.md
│   ├── PERFORMANCE_OPTIMIZATIONS.md
│   ├── PROVIDER_SELECTION_ROADMAP.md
│   ├── COMPARISON_EXPERIMENTS.md
│   └── SELF_BUILD_SUMMARY.md
│
├── architecture/                # Architecture docs
│   ├── 01_overview.md
│   ├── 02_provider_protocol.md
│   └── 03_core_engine_design.md
│
├── concepts/                    # Conceptual guides
│   ├── declarative_ai_workflows.md
│   └── test_driven_ai.md
│
├── adr/                         # Architecture decisions
│   ├── 001_grpc_and_container_architecture.md
│   └── 002_provider_dependency_management.md
│
├── spec/                        # Technical specs (v1)
│   ├── 00-architecture.md
│   ├── 01-config.md
│   └── [05 more specs...]
│
├── v2.1/, v2.2/, v2.3/         # Version-specific docs
│
└── archive/                     # Historical docs
    ├── Old architecture plans
    ├── Migration guides
    └── Legacy validation reports
```

## 🚀 Common Tasks

### I want to...

**Install AICL**
→ See [SETUP.md](SETUP.md)

**Run my first experiment**
→ See [Quick Start](../README.md#quick-start)

**Understand CLI flags**
→ See [CLI_USAGE.md](CLI_USAGE.md)

**Create a custom experiment**
→ See [EXPERIMENT_BUILDER_GUIDE.md](EXPERIMENT_BUILDER_GUIDE.md)

**Debug provider issues**
→ See [INTEGRATION_VALIDATION.md](INTEGRATION_VALIDATION.md)

**Optimize performance**
→ See [guides/PERFORMANCE_OPTIMIZATIONS.md](guides/PERFORMANCE_OPTIMIZATIONS.md)

**Understand the architecture**
→ See [architecture/01_overview.md](architecture/01_overview.md)

**See what's new in v0.2.0**
→ See [VERSION_0.2.0_SUMMARY.md](VERSION_0.2.0_SUMMARY.md)

## 📖 Documentation by Audience

### For New Users
1. [README](../README.md) - Overview and quick start
2. [SETUP.md](SETUP.md) - Installation
3. [CLI_USAGE.md](CLI_USAGE.md) - Basic usage
4. [EXPERIMENT_BUILDER_GUIDE.md](EXPERIMENT_BUILDER_GUIDE.md) - First experiment

### For Developers
1. [Architecture Overview](architecture/01_overview.md)
2. [Provider Protocol](architecture/02_provider_protocol.md)
3. [Core Engine Design](architecture/03_core_engine_design.md)
4. [ADRs](adr/) - Design decisions
5. [../CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guide

### For Advanced Users
1. [Performance Optimization](guides/PERFORMANCE_OPTIMIZATIONS.md)
2. [Experiment Testing](guides/EXPERIMENT_TESTING_GUIDE.md)
3. [Provider Selection](guides/PROVIDER_SELECTION_ROADMAP.md)
4. [Integration Validation](INTEGRATION_VALIDATION.md)

### For Integration Partners
1. [Azure Integration](AZURE_TERRAFORM_INTEGRATION.md)
2. [Redmine Integration](REDMINE_INTEGRATION.md)
3. [External Codebase Index](EXTERNAL_CODEBASE_INDEX.md)

## 🔍 Finding Documentation

### By Topic

**Setup & Installation**
- [SETUP.md](SETUP.md) - Complete setup guide
- [CLI_USAGE.md](CLI_USAGE.md) - CLI reference

**Experiments**
- [EXPERIMENT_BUILDER_GUIDE.md](EXPERIMENT_BUILDER_GUIDE.md) - Building experiments
- [guides/EXPERIMENT_TESTING_GUIDE.md](guides/EXPERIMENT_TESTING_GUIDE.md) - Testing
- [guides/COMPARISON_EXPERIMENTS.md](guides/COMPARISON_EXPERIMENTS.md) - Comparisons
- [EXPERIMENT_STATUS.md](EXPERIMENT_STATUS.md) - Current status

**Architecture**
- [architecture/](architecture/) - System design
- [adr/](adr/) - Decision records
- [spec/](spec/) - Technical specifications

**Integrations**
- [AZURE_TERRAFORM_INTEGRATION.md](AZURE_TERRAFORM_INTEGRATION.md)
- [REDMINE_INTEGRATION.md](REDMINE_INTEGRATION.md)
- [opentelemetry-setup.md](opentelemetry-setup.md)

**Guides**
- [guides/PERFORMANCE_OPTIMIZATIONS.md](guides/PERFORMANCE_OPTIMIZATIONS.md)
- [guides/PROVIDER_SELECTION_ROADMAP.md](guides/PROVIDER_SELECTION_ROADMAP.md)
- [guides/SELF_BUILD_SUMMARY.md](guides/SELF_BUILD_SUMMARY.md)

### By Version

**v0.2.0 (Current)**
- [VERSION_0.2.0_SUMMARY.md](VERSION_0.2.0_SUMMARY.md) - Release summary
- [../CHANGELOG.md](../CHANGELOG.md) - Full changelog
- [CLI_USAGE.md](CLI_USAGE.md) - New CLI features

**v0.1.0**
- See [archive/](archive/) for historical docs

## 📝 Contributing to Docs

### Documentation Standards

1. **File Naming**
   - Use SCREAMING_SNAKE_CASE for major docs: `SETUP.md`
   - Use kebab-case for guides: `experiment-builder.md`
   - Number specs in order: `01-config.md`

2. **Structure**
   - Start with clear title (# heading)
   - Include table of contents for long docs
   - Use meaningful subheadings
   - Add code examples where relevant
   - Link to related documentation

3. **Location**
   - Core docs → `docs/`
   - Guides → `docs/guides/`
   - Architecture → `docs/architecture/`
   - Specs → `docs/spec/`
   - Old docs → `docs/archive/`

4. **Content**
   - Write for your audience (beginner/intermediate/advanced)
   - Include practical examples
   - Link to source code when relevant
   - Keep up to date with code changes

### Adding New Documentation

1. Create file in appropriate directory
2. Add to this README index
3. Link from related documentation
4. Update [../CHANGELOG.md](../CHANGELOG.md) if user-facing

## 🔗 External Resources

- **Repository**: https://github.com/zacharyelston/tofu-aicl
- **License**: GPL-3.0
- **Tests**: [../tests/](../tests/)
- **Examples**: [../experiments/](../experiments/)
- **Source**: [../src/](../src/)

## 📊 Documentation Health

| Category | Files | Status |
|----------|-------|--------|
| Getting Started | 3 | ✅ Complete |
| Guides | 5 | ✅ Complete |
| Architecture | 3 | ✅ Complete |
| Integrations | 3 | ✅ Complete |
| Reference | 4 | ✅ Complete |
| Specs (v1) | 8 | 📦 Archived |
| Version Docs | 3 | ✅ Complete |

**Last Updated**: October 13, 2025 (v0.2.0)
