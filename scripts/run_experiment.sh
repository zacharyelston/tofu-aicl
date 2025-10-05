#!/bin/bash
set -e

# This script builds all components and runs an experiment defined in an .aicl file.

CONFIG_FILE="${1:-example.aicl}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found at $CONFIG_FILE" >&2
    exit 1
fi

# 1. Build provider containers
echo "--- Building Provider Containers ---"
./scripts/build_providers.sh

# 2. Ensure local dependencies are installed
echo "\n--- Installing Project Dependencies ---"
pip install -e . > /dev/null

# 3. Compile protobufs
PROTO_DIR="./proto"
if [ -d "$PROTO_DIR" ]; then
    echo "\n--- Compiling Protobufs ---"
    python -m grpc_tools.protoc \
        -I. \
        --python_out=. \
        --grpc_python_out=. \
        $PROTO_DIR/provider.proto
fi

# 4. Create a main entrypoint for the engine
cat <<EOF > run.py
import sys
from aicl.core.engine import AICLEngine

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'example.aicl'
    engine = AICLEngine(config_path=config_path)
    engine.run()
EOF

export PYTHONPATH=$PYTHONPATH:./src

# 5. Run the experiment
echo "\n--- Running Experiment from $CONFIG_FILE ---"
python run.py "$CONFIG_FILE"

echo "\n--- Experiment Finished ---"