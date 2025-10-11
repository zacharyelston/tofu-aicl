"""
Model Catalog Loader

Centralized model metadata management for AICL.
Loads model catalog from models.yaml and provides query/filter capabilities.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Model:
    """Model metadata"""
    id: str
    name: str
    display_name: str
    provider: str
    type: str  # chat, embedding, completion
    context_window: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    quality_score: float
    capabilities: List[str] = field(default_factory=list)
    dimensions: Optional[int] = None  # For embeddings
    reliability_score: Optional[float] = None  # For judge models
    
    @property
    def cost_per_1m_input(self) -> float:
        """Cost per million tokens (for compatibility)"""
        return self.cost_per_1k_input * 1000
    
    @property
    def cost_per_1m_output(self) -> float:
        """Cost per million tokens (for compatibility)"""
        return self.cost_per_1k_output * 1000
    
    def has_capability(self, capability: str) -> bool:
        """Check if model has a specific capability"""
        return capability in self.capabilities


class ModelCatalog:
    """
    Centralized model catalog
    
    Usage:
        catalog = ModelCatalog()
        gpt4o = catalog.get("gpt-4o")
        chat_models = catalog.list_by_type("chat")
        cheap_models = catalog.filter_by_cost(max_cost_per_1k=0.001)
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize catalog
        
        Args:
            config_path: Path to models.yaml (defaults to v2/config/models.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent / "models.yaml"
        
        self.config_path = Path(config_path)
        self._models: Dict[str, Model] = {}
        self._categories: Dict[str, List[str]] = {}
        self._load_catalog()
    
    def _load_catalog(self):
        """Load model catalog from YAML"""
        with open(self.config_path) as f:
            data = yaml.safe_load(f)
        
        # Load chat models
        for model_data in data.get('chat_models', []):
            model = Model(
                id=model_data['id'],
                name=model_data['name'],
                display_name=model_data['display_name'],
                provider=model_data['provider'],
                type=model_data['type'],
                context_window=model_data['context_window'],
                cost_per_1k_input=model_data['cost_per_1k_input'],
                cost_per_1k_output=model_data['cost_per_1k_output'],
                quality_score=model_data['quality_score'],
                capabilities=model_data.get('capabilities', [])
            )
            self._models[model.id] = model
            # Also index by name for backward compatibility
            if model.name != model.id:
                self._models[model.name] = model
        
        # Load embedding models
        for model_data in data.get('embedding_models', []):
            model = Model(
                id=model_data['id'],
                name=model_data['name'],
                display_name=model_data['display_name'],
                provider=model_data['provider'],
                type=model_data['type'],
                context_window=model_data['context_window'],
                cost_per_1k_input=model_data['cost_per_1k_input'],
                cost_per_1k_output=model_data['cost_per_1k_output'],
                quality_score=model_data['quality_score'],
                capabilities=model_data.get('capabilities', []),
                dimensions=model_data.get('dimensions')
            )
            self._models[model.id] = model
            if model.name != model.id:
                self._models[model.name] = model
        
        # Load judge models
        for model_data in data.get('judge_models', []):
            model = Model(
                id=model_data['id'],
                name=model_data['name'],
                display_name=model_data['display_name'],
                provider=model_data['provider'],
                type=model_data['type'],
                context_window=model_data['context_window'],
                cost_per_1k_input=model_data['cost_per_1k_input'],
                cost_per_1k_output=model_data['cost_per_1k_output'],
                quality_score=model_data['quality_score'],
                capabilities=model_data.get('capabilities', []),
                reliability_score=model_data.get('reliability_score')
            )
            self._models[model.id] = model
            if model.name != model.id:
                self._models[model.name] = model
        
        # Load categories
        self._categories = data.get('categories', {})
    
    def get(self, model_id: str) -> Optional[Model]:
        """Get model by ID or name"""
        return self._models.get(model_id)
    
    def list_all(self) -> List[Model]:
        """List all models (unique by ID)"""
        seen = set()
        unique_models = []
        for model in self._models.values():
            if model.id not in seen:
                seen.add(model.id)
                unique_models.append(model)
        return unique_models
    
    def list_by_type(self, model_type: str) -> List[Model]:
        """List models by type (chat, embedding, etc.)"""
        return [m for m in self.list_all() if m.type == model_type]
    
    def list_by_provider(self, provider: str) -> List[Model]:
        """List models by provider"""
        return [m for m in self.list_all() if m.provider == provider]
    
    def list_by_category(self, category: str) -> List[Model]:
        """List models in a category"""
        model_ids = self._categories.get(category, [])
        return [self._models[mid] for mid in model_ids if mid in self._models]
    
    def filter_by_cost(
        self,
        max_cost_per_1k: Optional[float] = None,
        min_quality: Optional[float] = None
    ) -> List[Model]:
        """Filter models by cost and quality"""
        models = self.list_all()
        
        if max_cost_per_1k is not None:
            models = [m for m in models if m.cost_per_1k_input <= max_cost_per_1k]
        
        if min_quality is not None:
            models = [m for m in models if m.quality_score >= min_quality]
        
        return models
    
    def get_recommended(self, category: str) -> List[Model]:
        """Get recommended models for a category"""
        return self.list_by_category(f"recommended_{category}")
    
    def get_best_value(self, model_type: str) -> Optional[Model]:
        """Get best value model (quality >= 7, lowest cost)"""
        models = [
            m for m in self.list_by_type(model_type)
            if m.quality_score >= 7.0
        ]
        
        if not models:
            return None
        
        return min(models, key=lambda m: m.cost_per_1k_input)
    
    def __len__(self) -> int:
        """Get number of unique models"""
        return len(self.list_all())
    
    def __repr__(self):
        return f"<ModelCatalog models={len(self)} categories={len(self._categories)}>"


# Global instance
_catalog = None

def get_model_catalog() -> ModelCatalog:
    """Get global model catalog instance"""
    global _catalog
    if _catalog is None:
        _catalog = ModelCatalog()
    return _catalog
