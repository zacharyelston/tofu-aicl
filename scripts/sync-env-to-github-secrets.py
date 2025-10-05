#!/usr/bin/env python3
"""
sync-env-to-github-secrets.py

Advanced Python script to sync .env file variables to GitHub repository secrets.
Supports environment filtering, validation, and batch operations.

Requirements:
    pip install requests python-dotenv
    GitHub CLI (gh) installed and authenticated
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from dotenv import dotenv_values
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests")
    sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


class GitHubSecretsSync:
    """Main class for syncing environment variables to GitHub secrets."""
    
    def __init__(self, args):
        self.env_file = args.file
        self.repo = args.repo
        self.dry_run = args.dry_run
        self.force = args.force
        self.include_patterns = args.include or []
        self.exclude_patterns = args.exclude or []
        self.prefix = args.prefix or ""
        self.validate_only = args.validate
        
    def log(self, level: str, message: str):
        """Log a message with color coding."""
        colors = {
            'INFO': Colors.BLUE,
            'SUCCESS': Colors.GREEN,
            'WARNING': Colors.YELLOW,
            'ERROR': Colors.RED,
            'DEBUG': Colors.PURPLE
        }
        color = colors.get(level, Colors.NC)
        print(f"{color}[{level}]{Colors.NC} {message}")
    
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        self.log('INFO', 'Checking prerequisites...')
        
        # Check GitHub CLI
        try:
            result = subprocess.run(['gh', '--version'], 
                                  capture_output=True, text=True, check=True)
            self.log('DEBUG', f'GitHub CLI version: {result.stdout.strip().split()[2]}')
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log('ERROR', 'GitHub CLI (gh) not found or not working')
            self.log('INFO', 'Install from: https://cli.github.com/')
            return False
        
        # Check GitHub CLI authentication
        try:
            subprocess.run(['gh', 'auth', 'status'], 
                         capture_output=True, check=True)
            self.log('DEBUG', 'GitHub CLI authentication verified')
        except subprocess.CalledProcessError:
            self.log('ERROR', 'GitHub CLI not authenticated')
            self.log('INFO', 'Run: gh auth login')
            return False
        
        # Check .env file
        if not Path(self.env_file).exists():
            self.log('ERROR', f'Environment file "{self.env_file}" not found')
            return False
        
        if not Path(self.env_file).is_file():
            self.log('ERROR', f'"{self.env_file}" is not a file')
            return False
        
        self.log('SUCCESS', 'Prerequisites check passed')
        return True
    
    def get_repository_info(self) -> Optional[str]:
        """Get repository information."""
        if self.repo:
            self.log('INFO', f'Using specified repository: {self.repo}')
            return self.repo
        
        # Try to detect from git remote
        try:
            result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'],
                                  capture_output=True, text=True, check=True)
            remote_url = result.stdout.strip()
            
            # Parse GitHub URL patterns
            patterns = [
                r'github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$',
                r'https://github\.com/([^/]+)/([^/.]+)(?:\.git)?/?$'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, remote_url)
                if match:
                    repo = f"{match.group(1)}/{match.group(2)}"
                    self.log('INFO', f'Detected repository: {repo}')
                    return repo
            
            self.log('WARNING', f'Could not parse GitHub URL: {remote_url}')
        except subprocess.CalledProcessError:
            self.log('WARNING', 'Not in a git repository or no origin remote')
        
        self.log('ERROR', 'Could not determine repository. Use --repo option.')
        return None
    
    def load_env_variables(self) -> Dict[str, str]:
        """Load and filter environment variables from .env file."""
        self.log('INFO', f'Loading environment variables from: {self.env_file}')
        
        try:
            # Use python-dotenv for robust parsing
            env_vars = dotenv_values(self.env_file)
        except Exception as e:
            self.log('ERROR', f'Failed to parse .env file: {e}')
            return {}
        
        if not env_vars:
            self.log('WARNING', 'No environment variables found')
            return {}
        
        # Apply filters
        filtered_vars = {}
        
        for key, value in env_vars.items():
            if value is None:  # Skip variables without values
                self.log('WARNING', f'Skipping variable with no value: {key}')
                continue
            
            # Apply include patterns
            if self.include_patterns:
                if not any(re.search(pattern, key) for pattern in self.include_patterns):
                    self.log('DEBUG', f'Excluding {key} (not in include patterns)')
                    continue
            
            # Apply exclude patterns
            if self.exclude_patterns:
                if any(re.search(pattern, key) for pattern in self.exclude_patterns):
                    self.log('DEBUG', f'Excluding {key} (matches exclude pattern)')
                    continue
            
            # Apply prefix
            secret_name = f"{self.prefix}{key}" if self.prefix else key
            filtered_vars[secret_name] = value
            self.log('DEBUG', f'Including variable: {key} -> {secret_name}')
        
        self.log('SUCCESS', f'Loaded {len(filtered_vars)} environment variables')
        return filtered_vars
    
    def validate_variables(self, env_vars: Dict[str, str]) -> List[str]:
        """Validate environment variables for GitHub secrets."""
        issues = []
        
        for key, value in env_vars.items():
            # Check secret name format
            if not re.match(r'^[A-Z][A-Z0-9_]*$', key):
                issues.append(f"Secret name '{key}' should be uppercase with underscores")
            
            # Check for potentially sensitive patterns
            sensitive_patterns = [
                (r'localhost|127\.0\.0\.1', 'Contains localhost reference'),
                (r'\.local|\.dev', 'Contains local development domain'),
                (r'/tmp/|/var/tmp/', 'Contains temporary file path'),
                (r'password.*123|admin.*admin', 'Contains weak credentials')
            ]
            
            for pattern, message in sensitive_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    issues.append(f"Variable '{key}': {message}")
            
            # Check value length (GitHub has limits)
            if len(value) > 65536:  # 64KB limit
                issues.append(f"Variable '{key}' exceeds GitHub's 64KB limit")
        
        return issues
    
    def get_existing_secrets(self) -> List[str]:
        """Get list of existing secrets in the repository."""
        try:
            result = subprocess.run(['gh', 'secret', 'list', '--repo', self.repo],
                                  capture_output=True, text=True, check=True)
            
            secrets = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Parse secret name from gh output format
                    secret_name = line.split()[0]
                    secrets.append(secret_name)
            
            return secrets
        except subprocess.CalledProcessError as e:
            self.log('ERROR', f'Failed to get existing secrets: {e}')
            return []
    
    def set_secret(self, name: str, value: str, existing_secrets: List[str]) -> bool:
        """Set a single GitHub secret."""
        if self.dry_run:
            action = "UPDATE" if name in existing_secrets else "CREATE"
            self.log('INFO', f'[DRY RUN] Would {action} secret: {name}')
            return True
        
        # Check if secret exists
        if name in existing_secrets:
            if not self.force:
                response = input(f"Secret '{name}' exists. Overwrite? (y/N): ")
                if response.lower() != 'y':
                    self.log('INFO', f'Skipping {name}')
                    return True
            self.log('INFO', f'Updating existing secret: {name}')
        else:
            self.log('INFO', f'Creating new secret: {name}')
        
        try:
            # Use gh CLI to set secret
            process = subprocess.Popen(['gh', 'secret', 'set', name, '--repo', self.repo],
                                     stdin=subprocess.PIPE, text=True)
            process.communicate(input=value)
            
            if process.returncode == 0:
                self.log('SUCCESS', f'Successfully set secret: {name}')
                return True
            else:
                self.log('ERROR', f'Failed to set secret: {name}')
                return False
        except Exception as e:
            self.log('ERROR', f'Error setting secret {name}: {e}')
            return False
    
    def run(self) -> int:
        """Main execution method."""
        self.log('INFO', 'Starting GitHub secrets sync...')
        
        # Check prerequisites
        if not self.check_prerequisites():
            return 1
        
        # Get repository info
        repo = self.get_repository_info()
        if not repo:
            return 1
        self.repo = repo
        
        # Load environment variables
        env_vars = self.load_env_variables()
        if not env_vars:
            return 0
        
        # Validate variables
        validation_issues = self.validate_variables(env_vars)
        if validation_issues:
            self.log('WARNING', 'Validation issues found:')
            for issue in validation_issues:
                self.log('WARNING', f'  - {issue}')
            
            if self.validate_only:
                return 1 if validation_issues else 0
            
            if not self.force:
                response = input('Continue despite validation issues? (y/N): ')
                if response.lower() != 'y':
                    return 1
        
        if self.validate_only:
            self.log('SUCCESS', 'Validation passed')
            return 0
        
        # Get existing secrets
        existing_secrets = self.get_existing_secrets()
        
        # Confirm operation
        if not self.dry_run and not self.force:
            print(f"\n{Colors.YELLOW}This will upload {len(env_vars)} secrets to {repo}{Colors.NC}")
            print(f"{Colors.YELLOW}Secrets will be accessible to repository collaborators{Colors.NC}")
            response = input('Continue? (y/N): ')
            if response.lower() != 'y':
                self.log('INFO', 'Operation cancelled')
                return 0
        
        # Process secrets
        success_count = 0
        error_count = 0
        
        for name, value in env_vars.items():
            if self.set_secret(name, value, existing_secrets):
                success_count += 1
            else:
                error_count += 1
        
        # Summary
        print()
        self.log('SUCCESS', 'Sync completed!')
        self.log('INFO', f'Successfully processed: {success_count}')
        if error_count > 0:
            self.log('WARNING', f'Errors encountered: {error_count}')
        
        if not self.dry_run:
            self.log('INFO', f'View secrets at: https://github.com/{repo}/settings/secrets/actions')
        
        return 1 if error_count > 0 else 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sync .env file variables to GitHub repository secrets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Sync .env to current repo
  %(prog)s --file .env.prod --repo org/repo  # Sync specific file
  %(prog)s --dry-run                         # Preview changes
  %(prog)s --include "API_.*" --exclude "LOCAL_.*"  # Filter variables
  %(prog)s --prefix "PROD_"                  # Add prefix to secret names
  %(prog)s --validate                        # Only validate, don't sync
        """
    )
    
    parser.add_argument('-f', '--file', default='.env',
                       help='Path to .env file (default: .env)')
    parser.add_argument('-r', '--repo',
                       help='GitHub repository (owner/repo format)')
    parser.add_argument('-d', '--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--force', action='store_true',
                       help='Overwrite existing secrets without confirmation')
    parser.add_argument('--include', action='append',
                       help='Include only variables matching regex pattern (can be used multiple times)')
    parser.add_argument('--exclude', action='append',
                       help='Exclude variables matching regex pattern (can be used multiple times)')
    parser.add_argument('--prefix',
                       help='Add prefix to all secret names')
    parser.add_argument('--validate', action='store_true',
                       help='Only validate variables, don\'t sync')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Create and run sync
    sync = GitHubSecretsSync(args)
    return sync.run()


if __name__ == '__main__':
    sys.exit(main())
