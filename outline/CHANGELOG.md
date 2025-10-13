# Specification Changelog

## Version 1.1.0 (October 13, 2025)

### New Features

#### CLI Output Control
- **Multiple Output Destinations**: Added support for independent output destinations
  - JSON state files (`--output-file`)
  - PostgreSQL DocDB (`--output-docdb`)
  - Stdout console (`--output-stdout`)
  - Quiet mode (`--quiet`)
  - Disable stdout (`--no-stdout`)

#### PostgreSQL DocDB (Document Database)
- **JSONB Storage**: Complete experiment outputs stored in PostgreSQL JSONB format
- **Rich Metadata**: Support for experiment metadata and custom fields
- **Tagging System**: Tag experiments for organization and filtering
- **Powerful Querying**: JSON path queries, aggregations, comparisons
- **CLI Integration**: Seamless integration with `--output-docdb` flag

#### Experiment Metadata
- **Custom IDs**: `--experiment-id` flag for custom experiment identifiers
- **Tagging**: `--tags` flag for comma-separated tags
- **Organized Storage**: Better experiment organization and retrieval

### Updated Specifications

#### 06-api-specifications.md
- Added comprehensive CLI flags documentation
- Added output control flags (v0.2.0+)
- Added experiment metadata flags
- Added multiple output destination examples
- Added output routing architecture

#### 08-storage-layer.md
- Added PostgreSQL DocDB section
- Added JSONB schema for experiment_runs table
- Added ExperimentDocDB implementation
- Added JSONB querying examples
- Added CLI integration examples

#### 11-implementation-guide.md
- Updated Phase 6 with CLI output control
- Added OutputManager pattern for routing outputs
- Added argparse configuration examples
- Added integration examples

#### 00-INDEX.md
- Updated version to 1.1.0
- Added v1.1.0 changelog
- Preserved v1.0.0 changelog

#### README.md
- Updated version to 1.1.0
- Added "What's New in v1.1.0" section
- Updated last modified date

### Implementation Notes

**Backward Compatibility**: 100% backward compatible with v1.0.0
- All existing configurations work unchanged
- Default behavior preserved (stdout + file output)
- New flags are optional

**Database Requirements**:
- PostgreSQL DocDB feature requires `DATABASE_URL` environment variable
- Falls back gracefully if not configured
- Works with Replit PostgreSQL, Supabase, Neon, etc.

**CLI Enhancements**:
- Argparse used for argument parsing (Python stdlib)
- Support for flag grouping (output, metadata, execution)
- Flexible output routing architecture

### Migration from v1.0.0

No migration required. v1.1.0 is a drop-in replacement with additional features.

To use new features:
```bash
# Enable DocDB output
export DATABASE_URL="postgresql://user:pass@host/db"
python run.py config.aicl --output-docdb

# Add tags for organization
python run.py config.aicl --tags rag,demo,production

# Custom experiment ID
python run.py config.aicl --experiment-id my-test-001
```

### Testing Coverage

New tests added:
- 20 CLI tests covering all output modes
- Output destination routing tests
- DocDB integration tests
- Argparse configuration tests

All tests passing ✅

---

## Version 1.0.0 (October 11, 2025)

### Initial Release

- Complete specification suite (13 documents)
- Language-agnostic implementation guide
- gRPC provider architecture
- HCL configuration format
- Storage layer abstraction (Memory/SQLite/PostgreSQL)
- Matrix experiment system
- LLM-as-Judge evaluation
- Self-modification experiments
- OpenTelemetry observability
- Dual-tier business model (free CLI / paid Web)

### Documents Published

1. Vision and Goals
2. Architecture Overview
3. Core Components
4. Provider System
5. Configuration Format
6. API Specifications
7. Data Models
8. Storage Layer
9. Experiment System
10. Deployment Model
11. Implementation Guide
12. Directory Structure
13. Self-Modification Experiments

---

## Future Roadmap

### Version 1.2.0 (Planned)
- REST API specifications
- Web dashboard specifications
- Multi-user authentication
- Team collaboration features
- Advanced experiment comparison
- Cost optimization algorithms

### Version 2.0.0 (Planned)
- Native Go implementation
- Performance optimizations
- Advanced caching strategies
- Distributed execution
- Cloud-native deployment
