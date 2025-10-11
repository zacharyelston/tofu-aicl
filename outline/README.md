# tofu-aicl Technical Specifications

This directory contains complete technical specifications for rebuilding the tofu-aicl framework in any programming language.

## Overview

tofu-aicl is a declarative AI infrastructure framework ("Terraform for AI") that enables ephemeral, just-in-time provisioning of AI workflows through Infrastructure-as-Code using HCL syntax.

## Specification Documents

### Foundation
- **[01-vision-and-goals.md](01-vision-and-goals.md)** - Project vision, value propositions, target users, success criteria
- **[02-architecture-overview.md](02-architecture-overview.md)** - High-level architecture, patterns, execution flow

### Core Components
- **[03-core-components.md](03-core-components.md)** - Parser, Evaluator, Planner, Executor, State Manager, Provider Registry
- **[04-provider-system.md](04-provider-system.md)** - gRPC provider architecture, lifecycle, implementation guide

### Configuration & APIs
- **[05-configuration-format.md](05-configuration-format.md)** - HCL syntax, block types, interpolation, complete examples
- **[06-api-specifications.md](06-api-specifications.md)** - gRPC APIs, resource types, CLI commands, REST endpoints

### Data & Storage
- **[07-data-models.md](07-data-models.md)** - Model catalog, state files, database schemas, metrics
- **[08-storage-layer.md](08-storage-layer.md)** - Storage abstraction, implementations (memory/SQLite/PostgreSQL)

### Advanced Features
- **[09-experiment-system.md](09-experiment-system.md)** - Matrix experiments, template system, LLM-as-Judge grading
- **[10-deployment-model.md](10-deployment-model.md)** - Dual-tier business model, CLI vs Web, deployment platforms

### Implementation
- **[11-implementation-guide.md](11-implementation-guide.md)** - Step-by-step implementation guide, testing, deployment
- **[12-directory-structure.md](12-directory-structure.md)** - Complete file/folder layout, configuration files

## Reading Order

### For Product Managers
1. Vision and Goals (01)
2. Architecture Overview (02)
3. Deployment Model (10)

### For Architects
1. Architecture Overview (02)
2. Core Components (03)
3. Provider System (04)
4. Storage Layer (08)

### For Developers
1. Implementation Guide (11) - **Start here**
2. Core Components (03)
3. Provider System (04)
4. Configuration Format (05)
5. API Specifications (06)
6. Directory Structure (12)

### For DevOps/Platform Engineers
1. Deployment Model (10)
2. Storage Layer (08)
3. Directory Structure (12)

## Key Design Principles

1. **Configuration as Data** - Externalize metadata to YAML/HCL, not hardcoded
2. **Single Source of Truth** - No duplication (e.g., centralized model catalog)
3. **Fail-Fast Validation** - Schema validation at load time
4. **Auto-Discovery** - Convention over configuration (drop-in providers)
5. **Provider Abstraction** - Unified interface for heterogeneous services
6. **Observability First** - Tracing and metrics built-in
7. **Test-Driven AI** - Matrix experiments for systematic testing

## Language Implementation Notes

### Python (Current)
- HCL: `python-hcl2`
- gRPC: `grpcio`, `grpcio-tools`
- Concurrency: `concurrent.futures.ThreadPoolExecutor`
- Storage: `sqlite3`, `psycopg2`

### Go (Recommended for Performance)
- HCL: `hashicorp/hcl`
- gRPC: `google.golang.org/grpc`
- Concurrency: Goroutines + channels
- Storage: `database/sql`

### TypeScript/Node.js (For Web Integration)
- HCL: `js-hcl-parser` or custom parser
- gRPC: `@grpc/grpc-js`
- Concurrency: `Promise.all()`, async/await
- Storage: `sqlite3`, `pg`

### Rust (For Maximum Performance)
- HCL: `hcl-rs`
- gRPC: `tonic`
- Concurrency: Tokio async runtime
- Storage: `rusqlite`, `tokio-postgres`

## Quick Start for Rebuilding

1. **Read**: Implementation Guide (11)
2. **Set Up**: Follow Phase 1 (Core Engine MVP)
3. **Build**: Parser → Evaluator → Planner → Executor
4. **Test**: Unit tests at each phase
5. **Extend**: Add providers (Phase 2)
6. **Enhance**: Storage, experiments, CLI (Phases 3-6)

## Support

For questions about these specifications:
- Open an issue on GitHub
- Check existing documentation
- Review example implementations

## License

These specifications are released under the same license as the tofu-aicl project.

---

**Version**: 1.0.0  
**Last Updated**: October 11, 2025  
**Status**: Complete & Production-Ready
