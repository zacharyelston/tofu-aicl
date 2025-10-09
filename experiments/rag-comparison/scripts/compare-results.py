#!/usr/bin/env python3
"""
RAG Experiment Results Comparison and Analysis

Analyzes State as DNA lineage data from multiple experiments to generate
comprehensive comparisons and insights across providers and configurations.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from aicl.state.manager import StateManager
from aicl.state.models import State


class ExperimentAnalyzer:
    """Analyzes and compares RAG experiment results."""
    
    def __init__(self, experiment_dir: Path):
        self.experiment_dir = experiment_dir
        self.states_dir = experiment_dir / "states"
        self.results_dir = experiment_dir / "results"
        self.config_dir = experiment_dir / "config"
        
        # Load experiment configuration
        config_file = self.config_dir / "experiments.yaml"
        if config_file.exists():
            with open(config_file) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}
    
    def load_experiment_states(self, phase: Optional[int] = None, 
                             git_sha: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load all experiment state files matching criteria."""
        print("📊 Loading experiment state files...")
        
        experiments = []
        state_files = list(self.states_dir.glob("*.tfstate"))
        
        for state_file in state_files:
            try:
                # Parse experiment info from filename
                filename = state_file.stem
                parts = filename.split('_')
                
                if len(parts) < 4:
                    continue
                
                exp_phase = int(parts[0].replace('phase', ''))
                exp_provider = parts[1]
                exp_context_size = parts[2]
                exp_git_sha = parts[3]
                
                # Apply filters
                if phase is not None and exp_phase != phase:
                    continue
                if git_sha is not None and exp_git_sha != git_sha:
                    continue
                
                # Load state with lineage
                manager = StateManager(state_dir=str(self.states_dir), enable_lineage=True)
                state = manager.load(filename)
                
                if not isinstance(state, State):
                    continue
                
                # Extract experiment data
                experiment_data = {
                    'filename': filename,
                    'phase': exp_phase,
                    'provider': exp_provider,
                    'context_size': exp_context_size,
                    'git_sha': exp_git_sha,
                    'state': state,
                    'lineage_summary': manager.get_lineage_summary(),
                    'created_at': state.created_at,
                    'total_actions': len(state.lineage),
                    'total_cost': state.get_total_cost_usd(),
                    'total_duration_ms': state.get_total_duration_ms()
                }
                
                # Extract evaluation results from lineage
                evaluation_entries = [
                    entry for entry in state.lineage 
                    if entry.action == "execute" and entry.step == "evaluate_results"
                ]
                
                if evaluation_entries:
                    evaluation = evaluation_entries[-1].result
                    experiment_data.update({
                        'avg_relevance_score': evaluation.get('avg_relevance_score', 0.0),
                        'avg_latency_ms': evaluation.get('avg_latency_ms', 0.0),
                        'overall_score': evaluation.get('overall_score', 0.0),
                        'query_count': evaluation.get('query_count', 0)
                    })
                
                experiments.append(experiment_data)
                
            except Exception as e:
                print(f"   ⚠️  Error loading {state_file}: {e}")
                continue
        
        print(f"   ✅ Loaded {len(experiments)} experiment states")
        return experiments
    
    def generate_provider_comparison(self, experiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparison across providers."""
        print("🔍 Analyzing provider performance...")
        
        provider_stats = {}
        
        for exp in experiments:
            provider = exp['provider']
            
            if provider not in provider_stats:
                provider_stats[provider] = {
                    'experiments': [],
                    'total_cost': 0.0,
                    'total_duration_ms': 0,
                    'avg_relevance_scores': [],
                    'avg_latency_scores': [],
                    'overall_scores': []
                }
            
            stats = provider_stats[provider]
            stats['experiments'].append(exp)
            stats['total_cost'] += exp.get('total_cost', 0.0)
            stats['total_duration_ms'] += exp.get('total_duration_ms', 0)
            
            if 'avg_relevance_score' in exp:
                stats['avg_relevance_scores'].append(exp['avg_relevance_score'])
            if 'avg_latency_ms' in exp:
                stats['avg_latency_scores'].append(exp['avg_latency_ms'])
            if 'overall_score' in exp:
                stats['overall_scores'].append(exp['overall_score'])
        
        # Calculate aggregated metrics
        comparison = {}
        for provider, stats in provider_stats.items():
            exp_count = len(stats['experiments'])
            
            comparison[provider] = {
                'experiment_count': exp_count,
                'total_cost_usd': round(stats['total_cost'], 4),
                'avg_cost_per_experiment': round(stats['total_cost'] / exp_count, 4) if exp_count > 0 else 0,
                'total_duration_ms': stats['total_duration_ms'],
                'avg_duration_per_experiment': stats['total_duration_ms'] // exp_count if exp_count > 0 else 0,
                'avg_relevance_score': round(sum(stats['avg_relevance_scores']) / len(stats['avg_relevance_scores']), 3) if stats['avg_relevance_scores'] else 0,
                'avg_latency_ms': round(sum(stats['avg_latency_scores']) / len(stats['avg_latency_scores']), 1) if stats['avg_latency_scores'] else 0,
                'avg_overall_score': round(sum(stats['overall_scores']) / len(stats['overall_scores']), 3) if stats['overall_scores'] else 0,
                'experiments': [exp['filename'] for exp in stats['experiments']]
            }
        
        return comparison
    
    def generate_context_size_analysis(self, experiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance across different context sizes."""
        print("📏 Analyzing context size impact...")
        
        context_stats = {}
        
        for exp in experiments:
            context_size = exp['context_size']
            
            if context_size not in context_stats:
                context_stats[context_size] = {
                    'experiments': [],
                    'providers': set(),
                    'relevance_scores': [],
                    'latency_scores': [],
                    'overall_scores': [],
                    'costs': []
                }
            
            stats = context_stats[context_size]
            stats['experiments'].append(exp)
            stats['providers'].add(exp['provider'])
            
            if 'avg_relevance_score' in exp:
                stats['relevance_scores'].append(exp['avg_relevance_score'])
            if 'avg_latency_ms' in exp:
                stats['latency_scores'].append(exp['avg_latency_ms'])
            if 'overall_score' in exp:
                stats['overall_scores'].append(exp['overall_score'])
            if 'total_cost' in exp:
                stats['costs'].append(exp['total_cost'])
        
        # Calculate aggregated metrics
        analysis = {}
        for context_size, stats in context_stats.items():
            exp_count = len(stats['experiments'])
            
            analysis[context_size] = {
                'experiment_count': exp_count,
                'provider_count': len(stats['providers']),
                'providers': list(stats['providers']),
                'avg_relevance_score': round(sum(stats['relevance_scores']) / len(stats['relevance_scores']), 3) if stats['relevance_scores'] else 0,
                'avg_latency_ms': round(sum(stats['latency_scores']) / len(stats['latency_scores']), 1) if stats['latency_scores'] else 0,
                'avg_overall_score': round(sum(stats['overall_scores']) / len(stats['overall_scores']), 3) if stats['overall_scores'] else 0,
                'avg_cost_usd': round(sum(stats['costs']) / len(stats['costs']), 4) if stats['costs'] else 0,
                'experiments': [exp['filename'] for exp in stats['experiments']]
            }
        
        return analysis
    
    def generate_lineage_analysis(self, experiments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze lineage patterns across experiments."""
        print("🧬 Analyzing experiment lineage patterns...")
        
        lineage_analysis = {
            'total_experiments': len(experiments),
            'total_actions_across_all': 0,
            'total_cost_across_all': 0.0,
            'total_duration_across_all': 0,
            'action_type_distribution': {},
            'provider_action_patterns': {},
            'git_sha_distribution': {},
            'phase_distribution': {}
        }
        
        for exp in experiments:
            state = exp['state']
            
            # Aggregate totals
            lineage_analysis['total_actions_across_all'] += len(state.lineage)
            lineage_analysis['total_cost_across_all'] += state.get_total_cost_usd()
            lineage_analysis['total_duration_across_all'] += state.get_total_duration_ms()
            
            # Action type distribution
            for entry in state.lineage:
                action = entry.action
                if action not in lineage_analysis['action_type_distribution']:
                    lineage_analysis['action_type_distribution'][action] = 0
                lineage_analysis['action_type_distribution'][action] += 1
            
            # Provider patterns
            provider = exp['provider']
            if provider not in lineage_analysis['provider_action_patterns']:
                lineage_analysis['provider_action_patterns'][provider] = {
                    'total_actions': 0,
                    'total_cost': 0.0,
                    'total_duration': 0,
                    'experiments': 0
                }
            
            patterns = lineage_analysis['provider_action_patterns'][provider]
            patterns['total_actions'] += len(state.lineage)
            patterns['total_cost'] += state.get_total_cost_usd()
            patterns['total_duration'] += state.get_total_duration_ms()
            patterns['experiments'] += 1
            
            # Git SHA distribution
            git_sha = exp['git_sha']
            if git_sha not in lineage_analysis['git_sha_distribution']:
                lineage_analysis['git_sha_distribution'][git_sha] = 0
            lineage_analysis['git_sha_distribution'][git_sha] += 1
            
            # Phase distribution
            phase = exp['phase']
            if phase not in lineage_analysis['phase_distribution']:
                lineage_analysis['phase_distribution'][phase] = 0
            lineage_analysis['phase_distribution'][phase] += 1
        
        # Calculate averages
        if experiments:
            lineage_analysis['avg_actions_per_experiment'] = lineage_analysis['total_actions_across_all'] / len(experiments)
            lineage_analysis['avg_cost_per_experiment'] = lineage_analysis['total_cost_across_all'] / len(experiments)
            lineage_analysis['avg_duration_per_experiment'] = lineage_analysis['total_duration_across_all'] / len(experiments)
        
        return lineage_analysis
    
    def generate_recommendations(self, provider_comparison: Dict[str, Any], 
                               context_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Find best performing provider
        if provider_comparison:
            best_provider = max(provider_comparison.keys(), 
                              key=lambda p: provider_comparison[p]['avg_overall_score'])
            best_score = provider_comparison[best_provider]['avg_overall_score']
            
            recommendations.append(
                f"🏆 **Best Overall Provider**: {best_provider.title()} "
                f"(score: {best_score:.3f})"
            )
        
        # Find most cost-effective provider
        if provider_comparison:
            cheapest_provider = min(provider_comparison.keys(),
                                  key=lambda p: provider_comparison[p]['avg_cost_per_experiment'])
            cheapest_cost = provider_comparison[cheapest_provider]['avg_cost_per_experiment']
            
            recommendations.append(
                f"💰 **Most Cost-Effective**: {cheapest_provider.title()} "
                f"(${cheapest_cost:.4f} per experiment)"
            )
        
        # Find optimal context size
        if context_analysis:
            best_context = max(context_analysis.keys(),
                             key=lambda c: context_analysis[c]['avg_overall_score'])
            best_context_score = context_analysis[best_context]['avg_overall_score']
            
            recommendations.append(
                f"📏 **Optimal Context Size**: {best_context.title()} "
                f"(score: {best_context_score:.3f})"
            )
        
        # Performance vs cost trade-offs
        if provider_comparison:
            for provider, stats in provider_comparison.items():
                efficiency_ratio = stats['avg_overall_score'] / max(stats['avg_cost_per_experiment'], 0.0001)
                recommendations.append(
                    f"⚖️  **{provider.title()} Efficiency Ratio**: "
                    f"{efficiency_ratio:.1f} (score/cost)"
                )
        
        return recommendations
    
    def save_comparison_report(self, analysis_results: Dict[str, Any], 
                             output_file: Path) -> None:
        """Save comprehensive comparison report."""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'analysis_type': 'rag_provider_comparison',
            'git_context': self._get_git_context(),
            **analysis_results
        }
        
        # Save JSON report
        json_file = output_file.with_suffix('.json')
        with open(json_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        html_file = output_file.with_suffix('.html')
        self._generate_html_report(report, html_file)
        
        print(f"📊 Reports saved:")
        print(f"   JSON: {json_file}")
        print(f"   HTML: {html_file}")
    
    def _get_git_context(self) -> Dict[str, str]:
        """Get current git context."""
        import subprocess
        
        try:
            sha_result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                                      capture_output=True, text=True, check=True)
            branch_result = subprocess.run(['git', 'branch', '--show-current'],
                                         capture_output=True, text=True, check=True)
            
            return {
                'git_sha': sha_result.stdout.strip(),
                'git_branch': branch_result.stdout.strip()
            }
        except subprocess.CalledProcessError:
            return {'git_sha': 'unknown', 'git_branch': 'unknown'}
    
    def _generate_html_report(self, report: Dict[str, Any], html_file: Path) -> None:
        """Generate HTML report with visualizations."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAG Provider Comparison Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .section {{ margin-bottom: 30px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric-card {{ background: #fff; border: 1px solid #e9ecef; padding: 15px; border-radius: 6px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #0066cc; }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .provider-comparison {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .provider-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
        .score-bar {{ background: #e9ecef; height: 20px; border-radius: 10px; overflow: hidden; }}
        .score-fill {{ background: linear-gradient(90deg, #28a745, #ffc107, #dc3545); height: 100%; }}
        .recommendations {{ background: #e7f3ff; padding: 20px; border-radius: 8px; border-left: 4px solid #0066cc; }}
        .git-info {{ background: #f1f3f4; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 RAG Provider Comparison Report</h1>
        <p>Generated: {report['generated_at']}</p>
        <div class="git-info">
            Git SHA: {report.get('git_context', {}).get('git_sha', 'unknown')} | 
            Branch: {report.get('git_context', {}).get('git_branch', 'unknown')}
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Overview</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{report.get('lineage_analysis', {}).get('total_experiments', 0)}</div>
                <div class="metric-label">Total Experiments</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">${report.get('lineage_analysis', {}).get('total_cost_across_all', 0):.4f}</div>
                <div class="metric-label">Total Cost</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{report.get('lineage_analysis', {}).get('total_actions_across_all', 0)}</div>
                <div class="metric-label">Total Actions</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🏆 Provider Comparison</h2>
        <div class="provider-comparison">
"""
        
        # Add provider cards
        provider_comparison = report.get('provider_comparison', {})
        for provider, stats in provider_comparison.items():
            score_percentage = stats['avg_overall_score'] * 100
            html_content += f"""
            <div class="provider-card">
                <h3>{provider.title()}</h3>
                <p><strong>Overall Score:</strong> {stats['avg_overall_score']:.3f}</p>
                <div class="score-bar">
                    <div class="score-fill" style="width: {score_percentage}%"></div>
                </div>
                <p><strong>Avg Cost:</strong> ${stats['avg_cost_per_experiment']:.4f}</p>
                <p><strong>Avg Latency:</strong> {stats['avg_latency_ms']:.1f}ms</p>
                <p><strong>Experiments:</strong> {stats['experiment_count']}</p>
            </div>
"""
        
        html_content += """
        </div>
    </div>
    
    <div class="section">
        <h2>💡 Recommendations</h2>
        <div class="recommendations">
"""
        
        # Add recommendations
        recommendations = report.get('recommendations', [])
        for rec in recommendations:
            html_content += f"<p>{rec}</p>"
        
        html_content += """
        </div>
    </div>
    
    <div class="section">
        <h2>🔍 Detailed Analysis</h2>
        <pre style="background: #f8f9fa; padding: 15px; border-radius: 6px; overflow-x: auto;">
"""
        
        # Add JSON data for detailed analysis
        html_content += json.dumps(report, indent=2)
        
        html_content += """
        </pre>
    </div>
</body>
</html>
"""
        
        with open(html_file, 'w') as f:
            f.write(html_content)
    
    def run_analysis(self, phase: Optional[int] = None, 
                    git_sha: Optional[str] = None,
                    output_file: Optional[str] = None) -> Dict[str, Any]:
        """Run complete analysis pipeline."""
        print(f"🔬 Starting RAG experiment analysis")
        if phase:
            print(f"   Phase filter: {phase}")
        if git_sha:
            print(f"   Git SHA filter: {git_sha}")
        print()
        
        # Load experiment data
        experiments = self.load_experiment_states(phase=phase, git_sha=git_sha)
        
        if not experiments:
            print("❌ No experiments found matching criteria")
            return {}
        
        # Generate analyses
        provider_comparison = self.generate_provider_comparison(experiments)
        context_analysis = self.generate_context_size_analysis(experiments)
        lineage_analysis = self.generate_lineage_analysis(experiments)
        recommendations = self.generate_recommendations(provider_comparison, context_analysis)
        
        # Compile results
        analysis_results = {
            'provider_comparison': provider_comparison,
            'context_size_analysis': context_analysis,
            'lineage_analysis': lineage_analysis,
            'recommendations': recommendations,
            'experiment_details': [
                {
                    'filename': exp['filename'],
                    'provider': exp['provider'],
                    'context_size': exp['context_size'],
                    'phase': exp['phase'],
                    'git_sha': exp['git_sha'],
                    'overall_score': exp.get('overall_score', 0),
                    'total_cost': exp.get('total_cost', 0),
                    'total_actions': exp['total_actions']
                }
                for exp in experiments
            ]
        }
        
        # Save report
        if output_file:
            output_path = self.results_dir / output_file
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.results_dir / f"comparison_report_{timestamp}"
        
        self.save_comparison_report(analysis_results, output_path)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Analysis Summary")
        print("=" * 60)
        
        print(f"Total Experiments: {len(experiments)}")
        print(f"Providers Tested: {len(provider_comparison)}")
        print(f"Context Sizes: {len(context_analysis)}")
        print(f"Total Cost: ${lineage_analysis['total_cost_across_all']:.4f}")
        print(f"Total Actions: {lineage_analysis['total_actions_across_all']}")
        
        print("\n🏆 Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec}")
        
        return analysis_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze RAG experiment results")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3],
                       help="Filter by experiment phase")
    parser.add_argument("--git-sha", type=str,
                       help="Filter by git commit SHA")
    parser.add_argument("--output", type=str,
                       help="Output file name (without extension)")
    parser.add_argument("--experiment-dir", type=str,
                       default="experiments/rag-comparison",
                       help="Experiment directory path")
    
    args = parser.parse_args()
    
    # Create analyzer
    experiment_dir = Path(args.experiment_dir)
    analyzer = ExperimentAnalyzer(experiment_dir)
    
    # Run analysis
    results = analyzer.run_analysis(
        phase=args.phase,
        git_sha=args.git_sha,
        output_file=args.output
    )
    
    if results:
        print(f"\n✅ Analysis complete! Check results directory for reports.")
    else:
        print(f"\n❌ No results to analyze.")
        sys.exit(1)


if __name__ == "__main__":
    main()
