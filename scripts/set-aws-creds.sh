#!/bin/bash
set -eo pipefail

PROFILE=${1:-default}
ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
  echo "⚠️  $ENV_FILE not found. Please create it from .env.example and fill in AWS keys."
  exit 1
fi

export $(grep -v '^#' "$ENV_FILE" | xargs)

echo "Configuring AWS CLI for profile: $PROFILE"
aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID" --profile "$PROFILE"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY" --profile "$PROFILE"
aws configure set region "$AWS_REGION" --profile "$PROFILE"

echo "AWS profile $PROFILE configured"
