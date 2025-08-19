param([switch]$UseContainer = $true)

# Clean old build
Remove-Item -Recurse -Force .aws-sam -ErrorAction SilentlyContinue

# Build with/without Docker
if ($UseContainer) { sam build --use-container } else { sam build }
