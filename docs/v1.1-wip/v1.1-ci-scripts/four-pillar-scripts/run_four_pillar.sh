#!/bin/bash
set -e

echo "[Base120 v1.1] Running Four-Pillar CI Validation"

# 1. Check dependencies
./check_dependencies.sh

# 2. Validate Base120 schema
./validate_base120_schema.sh

# 3. Run PNPM install
echo "Running PNPM install..."
pnpm install

# 4. Validate artifacts folder
echo "Validating artifacts folder..."
ls artifacts/

echo "[Base120 v1.1] Four-Pillar CI Completed"
