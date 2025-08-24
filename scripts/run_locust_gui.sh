#!/bin/bash

SCENARIO="B"
BASE_URL=""
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --Scenario) SCENARIO="$2"; shift ;;
    --BaseUrl) BASE_URL="$2"; shift ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done
export SCENARIO="$SCENARIO"
if [[ -n "$BASE_URL" ]]; then
  export NER_API_BASE_URL="$BASE_URL"
fi

locust -f testing/locust_ner.py
