#!/bin/bash
set -euo pipefail

echo "🔨 Building SAM project..."
sam build --use-container
