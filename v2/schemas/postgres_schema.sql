-- AICL v2 PostgreSQL Schema
-- Version: 1.0.0
-- Description: Experiment storage for RAG pipeline testing and optimization

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
  id SERIAL PRIMARY KEY,
  version TEXT NOT NULL,
  applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  description TEXT
);

-- Core experiment metadata
CREATE TABLE IF NOT EXISTS experiments (
  id SERIAL PRIMARY KEY,
  experiment_id TEXT UNIQUE NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  config_file TEXT,
  description TEXT,
  status TEXT DEFAULT 'pending',
  version INTEGER DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model configurations
CREATE TABLE IF NOT EXISTS configurations (
  id SERIAL PRIMARY KEY,
  experiment_id TEXT NOT NULL,
  chat_model TEXT,
  embedding_model TEXT,
  temperature REAL,
  max_tokens INTEGER,
  top_k INTEGER,
  provider TEXT,
  rerank BOOLEAN,
  other_params TEXT,
  FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Performance metrics
CREATE TABLE IF NOT EXISTS results (
  id SERIAL PRIMARY KEY,
  experiment_id TEXT NOT NULL,
  total_cost_usd REAL,
  embedding_cost_usd REAL,
  chat_cost_usd REAL,
  total_tokens INTEGER,
  prompt_tokens INTEGER,
  completion_tokens INTEGER,
  latency_ms REAL,
  end_to_end_ms REAL,
  chunks_retrieved INTEGER,
  success BOOLEAN,
  error_message TEXT,
  FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Quality evaluation scores
CREATE TABLE IF NOT EXISTS quality_scores (
  id SERIAL PRIMARY KEY,
  experiment_id TEXT NOT NULL,
  judge_model TEXT,
  judge_score REAL,
  accuracy_score REAL,
  completeness_score REAL,
  clarity_score REAL,
  relevance_score REAL,
  judge_feedback TEXT,
  FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_exp_timestamp ON experiments(timestamp);
CREATE INDEX IF NOT EXISTS idx_config_exp_id ON configurations(experiment_id);
CREATE INDEX IF NOT EXISTS idx_config_model ON configurations(chat_model);
CREATE INDEX IF NOT EXISTS idx_results_exp_id ON results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_results_cost ON results(total_cost_usd);
CREATE INDEX IF NOT EXISTS idx_quality_exp_id ON quality_scores(experiment_id);
CREATE INDEX IF NOT EXISTS idx_quality_score ON quality_scores(judge_score);

-- Initial schema version
INSERT INTO schema_version (version, description) 
VALUES ('1.0.0', 'Initial schema with experiments, configurations, results, quality_scores');
