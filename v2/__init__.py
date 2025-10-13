"""
AICL v2 - Next Generation Architecture

Clean separation of concerns for CLI/Web split:
- storage/   - Pluggable storage backends (in-memory, SQLite, PostgreSQL)
- api/       - Shared experiment and grading logic
- cli/       - Free CLI tool
- schemas/   - Database schemas and migrations

V1 (current): Tightly coupled, SQLite-only
V2 (new):     Modular, storage-agnostic, supports both free CLI and paid web tiers
"""

__version__ = "2.0.0-alpha"
