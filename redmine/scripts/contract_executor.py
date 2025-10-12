#!/usr/bin/env python3
"""
Contract-Based Test Executor (v2.2)
Executes behavior contract tests and reports to Redmine
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class ContractExecutor:
    """Execute contract-based tests (v2.2)"""
    
    def __init__(self, redmine):
        self.redmine = redmine
        self.contracts_dir = Path(__file__).parent.parent.parent / 'docs' / 'v2.2'
    
    def execute(self, parent_issue, model: str, spec_version: str) -> Dict:
        """Execute all contracts"""
        logger.info(f"Executing contracts for {model}")
        
        start_time = datetime.now()
        
        # Load contracts
        contracts = self._load_contracts()
        
        # Create child issues
        child_issues = self._create_child_issues(parent_issue, model, contracts)
        
        # Execute each contract (all independent)
        results = []
        total_score = 0
        max_score = 0
        
        for contract, child_issue in zip(contracts, child_issues):
            logger.info(f"Testing contract: {contract['name']}")
            
            result = self._test_contract(child_issue, model, contract)
            results.append(result)
            
            total_score += result['score']
            max_score += contract['max_points']
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds() / 60
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': (total_score / max_score * 100) if max_score > 0 else 0,
            'duration_minutes': round(duration, 2),
            'breakdown': results,
            'attachments': [
                'logs/contract_execution.log',
                'results/contract_summary.json'
            ]
        }
    
    def _load_contracts(self) -> List[Dict]:
        """Load contract definitions"""
        contracts = [
            {'id': 1, 'name': 'Configuration', 'max_points': 25},
            {'id': 2, 'name': 'Logging', 'max_points': 15},
            {'id': 3, 'name': 'Docker Execution', 'max_points': 30},
            {'id': 4, 'name': 'Local Execution', 'max_points': 20},
            {'id': 5, 'name': 'CLI Interface', 'max_points': 30},
            {'id': 6, 'name': 'State Management', 'max_points': 20},
            {'id': 7, 'name': 'Error Handling', 'max_points': 10}
        ]
        return contracts
    
    def _create_child_issues(self, parent_issue, model: str, contracts: List[Dict]) -> List:
        """Create child issues for each contract"""
        child_issues = []
        
        for contract in contracts:
            try:
                child = self.redmine.issue.create(
                    project_id=parent_issue.project.id,
                    tracker_id=self._get_tracker_id('contract test'),
                    subject=f"{model} - Contract: {contract['name']}",
                    parent_issue_id=parent_issue.id,
                    description=f"Behavior Contract: {contract['name']} ({contract['max_points']} points)",
                    custom_fields=[
                        {'id': self._get_field_id('max_points'), 'value': contract['max_points']},
                        {'id': self._get_field_id('model'), 'value': model}
                    ]
                )
                child_issues.append(child)
                logger.info(f"Created child issue #{child.id} for contract {contract['id']}")
            except Exception as e:
                logger.error(f"Failed to create child issue: {e}")
                child_issues.append(None)
        
        return child_issues
    
    def _test_contract(self, issue, model: str, contract: Dict) -> Dict:
        """Test a single contract"""
        if issue is None:
            return {
                'name': contract['name'],
                'score': 0,
                'max': contract['max_points'],
                'passed': False,
                'error': 'Failed to create issue'
            }
        
        # Update status
        issue.status_id = self._get_status_id('running')
        issue.notes = f"⏳ Testing contract: {contract['name']}..."
        issue.save()
        
        try:
            # Execute contract tests
            result = self._execute_contract_tests(contract, model)
            
            # Contracts are pass/fail (all behaviors must pass)
            passed = result['score'] == contract['max_points']
            
            # Update issue with results
            issue.status_id = self._get_status_id('complete' if passed else 'failed')
            issue.notes = f"""
## {"✅" if passed else "❌"} Contract: {contract['name']}

**Score:** {result['score']} / {contract['max_points']}
**Status:** {"FULFILLED" if passed else "VIOLATED"}

### Behaviors Tested:
{self._format_behaviors(result.get('behaviors', []))}

### Implementation Approach:
{result.get('implementation_notes', 'Not captured')}

### Contract Details:
{self._get_contract_description(contract['id'])}

{"### Compliance Notes:" if passed else "### Violations:"}
{result.get('notes', 'See test results above')}
"""
            
            # Update custom field
            for field in issue.custom_fields:
                if field.name.lower() == 'score':
                    issue.custom_fields = [{'id': field.id, 'value': result['score']}]
                    break
            
            issue.save()
            
            return {
                'name': contract['name'],
                'score': result['score'],
                'max': contract['max_points'],
                'passed': passed
            }
            
        except Exception as e:
            logger.error(f"Contract {contract['id']} testing failed: {e}", exc_info=True)
            
            issue.status_id = self._get_status_id('failed')
            issue.notes = f"## ❌ Testing Error\n\n{str(e)}"
            issue.save()
            
            return {
                'name': contract['name'],
                'score': 0,
                'max': contract['max_points'],
                'passed': False,
                'error': str(e)
            }
    
    def _execute_contract_tests(self, contract: Dict, model: str) -> Dict:
        """Execute tests for a contract"""
        # Mock implementation - replace with actual contract testing
        import random
        
        behaviors = self._get_contract_behaviors(contract['id'])
        
        # Contract testing is pass/fail
        all_passed = random.random() > 0.3
        score = contract['max_points'] if all_passed else random.randint(0, contract['max_points'] - 1)
        
        return {
            'score': score,
            'behaviors': [
                {'name': behavior, 'passed': all_passed or random.random() > 0.5}
                for behavior in behaviors
            ],
            'implementation_notes': f"Implementation uses {'standard' if all_passed else 'custom'} approach",
            'notes': 'All behaviors fulfilled' if all_passed else 'Some behaviors violated'
        }
    
    def _get_contract_behaviors(self, contract_id: int) -> List[str]:
        """Get behaviors for a contract"""
        behaviors_map = {
            1: ['Load from multiple sources', 'Required attributes present', 'Validate values'],
            2: ['Console and file output', 'Verbose mode', 'Structured logging'],
            3: ['Builds valid docker command', 'Volume mounts work', 'Exit codes correct'],
            4: ['Executes locally', 'Directory handling', 'Error handling'],
            5: ['Help command', 'Run command', 'Global options'],
            6: ['List state', 'Show resource', 'Handle missing state'],
            7: ['Clear error messages', 'Graceful failures', 'Exit codes']
        }
        return behaviors_map.get(contract_id, ['Behavior 1', 'Behavior 2', 'Behavior 3'])
    
    def _get_contract_description(self, contract_id: int) -> str:
        """Get contract description"""
        descriptions = {
            1: "Configuration must load from files, environment, and provide defaults with proper precedence",
            2: "Logging must output to console and file with appropriate levels and structured data support",
            3: "Docker execution must build correct commands, mount volumes, and return proper exit codes",
            4: "Local execution must run AICL engine, handle directory changes, and gracefully handle errors",
            5: "CLI must provide help, execute run command, and respect global options",
            6: "State management must list resources, show details, and handle missing data",
            7: "Error handling must provide clear messages, fail gracefully, and return correct codes"
        }
        return descriptions.get(contract_id, "Contract specification")
    
    def _format_behaviors(self, behaviors: List[Dict]) -> str:
        """Format behavior results"""
        if not behaviors:
            return "No behavior details available"
        
        lines = []
        for behavior in behaviors:
            icon = "✅" if behavior['passed'] else "❌"
            lines.append(f"- {icon} {behavior['name']}")
        
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
