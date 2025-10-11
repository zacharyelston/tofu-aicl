"""
v2 CLI - Free Command-Line Interface

The free tier CLI tool with optional database setup.
Default: in-memory storage (no persistence)
Optional: User-configured SQLite for persistence

Commands:
- aicl run        - Run experiments
- aicl setup-db   - Create SQLite database
- aicl export-schema - Export DB schema
- aicl stats      - Show statistics
"""

__version__ = "2.0.0-alpha"
