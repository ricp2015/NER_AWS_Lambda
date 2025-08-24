# scripts/run_locust_headless.ps1
param(
  [ValidateSet('A','B','C','D')] [string]$Scenario = 'B',
  [string]$BaseUrl,
  [int]$Users = 8,
  [int]$SpawnRate = 2,
  [string]$Duration = '6m'
)

if (-not $BaseUrl) { Write-Error "Please provide -BaseUrl (e.g., https://<api-id>.execute-api.us-east-1.amazonaws.com)"; exit 1 }
$env:SCENARIO = $Scenario
$env:NER_API_BASE_URL = $BaseUrl

locust -f testing\locust_ner.py `
  --headless `
  -u $Users -r $SpawnRate -t $Duration `
  --csv "locust-$Scenario"
