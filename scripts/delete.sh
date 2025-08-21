#!/bin/bash
set -euo pipefail

PROFILE=${1:-default}
STACK_NAME="ner-lambda-project"

echo "🗑️ Deleting stack $STACK_NAME with profile $PROFILE"
aws cloudformation delete-stack --stack-name "$STACK_NAME" --profile "$PROFILE"
