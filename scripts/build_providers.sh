#!/bin/bash
set -e

# This script builds all provider Docker containers.

ROOT_DIR=$(dirname "$0")/..
PROVIDERS_DIR="$ROOT_DIR/providers"
PROTO_DIR="$ROOT_DIR/proto"

for provider_path in "$PROVIDERS_DIR"/*/; do
    if [ -f "$provider_path/Dockerfile" ]; then
        provider_name=$(basename "$provider_path")
        image_name="aicl/$provider_name:1.0.0"
        echo "Building $provider_name provider -> $image_name..."

        # Build from root directory with provider-specific context
        docker build -t "$image_name" -f "$provider_path/Dockerfile" .

        echo "Successfully built $image_name"
        echo "------------------------------------"
    fi
done

echo "All provider containers built successfully."