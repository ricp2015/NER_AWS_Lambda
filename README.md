# NER Lambda (spaCy)

Serverless Named Entity Recognition API on AWS Lambda + API Gateway (HTTP API).
No managed AI services used. Deployed with AWS SAM.

## Prerequisites
- Windows/macOS/Linux
- Python 3.10+ (added to PATH)
- Docker Desktop (for `sam build --use-container`)
- AWS CLI v2, AWS SAM CLI
- An AWS account (e.g., AWS Academy Learner Lab)

## Quickstart

```powershell
git clone <this repo>
cd ner-lambda-project

# 1) Create venv and install deps
python -m venv .venv; . .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) (Optional) local smoke test
python - <<'PY'
from src.ner import extract_entities
print(extract_entities("Tim Cook met Elon Musk in Rome on Monday."))
PY

# 3) Configure AWS creds (Learner Lab)
copy .env.example .env    # fill keys from "AWS Details"
.\scripts\set-aws-creds.ps1 -Profile learnerlab

# 4) Build & deploy
.\scripts\build.ps1
sam deploy --guided --profile learnerlab   # first time only
# then: .\scripts\deploy.ps1

# 5) Get URL & test
.\scripts\smoke.ps1 -Profile learnerlab
