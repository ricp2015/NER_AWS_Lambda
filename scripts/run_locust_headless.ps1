# scripts/run_locust_headless.ps1
param(
  [ValidateSet('A','B','C','D')] [string]$Scenario = 'B',
  [string]$BaseUrl,                 # required for headless
  [int]$Users = 8,                  # used mainly by A/D
  [int]$SpawnRate = 2,
  [string]$Duration = '6m'          # e.g., 6m, 10m
)

if (-not $BaseUrl) { Write-Error "Please provide -BaseUrl (e.g., https://<api-id>.execute-api.us-east-1.amazonaws.com)"; exit 1 }
$env:SCENARIO = $Scenario
$env:NER_API_BASE_URL = $BaseUrl

locust -f testing\locust_ner.py `
  --headless `
  -u $Users -r $SpawnRate -t $Duration `
  --csv "locust-$Scenario"
