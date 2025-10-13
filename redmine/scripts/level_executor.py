#!/usr/bin/env python3
"""
Progressive Level Test Executor (v2.1)
Executes progressive level tests and reports to Redmine
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class LevelExecutor:
    """Execute progressive level tests (v2.1)"""
    
    def __init__(self, redmine):
        self.redmine = redmine
        self.levels_dir = Path(__file__).parent.parent.parent / 'docs' / 'v2.1'
    
    def execute(self, parent_issue, model: str, spec_version: str) -> Dict:
        """Execute all levels"""
        logger.info(f"Executing levels for {model}")
        
        start_time = datetime.now()
        
        # Load levels
        levels = self._load_levels()
        
        # Create child issues
        child_issues = self._create_child_issues(parent_issue, model, levels)
        
        # Execute each level
        results = []
        total_score = 0
        max_score = 0
        
        for level, child_issue in zip(levels, child_issues):
            logger.info(f"Running level {level['id']}: {level['name']}")
            
            result = self._run_level(child_issue, model, level)
            results.append(result)
            
            total_score += result['score']
            max_score += level['max_points']
            
            # Stop if level failed (progressive dependency)
            if not result['passed']:
                logger.warning(f"Level {level['id']} failed, skipping remaining levels")
                # Mark remaining levels as skipped
                for remaining_level, remaining_issue in zip(levels[level['id']:], child_issues[level['id']:]):
                    if remaining_issue and remaining_issue != child_issue:
                        self._mark_skipped(remaining_issue, remaining_level)
                        results.append({
                            'name': remaining_level['name'],
                            'score': 0,
                            'max': remaining_level['max_points'],
                            'passed': False,
                            'skipped': True
                        })
                        max_score += remaining_level['max_points']
                break
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds() / 60
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': (total_score / max_score * 100) if max_score > 0 else 0,
            'duration_minutes': round(duration, 2),
            'breakdown': results,
            'attachments': [
                'logs/level_execution.log',
                'results/level_summary.json'
            ]
        }
    
    def _load_levels(self) -> List[Dict]:
        """Load level definitions"""
        levels = [
            {'id': 1, 'name': 'Foundation', 'max_points': 40},
            {'id': 2, 'name': 'Execution', 'max_points': 50},
            {'id': 3, 'name': 'CLI', 'max_points': 40},
            {'id': 4, 'name': 'Polish', 'max_points': 20}
        ]
        return levels
    
    def _create_child_issues(self, parent_issue, model: str, levels: List[Dict]) -> List:
        """Create child issues for each level"""
        child_issues = []
        
        for level in levels:
            try:
                child = self.redmine.issue.create(
                    project_id=parent_issue.project.id,
                    tracker_id=self._get_tracker_id('level test'),
                    subject=f"{model} - Level {level['id']}: {level['name']}",
                    parent_issue_id=parent_issue.id,
                    description=f"Progressive Level {level['id']}: {level['name']} ({level['max_points']} points)",
                    custom_fields=[
                        {'id': self._get_field_id('max_points'), 'value': level['max_points']},
                        {'id': self._get_field_id('model'), 'value': model}
                    ]
                )
                child_issues.append(child)
                logger.info(f"Created child issue #{child.id} for level {level['id']}")
            except Exception as e:
                logger.error(f"Failed to create child issue: {e}")
                child_issues.append(None)
        
        return child_issues
    
    def _run_level(self, issue, model: str, level: Dict) -> Dict:
        """Run a single level"""
        if issue is None:
            return {
                'name': level['name'],
                'score': 0,
                'max': level['max_points'],
                'passed': False,
                'error': 'Failed to create issue'
            }
        
        # Update status
        issue.status_id = self._get_status_id('running')
        issue.notes = f"⏳ Executing Level {level['id']}: {level['name']}..."
        issue.save()
        
        try:
            # Run level test
            result = self._execute_level_tests(level, model)
            
            # Determine pass/fail
            passed = result['score'] >= level['max_points'] * 0.8
            
            # Update issue with results
            issue.status_id = self._get_status_id('complete' if passed else 'failed')
            issue.notes = f"""
## {"✅" if passed else "❌"} Level {level['id']}: {level['name']}

**Score:** {result['score']} / {level['max_points']}
**Status:** {"PASSED" if passed else "FAILED"}

### Components Tested:
{self._format_components(result.get('components', []))}

### Details:
{result.get('details', 'No details available')}

{"### Next Level:" if passed else "### Issue:"}
{result.get('next_steps', 'Review implementation') if passed else result.get('failure_reason', 'See logs for details')}
"""
            
            # Update custom field
            for field in issue.custom_fields:
                if field.name.lower() == 'score':
                    issue.custom_fields = [{'id': field.id, 'value': result['score']}]
                    break
            
            issue.save()
            
            return {
                'name': level['name'],
                'score': result['score'],
                'max': level['max_points'],
                'passed': passed
            }
            
        except Exception as e:
            logger.error(f"Level {level['id']} failed: {e}", exc_info=True)
            
            issue.status_id = self._get_status_id('failed')
            issue.notes = f"## ❌ Execution Error\n\n{str(e)}"
            issue.save()
            
            return {
                'name': level['name'],
                'score': 0,
                'max': level['max_points'],
                'passed': False,
                'error': str(e)
            }
    
    def _mark_skipped(self, issue, level: Dict):
        """Mark level as skipped"""
        issue.status_id = self._get_status_id('failed')
        issue.notes = f"""
## ⏭️ Level {level['id']}: {level['name']} - SKIPPED

**Reason:** Previous level failed

Progressive complexity testing requires each level to pass before proceeding.
Since a previous level failed, this level was not executed.

**To Test This Level:**
1. Fix issues in previous level(s)
2. Rerun test from beginning
"""
        issue.save()
    
    def _execute_level_tests(self, level: Dict, model: str) -> Dict:
        """Execute tests for a level"""
        # Mock implementation - replace with actual test execution
        import random
        
        components = self._get_level_components(level['id'])
        score = random.randint(
            int(level['max_points'] * 0.7),
            level['max_points']
        )
        
        return {
            'score': score,
            'components': [
                {'name': comp, 'passed': score >= level['max_points'] * 0.8}
                for comp in components
            ],
            'details': f"Level {level['id']} execution completed",
            'next_steps': 'Proceed to next level' if score >= level['max_points'] * 0.8 else None,
            'failure_reason': 'Score below passing threshold' if score < level['max_points'] * 0.8 else None
        }
    
    def _get_level_components(self, level_id: int) -> List[str]:
        """Get components for a level"""
        components_map = {
            1: ['config.py', 'logging_setup.py'],
            2: ['docker.py', 'local.py'],
            3: ['run.py', 'aicl_modular'],
            4: ['output.py', 'state.py']
        }
        return components_map.get(level_id, [])
    
    def _format_components(self, components: List[Dict]) -> str:
        """Format component results"""
        if not components:
            return "No component details available"
        
        lines = []
        for comp in components:
            icon = "✅" if comp['passed'] else "❌"
            lines.append(f"- {icon} {comp['name']}")
        
        return '\n'.join(lines)
    
    def _get_tracker_id(self, name: str) -> int:
        """Get tracker ID"""
        for tracker in self.redmine.tracker.all():
            if tracker.name.lower() == name.lower():
                return tracker.id
        return 1
    
    def _get_status_id(self, name: str) -> int:
        """Get status ID"""
        for status in self.redmine.issue_status.all():
            if status.name.lower() == name.lower():
                return status.id
        return 1
    
    def _get_field_id(self, name: str) -> int:
        """Get custom field ID"""
        field_map = {
            'max_points': 2,
            'model': 3,
            'score': 4
        }
        return field_map.get(name, 0)
