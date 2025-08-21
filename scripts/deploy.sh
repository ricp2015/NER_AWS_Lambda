#!/bin/bash
set -euo pipefail

PROFILE=${1:-default}

echo "🚀 Deploying SAM project with AWS profile: $PROFILE"
sam deploy --guided --profile "$PROFILE"
