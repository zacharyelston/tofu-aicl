#!/usr/bin/env python3
"""
LLM-as-Judge Grading System
Evaluates response quality using an LLM to score accuracy, relevance, and actionability
"""

import os
import json
import requests
from typing import Dict, Optional, List


class LLMGrader:
    """Uses an LLM to grade response quality on multiple dimensions"""
    
    GRADING_CRITERIA = {
        'accuracy': 'How factually correct and technically accurate is the response?',
        'relevance': 'How well does the response address the specific question asked?',
        'actionability': 'How clear and practical are the suggestions or answers provided?',
        'clarity': 'How well-structured and easy to understand is the response?',
        'completeness': 'How thoroughly does the response cover the topic?'
    }
    
    def __init__(self, judge_model: str = "openai/gpt-4", api_key: Optional[str] = None):
        """
        Initialize the grader
        
        Args:
            judge_model: Model to use as judge (e.g., "openai/gpt-4", "anthropic/claude-3.5-sonnet")
            api_key: OpenRouter API key (uses env var if not provided)
        """
        self.judge_model = judge_model
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def grade_response(
        self, 
        question: str, 
        response: str,
        criteria: Optional[List[str]] = None,
        context: Optional[str] = None
    ) -> Dict:
        """
        Grade a response using LLM-as-Judge
        
        Args:
            question: The original question/prompt
            response: The response to grade
            criteria: List of criteria to grade (uses default if None)
            context: Optional additional context for grading
            
        Returns:
            Dict with scores for each criterion and overall grade
        """
        criteria = criteria or list(self.GRADING_CRITERIA.keys())
        
        # Build grading prompt
        grading_prompt = self._build_grading_prompt(question, response, criteria, context)
        
        # Call judge model
        try:
            judge_response = self._call_judge(grading_prompt)
            grades = self._parse_grades(judge_response)
            
            # Calculate overall score
            overall = sum(grades['scores'].values()) / len(grades['scores'])
            grades['overall_score'] = round(overall, 2)
            
            return grades
            
        except Exception as e:
            return {
                'error': str(e),
                'overall_score': 0.0,
                'scores': {},
                'reasoning': ''
            }
    
    def _build_grading_prompt(self, question: str, response: str, criteria: List[str], context: Optional[str]) -> str:
        """Build the grading prompt for the judge model"""
        
        criteria_descriptions = "\n".join([
            f"- **{criterion.title()}** (1-10): {self.GRADING_CRITERIA[criterion]}"
            for criterion in criteria
        ])
        
        context_section = f"\n\n**Context:**\n{context}" if context else ""
        
        prompt = f"""You are an expert evaluator assessing the quality of AI-generated responses.

**Question/Prompt:**
{question}

**Response to Evaluate:**
{response}{context_section}

**Grading Criteria:**
{criteria_descriptions}

**Instructions:**
1. Evaluate the response on each criterion above
2. Provide a score from 1-10 for each (10 = excellent, 1 = poor)
3. Provide brief reasoning for your scores

**Output Format (JSON):**
```json
{{
  "scores": {{
    "accuracy": <score>,
    "relevance": <score>,
    "actionability": <score>,
    "clarity": <score>,
    "completeness": <score>
  }},
  "reasoning": "Brief explanation of the scores..."
}}
```

Respond with ONLY the JSON object, no additional text."""
        
        return prompt
    
    def _call_judge(self, prompt: str) -> str:
        """Call the judge model via OpenRouter"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/zacharyelston/tofu-aicl",
            "X-Title": "AICL LLM Grader"
        }
        
        payload = {
            "model": self.judge_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert evaluator. Provide precise, objective assessments in the requested JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Low temperature for consistent grading
            "max_tokens": 500
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        data = response.json()
        return data['choices'][0]['message']['content']
    
    def _parse_grades(self, judge_response: str) -> Dict:
        """Parse grades from judge response"""
        
        # Extract JSON from response (handle markdown code blocks)
        response_text = judge_response.strip()
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        
        try:
            grades = json.loads(response_text)
            return grades
        except json.JSONDecodeError:
            # Fallback: try to extract scores with regex
            return {
                'scores': {},
                'reasoning': judge_response,
                'parse_error': True
            }


def grade_experiment_response(
    experiment_id: str,
    question: str,
    response: str,
    judge_model: str = "openai/gpt-4",
    criteria: Optional[List[str]] = None
) -> Dict:
    """
    Convenience function to grade a single experiment response
    
    Args:
        experiment_id: ID of the experiment
        question: Original question
        response: Response to grade
        judge_model: Model to use as judge
        criteria: Grading criteria
        
    Returns:
        Dict with experiment_id and grading results
    """
    grader = LLMGrader(judge_model=judge_model)
    grades = grader.grade_response(question, response, criteria)
    
    return {
        'experiment_id': experiment_id,
        'judge_model': judge_model,
        **grades
    }


if __name__ == "__main__":
    # Example usage
    grader = LLMGrader(judge_model="openai/gpt-4")
    
    question = "How can I optimize Python code for better performance?"
    response = """Here are 3 key ways to optimize Python code:
1. Use built-in functions and libraries (like numpy) instead of loops
2. Profile your code to find bottlenecks before optimizing
3. Consider using generators for memory efficiency with large datasets"""
    
    grades = grader.grade_response(question, response)
    print(json.dumps(grades, indent=2))
