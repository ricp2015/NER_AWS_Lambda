param([string]$Profile = "learnerlab", [string]$StackName = "ner-lambda-stack")
sam delete --stack-name $StackName --profile $Profile
