# NER Lambda (spaCy)

Serverless Named Entity Recognition API on AWS Lambda + API Gateway (HTTP API).  
No managed AI services used. Deployed with AWS SAM.

## Prerequisites
- Windows/macOS/Linux
- Python 3.10+ (added to PATH)
- Docker Desktop (for `sam build --use-container`)
- AWS CLI v2, AWS SAM CLI
- An AWS account (e.g., AWS Academy Learner Lab)

---

## Quickstart

### 🔹 Windows (PowerShell)

```powershell
git clone <this repo>
cd ner-lambda-project

# 1) Create venv and install deps
python -m venv .venv; . .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) (Optional) local smoke test
python - <<'PY'
from src.ner import extract_entities
print(extract_entities("Alan Turing was born on June 23, 1912, in London, England."))
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

### 🔹 Linux/macOS (Bash/zsh)

git clone <this repo>
cd ner-lambda-project

# 1) Create venv and install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2) (Optional) local smoke test
python - <<'PY'
from src.ner import extract_entities
print(extract_entities("Alan Turing was born on June 23, 1912, in London, England."))
PY

# 3) Configure AWS creds (Learner Lab)
cp .env.example .env    # fill keys from "AWS Details"
chmod +x scripts/*.sh
./scripts/set-aws-creds.sh learnerlab

# 4) Build & deploy
./scripts/build.sh
sam deploy --guided --profile learnerlab   # first time only
# then: ./scripts/deploy.sh learnerlab

# 5) Get URL & test
./scripts/smoke.sh learnerlab

## Frontend (Local Demo)

A minimal frontend is provided in `front-end/index.html` to test the NER API.

### Run directly in browser
1. Open `frontend/index.html` in Chrome/Firefox.
2. Paste your API Gateway endpoint into the field.
3. Enter text and click **Extract Entities**.

### Run with Docker (nginx)
To serve the frontend on `http://localhost:8080`:

cd front-end
docker build -t ner-frontend .
docker run -d -p 8080:80 ner-frontend

Then open http://localhost:8080 in your browser.
