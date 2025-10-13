"""
v2 API Layer - Shared experiment and grading logic

Provides storage-agnostic APIs for:
- Running experiments
- Grading responses with LLM-as-Judge
- Analyzing results

This layer sits between the core engine and the CLI/Web interfaces.
"""

from .experiments import ExperimentRunner
from .grading import LLMGrader

__all__ = ['ExperimentRunner', 'LLMGrader']
