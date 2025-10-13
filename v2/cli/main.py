"""
AICL v2 CLI - Free Command-Line Interface

Entry point for the free CLI tool.
Supports in-memory storage (default) or user-configured SQLite.
"""

import argparse
import sys
from pathlib import Path

from v2.storage import InMemoryStorage, SQLiteStorage
from v2.api import ExperimentRunner


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='aicl',
        description='AICL v2 - Declarative AI Infrastructure (Free CLI)'
    )
    
    # Global options
    parser.add_argument('--db', help='Path to SQLite database (optional, for persistence)')
    parser.add_argument('--version', action='version', version='%(prog)s 2.0.0-alpha')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run experiments')
    run_parser.add_argument('configs', nargs='+', help='AICL config files to run')
    run_parser.add_argument('--parallel', action='store_true', help='Run in parallel')
    run_parser.add_argument('--max-workers', type=int, default=4, help='Parallel workers')
    
    # Setup DB command
    setup_parser = subparsers.add_parser('setup-db', help='Create SQLite database')
    setup_parser.add_argument('--path', default='experiments/results.db', help='Database path')
    
    # Export schema command
    export_parser = subparsers.add_parser('export-schema', help='Export database schema')
    export_parser.add_argument('--format', choices=['sql', 'stub'], default='sql', help='Export format')
    export_parser.add_argument('--output', help='Output file (default: stdout)')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show experiment statistics')
    
    args = parser.parse_args()
    
    # Show help if no command
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize storage
    if args.db:
        try:
            storage = SQLiteStorage(args.db)
            print(f"📁 Using SQLite: {args.db}")
        except ValueError as e:
            print(f"❌ {e}")
            return 1
    else:
        storage = InMemoryStorage()
        print(f"💡 Using in-memory storage (session only)")
        print(f"   To persist results: aicl setup-db --path my.db")
        print()
    
    # Execute command
    if args.command == 'run':
        return cmd_run(args, storage)
    elif args.command == 'setup-db':
        return cmd_setup_db(args)
    elif args.command == 'export-schema':
        return cmd_export_schema(args)
    elif args.command == 'stats':
        return cmd_stats(args, storage)
    
    return 0


def cmd_run(args, storage):
    """Run experiments command"""
    runner = ExperimentRunner(storage=storage)
    
    print(f"🚀 Running {len(args.configs)} experiments...")
    # TODO: Implement experiment execution
    print("⏳ Experiment execution coming in Phase 2")
    
    return 0


def cmd_setup_db(args):
    """Setup database command"""
    db_path = Path(args.path)
    
    if db_path.exists():
        response = input(f"⚠️  Database {db_path} already exists. Recreate? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return 1
        # Remove existing DB to recreate
        db_path.unlink()
    
    # Create database (use create_if_missing=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    storage = SQLiteStorage(str(db_path), create_if_missing=True)
    
    print(f"✅ Created database: {db_path}")
    print(f"   Schema version: {storage.get_schema_version()}")
    print(f"\nUsage:")
    print(f"  python -m v2.cli.main run experiments/*.aicl --db {db_path}")
    
    return 0


def cmd_export_schema(args):
    """Export schema command"""
    # TODO: Implement schema export
    print("📄 Schema export coming in Phase 2")
    return 0


def cmd_stats(args, storage):
    """Show statistics command"""
    stats = storage.get_cost_analysis()
    
    print("\n📊 Experiment Statistics")
    print("━" * 40)
    print(f"  Total Experiments: {stats['total_experiments']}")
    print(f"  Total Cost:        ${stats['total_spent']:.4f}")
    print(f"  Average Cost:      ${stats['avg_cost']:.4f}")
    print("━" * 40)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
