#!/bin/bash
# Minimal MRCC hash generator for Base120 v1.1
# Usage: ./mrcc_hash_generator.sh <artifact_path> [--version v1.1]

set -e

ARTIFACT_PATH="${1:-.}"
VERSION="${2:-v1.1}"

if [ ! -d "$ARTIFACT_PATH" ] && [ ! -f "$ARTIFACT_PATH" ]; then
    echo "Error: Artifact path $ARTIFACT_PATH does not exist."
    exit 1
fi

echo "[MRCC] Generating SHA-256 hashes for artifacts in $ARTIFACT_PATH (version $VERSION)"

# Find all files (skip directories)
find "$ARTIFACT_PATH" -type f | while read file; do
    HASH=$(sha256sum "$file" | awk '{print $1}')
    echo "$file | SHA256: $HASH | MRCC Version: $VERSION"
done
