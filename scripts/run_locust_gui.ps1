# scripts/run_locust_gui.ps1
param(
  [ValidateSet('A','B','C','D')] [string]$Scenario = 'B',
  [string]$BaseUrl = ''
)
$env:SCENARIO = $Scenario
if ($BaseUrl) { $env:NER_API_BASE_URL = $BaseUrl }
locust -f testing\locust_ner.py
