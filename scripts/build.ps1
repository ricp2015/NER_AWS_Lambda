param([switch]$UseContainer = $true)

Remove-Item -Recurse -Force .aws-sam -ErrorAction SilentlyContinue

if ($UseContainer) { sam build --use-container } else { sam build }
