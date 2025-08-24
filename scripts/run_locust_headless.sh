#!/bin/bash
# scripts/run_locust_headless.sh

SCENARIO="B"
USERS=8
SPAWN_RATE=2
DURATION="6m"
BASE_URL=""

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --Scenario) SCENARIO="$2"; shift ;;
    --BaseUrl) BASE_URL="$2"; shift ;;
    --Users) USERS="$2"; shift ;;
    --SpawnRate) SPAWN_RATE="$2"; shift ;;
    --Duration) DURATION="$2"; shift ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

if [[ -z "$BASE_URL" ]]; then
  echo "Error: Please provide --BaseUrl (e.g., https://<api-id>.execute-api.us-east-1.amazonaws.com)"
  exit 1
fi

export SCENARIO="$SCENARIO"
export NER_API_BASE_URL="$BASE_URL"

locust -f testing/locust_ner.py \
  --headless \
  -u "$USERS" -r "$SPAWN_RATE" -t "$DURATION" \
  --csv "locust-$SCENARIO"
