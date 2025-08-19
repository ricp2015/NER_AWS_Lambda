param([string]$Profile = "learnerlab", [string]$EnvPath = ".env")

if (!(Test-Path $EnvPath)) { Write-Error "Missing $EnvPath"; exit 1 }

$kv = @{}
(Get-Content $EnvPath) | ForEach-Object {
  if ($_ -and $_ -notmatch '^\s*#') {
    $k,$v = $_ -split '=',2
    if ($k) { $kv[$k.Trim()] = $v.Trim() }
  }
}

aws configure set aws_access_key_id     $kv.AWS_ACCESS_KEY_ID     --profile $Profile
aws configure set aws_secret_access_key $kv.AWS_SECRET_ACCESS_KEY --profile $Profile
aws configure set region                ($kv.AWS_DEFAULT_REGION   ? $kv.AWS_DEFAULT_REGION : "us-east-1") --profile $Profile
aws configure set aws_session_token     $kv.AWS_SESSION_TOKEN     --profile $Profile

aws sts get-caller-identity --profile $Profile
