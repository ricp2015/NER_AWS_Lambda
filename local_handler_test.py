import json
from src.handler import lambda_handler

event = {"body": json.dumps({"text": "Tim Cook met Elon Musk in Rome on Monday."})}
resp = lambda_handler(event, None)

print("status:", resp["statusCode"])
print("json:", json.loads(resp["body"]))
