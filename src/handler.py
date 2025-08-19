import json
from typing import Any, Dict
from .ner import extract_entities

def _parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    API Gateway HTTP API may pass body as a JSON string. Local tests may pass a dict.
    This normalizes it.
    """
    body = event.get("body")
    if isinstance(body, dict):
        return body
    if isinstance(body, str):
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    # Allow direct call: event itself is the body
    return event if isinstance(event, dict) else {}

def lambda_handler(event, context) -> Dict[str, Any]:
    body = _parse_body(event)
    text = body.get("text")

    if not text or not isinstance(text, str):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing or invalid 'text' field"})
        }

    entities = extract_entities(text)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"entities": entities})
    }
