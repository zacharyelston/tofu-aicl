import sys
import argparse
from aicl.core.engine import AICLEngine

def main():
    parser = argparse.ArgumentParser(description='AICL - Declarative AI Infrastructure Engine')
    parser.add_argument('config_path', nargs='?', default='example.aicl',
                       help='Path to AICL configuration file')
    parser.add_argument('--output-file', action='store_true',
                       help='Save experiment results to JSON file (default: enabled)')
    parser.add_argument('--output-docdb', action='store_true',
                       help='Save experiment results to PostgreSQL DocDB')
    parser.add_argument('--output-stdout', action='store_true', default=True,
                       help='Print experiment results to stdout (default: enabled)')
    parser.add_argument('--no-stdout', dest='output_stdout', action='store_false',
                       help='Disable stdout output')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimal console output (errors only)')
    parser.add_argument('--parallel', action='store_true',
                       help='Enable parallel execution for independent resources (experimental)')
    parser.add_argument('--experiment-id', type=str,
                       help='Custom experiment ID (default: derived from config file)')
    parser.add_argument('--tags', type=str,
                       help='Comma-separated tags for DocDB storage (e.g., rag,demo,v1)')
    
    args = parser.parse_args()
    
    # Create engine with output configuration
    engine = AICLEngine(
        config_path=args.config_path,
        output_file=args.output_file,
        output_docdb=args.output_docdb,
        output_stdout=args.output_stdout,
        quiet=args.quiet,
        parallel=args.parallel,
        experiment_id=args.experiment_id,
        tags=args.tags.split(',') if args.tags else None
    )
    engine.run()

if __name__ == "__main__":
    main()