#!/usr/bin/env python3
"""
Test connection to Redmica server
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_env():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    else:
        print(f"⚠️  No .env file found at {env_file}")

def test_connection():
    """Test connection to Redmica server"""
    
    # Load environment
    load_env()
    
    # Get credentials
    redmine_url = os.getenv('REDMINE_URL', 'http://localhost:3000')
    api_key = os.getenv('REDMINE_API_KEY')
    
    if not api_key:
        print("❌ REDMINE_API_KEY not found in environment")
        print("\nPlease add to /Users/zacelston/code/tofu-aicl/.env:")
        print("REDMINE_URL=http://your-redmica-server:3000")
        print("REDMINE_API_KEY=your_api_key_here")
        return False
    
    print(f"Testing Redmica connection...")
    print(f"URL: {redmine_url}")
    print(f"API Key: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        from redminelib import Redmine
    except ImportError:
        print("\n❌ python-redmine not installed")
        print("Install with: pip install python-redmine")
        return False
    
    try:
        # Connect
        redmine = Redmine(redmine_url, key=api_key)
        
        # Test connection by getting current user
        user = redmine.user.get('current')
        
        print(f"\n✅ Connection successful!")
        print(f"Connected as: {user.firstname} {user.lastname} ({user.login})")
        print(f"Email: {user.mail}")
        print(f"Admin: {user.admin}")
        
        # Try to list projects
        try:
            projects = redmine.project.all(limit=5)
            print(f"\n📁 First 5 projects:")
            for project in projects:
                print(f"  - {project.name} ({project.identifier})")
        except Exception as e:
            print(f"\n⚠️  Could not list projects: {e}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nPlease verify:")
        print("1. Redmica server is running")
        print("2. URL is correct")
        print("3. API key is valid")
        print("4. API is enabled in Redmica settings")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
