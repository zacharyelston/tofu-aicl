#!/usr/bin/env python3
"""
Generate AICL experiment configs from test-variables.yaml
Supports single-variable, multi-variable, and A/B testing

Now integrates with centralized ModelCatalog for model metadata.
"""

import yaml
import itertools
from pathlib import Path
from typing import List, Dict, Any
from v2.config.model_catalog import ModelCatalog

def load_test_config(config_file: str = "test-variables.yaml") -> Dict:
    """
    Load test variables configuration
    
    Enriches model data from centralized ModelCatalog when available.
    """
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    # Enrich with catalog data if available
    try:
        catalog = ModelCatalog()
        
        # Enrich chat models
        if 'chat_models' in config and 'models' in config['chat_models']:
            enriched_chat = []
            for model_def in config['chat_models']['models']:
                # Ensure model_def is a dict (handle simple string names)
                if isinstance(model_def, str):
                    model_def = {'name': model_def}
                
                # Try to find in catalog
                catalog_model = catalog.get(model_def['name'])
                if catalog_model:
                    # Use catalog data as source of truth
                    enriched_chat.append({
                        'id': catalog_model.id,
                        'name': catalog_model.name,
                        'provider': catalog_model.provider,
                        'cost_per_1m_tokens': catalog_model.cost_per_1k_input * 1000,  # Convert to per 1M
                        'quality_score': catalog_model.quality_score,
                        'context_window': catalog_model.context_window
                    })
                else:
                    # Fallback: ensure required fields exist
                    if 'provider' not in model_def:
                        model_def['provider'] = 'unknown'
                    if 'cost_per_1m_tokens' not in model_def:
                        model_def['cost_per_1m_tokens'] = 0.0
                    enriched_chat.append(model_def)
            config['chat_models']['models'] = enriched_chat
        
        # Enrich embedding models
        if 'embedding_models' in config:
            for provider_key in ['openai', 'google', 'azure']:
                if provider_key in config['embedding_models']:
                    enriched_embeddings = []
                    for model_def in config['embedding_models'][provider_key]:
                        # Ensure model_def is a dict
                        if isinstance(model_def, str):
                            model_def = {'name': model_def}
                        
                        catalog_model = catalog.get(model_def['name'])
                        if catalog_model:
                            enriched_embeddings.append({
                                'id': catalog_model.id,
                                'name': catalog_model.name,
                                'provider': catalog_model.provider,
                                'dimensions': catalog_model.dimensions,
                                'cost_per_1m_tokens': catalog_model.cost_per_1k_input * 1000,
                                'quality_score': catalog_model.quality_score
                            })
                        else:
                            # Fallback: ensure required fields exist
                            if 'provider' not in model_def:
                                model_def['provider'] = provider_key
                            if 'dimensions' not in model_def:
                                model_def['dimensions'] = 0
                            if 'cost_per_1m_tokens' not in model_def:
                                model_def['cost_per_1m_tokens'] = 0.0
                            enriched_embeddings.append(model_def)
                    config['embedding_models'][provider_key] = enriched_embeddings
    except Exception as e:
        print(f"Warning: Could not enrich config with ModelCatalog: {e}")
        # Continue with original config
    
    return config

def generate_single_variable_experiments(config: Dict) -> List[Dict]:
    """Generate single-variable experiments (one variable at a time)"""
    experiments = []
    
    for test in config['experiment_design']['single_variable']:
        variable = test['variable']
        fixed = test['fixed']
        test_values = test['test_values']
        
        for idx, value in enumerate(test_values):
            exp = {
                'id': f"{variable.replace('.', '_')}_{idx+1}",
                'description': f"Test {variable} = {value}",
                'variable': variable,
                'value': value,
                'fixed_params': fixed
            }
            experiments.append(exp)
    
    return experiments

def generate_multi_variable_experiments(config: Dict) -> List[Dict]:
    """Generate multi-variable grid search experiments"""
    experiments = []
    
    for test in config['experiment_design']['multi_variable']:
        name = test['name']
        variables = test['variables']
        fixed = test.get('fixed', {})
        
        # Create all combinations (grid search)
        var_names = list(variables.keys())
        var_values = [variables[var] for var in var_names]
        
        for idx, combination in enumerate(itertools.product(*var_values)):
            params = dict(zip(var_names, combination))
            params.update(fixed)
            
            exp = {
                'id': f"{name}_{idx+1}",
                'description': f"{name}: {params}",
                'variables': params,
                'test_type': 'grid_search'
            }
            experiments.append(exp)
    
    return experiments

def generate_aicl_config(exp: Dict, output_dir: str = "experiments/auto_generated") -> str:
    """Generate AICL configuration file from experiment spec"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Extract parameters
    if 'variables' in exp:
        params = exp['variables']
    else:
        params = exp['fixed_params'].copy()
        # Apply the variable being tested
        var_parts = exp['variable'].split('.')
        params[var_parts[-1]] = exp['value']
    
    # Build AICL config
    config = f'''terraform {{
  required_providers {{
    naga = {{ source = "aicl/naga" }}
    pinecone = {{ source = "aicl/pinecone" }}
  }}
}}

# Embedding
resource "naga_embedding" "vector" {{
  model = "{params.get('embedding', params.get('embedding_model', 'text-embedding-3-large'))}"
  text = "What is the role of the Evaluator in AICL?"
  aiclResourceName = "vector"
}}

# Vector query
resource "query" "results" {{
  index_name = "tofu-aicl"
  namespace = "tofu-aicl-codebase"
  top_k = {params.get('top_k', 5)}
  vector = "${{resource.naga_embedding.vector.attributes.embeddings[0].values}}"
  aiclResourceName = "results"
}}

# Chat response
resource "naga_chat" "answer" {{
  model = "{params.get('model', params.get('chat', 'gpt-4o-2024-08-06'))}"
  messages = [
    {{
      role = "user"
      content = "Based on this context, answer: What is the role of the Evaluator?\\n\\nContext: ${{resource.query.results.attributes.matches}}"
    }}
  ]
  max_tokens = {params.get('max_tokens', 500)}
  temperature = {params.get('temperature', 0.7)}
  aiclResourceName = "answer"
}}
'''
    
    # Save config
    config_path = f"{output_dir}/{exp['id']}.aicl"
    with open(config_path, 'w') as f:
        f.write(config)
    
    return config_path

def generate_test_suite(suite_name: str, config: Dict) -> List[str]:
    """Generate a predefined test suite"""
    suites = config['test_suites']
    
    if suite_name not in suites:
        raise ValueError(f"Unknown test suite: {suite_name}")
    
    suite = suites[suite_name]
    experiments = suite['variables']
    
    output_dir = f"experiments/suites/{suite_name}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    configs = []
    
    if isinstance(experiments, list):
        # Simple list of experiments
        for idx, exp_vars in enumerate(experiments):
            exp = {
                'id': f"{suite_name}_{idx+1}",
                'description': f"{suite_name} experiment {idx+1}",
                'variables': exp_vars
            }
            config_path = generate_aicl_config(exp, output_dir)
            configs.append(config_path)
    
    elif isinstance(experiments, dict):
        # Grid search over variables
        var_names = list(experiments.keys())
        var_values = [experiments[var] if isinstance(experiments[var], list) else [experiments[var]] 
                     for var in var_names]
        
        for idx, combination in enumerate(itertools.product(*var_values)):
            params = dict(zip(var_names, combination))
            exp = {
                'id': f"{suite_name}_{idx+1}",
                'description': f"{suite_name}: {params}",
                'variables': params
            }
            config_path = generate_aicl_config(exp, output_dir)
            configs.append(config_path)
    
    else:
        # Single experiment count
        for idx in range(experiments):
            exp = {
                'id': f"{suite_name}_{idx+1}",
                'description': f"{suite_name} experiment {idx+1}",
                'variables': {'model': 'gpt-4o-2024-08-06', 'top_k': 5}
            }
            config_path = generate_aicl_config(exp, output_dir)
            configs.append(config_path)
    
    return configs

def print_summary(config: Dict):
    """Print summary of available tests"""
    print("\n" + "="*80)
    print("📊 AICL EXPERIMENT GENERATOR")
    print("="*80)
    
    # Chat models
    print(f"\n🤖 Chat Models Available: {len(config['chat_models']['models'])}")
    for model in config['chat_models']['models']:
        print(f"   • {model['name']} ({model['provider']}) - ${model['cost_per_1m_tokens']}/1M")
    
    # Embeddings
    total_embeddings = (len(config['embedding_models']['openai']) + 
                       len(config['embedding_models']['google']) + 
                       len(config['embedding_models']['azure']))
    print(f"\n📐 Embedding Models Available: {total_embeddings}")
    for emb in config['embedding_models']['openai']:
        print(f"   • {emb['name']} ({emb['dimensions']}d) - Quality: {emb['quality_score']}/10")
    
    # Test suites
    print(f"\n🧪 Test Suites Available: {len(config['test_suites'])}")
    for suite_name, suite in config['test_suites'].items():
        print(f"   • {suite_name}: {suite['experiments']} experiments ({suite['duration']})")
    
    # Variables
    print(f"\n🎛️  Tunable Variables:")
    print(f"   • temperature: {config['chat_models']['temperature']['min']} - {config['chat_models']['temperature']['max']}")
    print(f"   • max_tokens: {config['chat_models']['max_tokens']['min']} - {config['chat_models']['max_tokens']['max']}")
    print(f"   • top_k: {config['pinecone']['top_k']['min']} - {config['pinecone']['top_k']['max']}")
    print(f"   • chunk_size: {config['text_splitter']['chunk_size']['min']} - {config['text_splitter']['chunk_size']['max']}")
    print(f"   • rerank (Ragie): {config['ragie']['retrieval']['rerank']['values']}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    import sys
    
    # Load configuration
    config = load_test_config()
    
    # Parse arguments
    if len(sys.argv) < 2:
        print_summary(config)
        print("\nUsage:")
        print("  python generate_experiments.py summary           # Show this summary")
        print("  python generate_experiments.py single            # Generate single-variable tests")
        print("  python generate_experiments.py multi             # Generate multi-variable tests")
        print("  python generate_experiments.py suite <name>      # Generate test suite")
        print("\nAvailable suites: smoke_test, comprehensive_test, cost_optimization, quality_optimization")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "summary":
        print_summary(config)
    
    elif command == "single":
        print("\n🔬 Generating single-variable experiments...")
        experiments = generate_single_variable_experiments(config)
        
        for exp in experiments:
            config_path = generate_aicl_config(exp)
            print(f"   ✅ {config_path}")
        
        print(f"\n✅ Generated {len(experiments)} single-variable experiments")
        print(f"   Run: python run_rag_graded_matrix.py experiments/auto_generated/*.aicl")
    
    elif command == "multi":
        print("\n🔬 Generating multi-variable grid search experiments...")
        experiments = generate_multi_variable_experiments(config)
        
        for exp in experiments:
            config_path = generate_aicl_config(exp)
            print(f"   ✅ {config_path}")
        
        print(f"\n✅ Generated {len(experiments)} multi-variable experiments")
        print(f"   Run: python run_rag_graded_matrix.py experiments/auto_generated/*.aicl")
    
    elif command == "suite":
        if len(sys.argv) < 3:
            print("❌ Please specify suite name")
            print("Available: smoke_test, comprehensive_test, cost_optimization, quality_optimization")
            sys.exit(1)
        
        suite_name = sys.argv[2]
        print(f"\n🔬 Generating {suite_name} suite...")
        
        configs = generate_test_suite(suite_name, config)
        
        for cfg in configs:
            print(f"   ✅ {cfg}")
        
        suite_info = config['test_suites'][suite_name]
        print(f"\n✅ Generated {len(configs)} experiments for {suite_name}")
        print(f"   Duration: {suite_info['duration']}")
        print(f"   Run: python run_rag_graded_matrix.py experiments/suites/{suite_name}/*.aicl")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
