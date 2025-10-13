"""
Test experiment document database
"""
import os
import pytest
from datetime import datetime
from experiments.storage import ExperimentDocDB


@pytest.fixture
def db():
    """Create test database connection"""
    if not os.getenv('DATABASE_URL'):
        pytest.skip("DATABASE_URL not set")
    
    return ExperimentDocDB()


def test_save_and_retrieve_experiment(db):
    """Test saving and retrieving experiment"""
    experiment_id = f"test_exp_{datetime.now().timestamp()}"
    
    outputs = {
        'step_1': {'result': 'success', 'tokens': 100},
        'total_tokens': 100
    }
    
    metadata = {
        'provider': 'test_provider',
        'tags': ['test', 'automated'],
        'total_cost': 0.001
    }
    
    # Save
    doc_id = db.save_experiment(
        experiment_id=experiment_id,
        outputs=outputs,
        metadata=metadata
    )
    
    assert doc_id > 0
    
    # Retrieve
    doc = db.get_by_id(experiment_id)
    
    assert doc is not None
    assert doc['experiment_id'] == experiment_id
    assert doc['outputs']['total_tokens'] == 100
    assert doc['metadata']['provider'] == 'test_provider'
    assert 'test' in doc['metadata']['tags']


def test_query_by_tags(db):
    """Test querying experiments by tags - THIS WAS THE BUG"""
    experiment_id = f"test_tags_{datetime.now().timestamp()}"
    
    outputs = {'total_tokens': 50}
    metadata = {
        'provider': 'test_provider',
        'tags': ['security', 'azure', 'test']
    }
    
    # Save experiment with tags
    db.save_experiment(
        experiment_id=experiment_id,
        outputs=outputs,
        metadata=metadata
    )
    
    # Query by tags
    results = db.query(tags=['security', 'azure'])
    
    assert len(results) > 0
    assert any(r['experiment_id'] == experiment_id for r in results)


def test_compare_experiments(db):
    """Test comparing multiple experiments"""
    exp1_id = f"test_compare_1_{datetime.now().timestamp()}"
    exp2_id = f"test_compare_2_{datetime.now().timestamp()}"
    
    # Save two experiments
    db.save_experiment(
        experiment_id=exp1_id,
        outputs={'total_tokens': 100},
        metadata={'total_cost': 0.001, 'quality_score': 80}
    )
    
    db.save_experiment(
        experiment_id=exp2_id,
        outputs={'total_tokens': 200},
        metadata={'total_cost': 0.002, 'quality_score': 90}
    )
    
    # Compare
    comparison = db.compare([exp1_id, exp2_id])
    
    assert len(comparison['experiments']) == 2
    assert 'total_cost' in comparison['metrics']
    assert comparison['metrics']['total_cost']['min'] == 0.001
    assert comparison['metrics']['total_cost']['max'] == 0.002


def test_get_best_by_cost(db):
    """Test getting best experiments by cost"""
    exp_id = f"test_best_{datetime.now().timestamp()}"
    
    db.save_experiment(
        experiment_id=exp_id,
        outputs={'total_tokens': 50},
        metadata={'total_cost': 0.0005}
    )
    
    # Get best (lowest cost)
    results = db.get_best(by_metric='total_cost', ascending=True, limit=5)
    
    assert len(results) > 0
    # Verify sorted ascending by cost
    costs = [r['metadata'].get('total_cost') for r in results if r['metadata'].get('total_cost')]
    assert costs == sorted(costs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
