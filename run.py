import sys
from aicl.core.engine import AICLEngine

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'example.aicl'
    engine = AICLEngine(config_path=config_path)
    engine.run()