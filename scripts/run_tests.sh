#!/bin/bash
set -e

# This script builds all components and runs a test suite defined in a .test-cl file.

TEST_FILE="${1:-example.test-cl}"

if [ ! -f "$TEST_FILE" ]; then
    echo "Error: Test file not found at $TEST_FILE" >&2
    exit 1
fi

# 1. Build all provider containers (including assertion providers)
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

# 4. Create a main entrypoint for the test runner
cat <<EOF > run_tests.py
import sys
from aicl.core.engine import AICLEngine

if __name__ == "__main__":
    test_path = sys.argv[1] if len(sys.argv) > 1 else 'example.test-cl'
    engine = AICLEngine(config_path=test_path) # The engine uses a generic config path
    engine.test(test_config_path=test_path)
EOF

export PYTHONPATH=$PYTHONPATH:./src

# 5. Run the tests
echo "\n--- Running Tests from $TEST_FILE ---"
python run_tests.py "$TEST_FILE"

echo "\n--- Tests Finished ---"
