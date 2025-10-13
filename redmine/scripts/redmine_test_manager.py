#!/usr/bin/env python3
"""
Redmine Test Manager
Watches for new test run issues and executes them
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from redminelib import Redmine
from redminelib.exceptions import ResourceNotFoundError

# Setup paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import test runners
from redmine.scripts.scenario_executor import ScenarioExecutor
from redmine.scripts.level_executor import LevelExecutor
from redmine.scripts.contract_executor import ContractExecutor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/redmine_manager.log')
    ]
)
logger = logging.getLogger(__name__)


class RedmineTestManager:
    """Manages test execution via Redmine issues"""
    
    def __init__(self, redmine_url: str, api_key: str, project_id: str):
        """Initialize manager"""
        self.redmine = Redmine(redmine_url, key=api_key)
        self.project_id = project_id
        
        # Cache tracker/status IDs
        self._tracker_ids = {}
        self._status_ids = {}
        self._load_ids()
        
        # Executors
        self.executors = {
            'v2.1': LevelExecutor(self.redmine),
            'v2.2': ContractExecutor(self.redmine),
            'v2.3': ScenarioExecutor(self.redmine)
        }
        
        logger.info(f"Initialized for project: {project_id}")
    
    def _load_ids(self):
        """Load and cache Redmine IDs"""
        # Trackers
        for tracker in self.redmine.tracker.all():
            self._tracker_ids[tracker.name.lower()] = tracker.id
        
        # Statuses
        for status in self.redmine.issue_status.all():
            self._status_ids[status.name.lower()] = status.id
        
        logger.info(f"Loaded {len(self._tracker_ids)} trackers, {len(self._status_ids)} statuses")
    
    def get_tracker_id(self, name: str) -> int:
        """Get tracker ID by name"""
        return self._tracker_ids.get(name.lower())
    
    def get_status_id(self, name: str) -> int:
        """Get status ID by name"""
        return self._status_ids.get(name.lower())
    
    def watch(self, interval: int = 30):
        """Main loop: watch for new test runs"""
        logger.info(f"Starting watch loop (interval: {interval}s)")
        
        while True:
            try:
                self._check_for_tests()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in watch loop: {e}", exc_info=True)
                time.sleep(interval)
    
    def _check_for_tests(self):
        """Check for new test runs"""
        try:
            # Find new test runs
            issues = self.redmine.issue.filter(
                project_id=self.project_id,
                tracker_id=self.get_tracker_id('test run'),
                status_id=self.get_status_id('new'),
                limit=10
            )
            
            for issue in issues:
                logger.info(f"Found new test: #{issue.id} - {issue.subject}")
                self.execute_test(issue)
                
        except Exception as e:
            logger.error(f"Error checking for tests: {e}")
    
    def execute_test(self, issue):
        """Execute a test run"""
        try:
            # Update status to queued
            issue.status_id = self.get_status_id('queued')
            issue.notes = "⏳ Test queued for execution..."
            issue.save()
            
            # Get parameters
            model = self._get_custom_field(issue, 'model_name')
            spec_version = self._get_custom_field(issue, 'spec_version')
            
            if not model or not spec_version:
                raise ValueError("Missing model_name or spec_version custom fields")
            
            logger.info(f"Executing: {model} with {spec_version}")
            
            # Update to running
            issue.status_id = self.get_status_id('running')
            issue.notes = f"🚀 Starting {model} test with {spec_version}..."
            issue.save()
            
            # Get executor
            executor = self.executors.get(spec_version)
            if not executor:
                raise ValueError(f"Unknown spec version: {spec_version}")
            
            # Execute
            results = executor.execute(issue, model, spec_version)
            
            # Post results
            self._post_success(issue, results)
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}", exc_info=True)
            self._post_failure(issue, str(e))
    
    def _get_custom_field(self, issue, field_name: str):
        """Get custom field value"""
        for field in issue.custom_fields:
            if field.name.lower().replace(' ', '_') == field_name.lower():
                return field.value
        return None
    
    def _post_success(self, issue, results: Dict):
        """Post successful results"""
        # Calculate grade
        grade = self._calculate_grade(results['total_score'], results['max_score'])
        
        # Format results
        notes = f"""
## ✅ Test Complete

**Score:** {results['total_score']} / {results['max_score']} ({results['percentage']:.1f}%)
**Grade:** {grade}
**Time:** {results['duration_minutes']} minutes

### Breakdown:
{self._format_results_table(results)}

### Attachments:
- execution_log.txt
- results_summary.json
- comparison_chart.png

### Next Steps:
- Review detailed results below
- Check failed items for improvement areas
- Compare with other model results
"""
        
        # Update issue
        issue.status_id = self.get_status_id('complete')
        issue.notes = notes
        
        # Update custom fields
        self._set_custom_field(issue, 'score', results['total_score'])
        self._set_custom_field(issue, 'execution_time', results['duration_minutes'])
        self._set_custom_field(issue, 'test_status', 'Complete')
        
        issue.save()
        
        # Attach files
        if 'attachments' in results:
            for attachment in results['attachments']:
                self._attach_file(issue, attachment)
        
        logger.info(f"Posted success for #{issue.id}: {results['total_score']}/{results['max_score']}")
    
    def _post_failure(self, issue, error: str):
        """Post failure"""
        notes = f"""
## ❌ Test Failed

**Error:** {error}

**Action Required:**
1. Check execution logs
2. Fix the issue
3. Update test status to 'New' to retry

**Support:**
Contact automation team if issue persists.
"""
        
        issue.status_id = self.get_status_id('failed')
        issue.notes = notes
        self._set_custom_field(issue, 'test_status', 'Failed')
        issue.save()
        
        logger.error(f"Posted failure for #{issue.id}: {error}")
    
    def _set_custom_field(self, issue, field_name: str, value):
        """Set custom field value"""
        # Redmine requires custom_fields list
        updated_fields = []
        for field in issue.custom_fields:
            if field.name.lower().replace(' ', '_') == field_name.lower():
                updated_fields.append({'id': field.id, 'value': value})
            else:
                updated_fields.append({'id': field.id, 'value': field.value})
        
        issue.custom_fields = updated_fields
    
    def _attach_file(self, issue, file_path: str):
        """Attach file to issue"""
        try:
            path = Path(file_path)
            if path.exists():
                with open(path, 'rb') as f:
                    issue.uploads = [{'path': str(path), 'filename': path.name}]
                logger.info(f"Attached {path.name} to #{issue.id}")
        except Exception as e:
            logger.error(f"Failed to attach {file_path}: {e}")
    
    def _calculate_grade(self, score: int, max_score: int) -> str:
        """Calculate letter grade"""
        percentage = (score / max_score) * 100
        
        if percentage >= 95:
            return "A+"
        elif percentage >= 90:
            return "A"
        elif percentage >= 85:
            return "B+"
        elif percentage >= 80:
            return "B"
        elif percentage >= 75:
            return "C+"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def _format_results_table(self, results: Dict) -> str:
        """Format results as markdown table"""
        if 'breakdown' not in results:
            return "No detailed breakdown available"
        
        table = "| Item | Score | Status |\n"
        table += "|------|-------|--------|\n"
        
        for item in results['breakdown']:
            status_icon = "✅" if item['passed'] else "❌"
            table += f"| {item['name']} | {item['score']}/{item['max']} | {status_icon} |\n"
        
        return table


def main():
    """Main entry point"""
    # Load config
    config_file = Path(__file__).parent.parent / 'config.json'
    
    if not config_file.exists():
        logger.error("Config file not found: config.json")
        logger.info("Copy config.example.json to config.json and update values")
        sys.exit(1)
    
    with open(config_file) as f:
        config = json.load(f)
    
    # Validate config
    required = ['redmine_url', 'api_key', 'project_id']
    for key in required:
        if key not in config:
            logger.error(f"Missing required config: {key}")
            sys.exit(1)
    
    # Create manager
    manager = RedmineTestManager(
        redmine_url=config['redmine_url'],
        api_key=config['api_key'],
        project_id=config['project_id']
    )
    
    # Start watching
    logger.info("Redmine Test Manager started")
    manager.watch(interval=config.get('watch_interval', 30))


if __name__ == "__main__":
    main()
