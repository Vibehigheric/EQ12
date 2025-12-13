<#
.SYNOPSIS
    Exports a Postman environment file populated with EQ12 X / X Ads credential variables.
.DESCRIPTION
    Reads credential values from environment variables (process, user, or machine scope) and emits a Postman
    environment JSON document. Missing values are left blank so secrets stay centralized. Defaults to writing the
    environment into configs\postman\EQ12_X_API_v2.postman_environment.json inside the repo.
.PARAMETER OutputPath
    Destination path for the Postman environment JSON. If omitted, a default path under configs\postman is used.
.PARAMETER EnvironmentName
    Friendly name used inside Postman. Defaults to "EQ12 X API v2".
.PARAMETER PassThru
    When set, returns the generated Postman environment object to the pipeline in addition to writing the file.
.EXAMPLE
    .\export_postman_environment.ps1
    Generates configs\postman\EQ12_X_API_v2.postman_environment.json using available environment variables.
.EXAMPLE
    .\export_postman_environment.ps1 -OutputPath 'C:\temp\eq12.postman_environment.json' -EnvironmentName 'EQ12 Ads'
    Writes the environment JSON to the custom path and uses the provided environment name.
#>
[CmdletBinding()]
param(
    [string]$OutputPath,
    [string]$EnvironmentName = 'EQ12 X API v2',
    [switch]$PassThru
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot

function Get-Eq12DefaultPath {
    param(
        [string]$EnvVar,
        [string]$FallbackRelative
    )

    if (-not [string]::IsNullOrWhiteSpace($EnvVar)) {
        return $EnvVar
    }

    return Join-Path -Path $repoRoot -ChildPath $FallbackRelative
}

if (-not $OutputPath) {
    $postmanDir = Get-Eq12DefaultPath -EnvVar $env:EQ12_POSTMAN_DIR -FallbackRelative 'configs\postman'
    if (-not (Test-Path -LiteralPath $postmanDir)) {
        New-Item -ItemType Directory -Path $postmanDir -Force | Out-Null
    }
    $OutputPath = Join-Path -Path $postmanDir -ChildPath 'EQ12_X_API_v2.postman_environment.json'
}

function Resolve-Eq12EnvValue {
    param(
        [string[]]$CandidateNames
    )

    foreach ($name in $CandidateNames) {
        foreach ($scope in @('Process','User','Machine')) {
            $value = [Environment]::GetEnvironmentVariable($name, $scope)
            if (-not [string]::IsNullOrWhiteSpace($value)) {
                Write-Verbose "Resolved $name from $scope scope."
                return $value
            }
        }
    }

    return ''
}

$variablePlan = @(
    @{ Key = 'consumer_key';    Candidates = @('X_CONSUMER_KEY','X_API_KEY','TWITTER_CONSUMER_KEY');           Type = 'secret' },
    @{ Key = 'consumer_secret'; Candidates = @('X_CONSUMER_SECRET','X_API_SECRET','TWITTER_CONSUMER_SECRET');    Type = 'secret' },
    @{ Key = 'access_token';    Candidates = @('X_ACCESS_TOKEN','TWITTER_ACCESS_TOKEN');                         Type = 'secret' },
    @{ Key = 'token_secret';    Candidates = @('X_ACCESS_TOKEN_SECRET','TWITTER_ACCESS_TOKEN_SECRET');           Type = 'secret' },
    @{ Key = 'bearer_token';    Candidates = @('X_BEARER_TOKEN','TWITTER_BEARER_TOKEN');                         Type = 'secret' },
    @{ Key = 'client_id';       Candidates = @('X_CLIENT_ID','X_ADS_CLIENT_ID','TWITTER_CLIENT_ID');             Type = 'secret' },
    @{ Key = 'client_secret';   Candidates = @('X_CLIENT_SECRET','X_ADS_CLIENT_SECRET','TWITTER_CLIENT_SECRET'); Type = 'secret' },
    @{ Key = 'redirect_uri';    Candidates = @('X_REDIRECT_URI','X_ADS_REDIRECT_URI');                           Type = 'text'   },
    @{ Key = 'scope';           Candidates = @('X_OAUTH_SCOPE','X_SCOPE','TWITTER_SCOPE');                        Type = 'text'   },
    @{ Key = 'ads_account_id';  Candidates = @('X_ADS_ACCOUNT_ID');                                               Type = 'text'   },
    @{ Key = 'webhook_url';     Candidates = @('X_WEBHOOK_URL','TWITTER_WEBHOOK_URL');                            Type = 'text'   }
)

$values = foreach ($entry in $variablePlan) {
    $value = Resolve-Eq12EnvValue -CandidateNames $entry.Candidates
    [PSCustomObject]@{
        key     = $entry.Key
        value   = $value
        enabled = $true
        type    = $entry.Type
    }
}

$postmanEnv = [PSCustomObject]@{
    id                      = [guid]::NewGuid().Guid
    name                    = $EnvironmentName
    values                  = $values
    _postman_variable_scope = 'environment'
    _postman_exported_at    = (Get-Date).ToString('s') + 'Z'
    _postman_exported_using = 'EQ12 export_postman_environment.ps1'
}

$postmanJson = $postmanEnv | ConvertTo-Json -Depth 5
$outputDir = Split-Path -Parent $OutputPath
if (-not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}
Set-Content -Path $OutputPath -Value $postmanJson -Encoding UTF8
Write-Host "Wrote Postman environment to $OutputPath" -ForegroundColor Green

$missing = $values | Where-Object { [string]::IsNullOrWhiteSpace($_.value) }
if ($missing) {
    $missingNames = $missing.key -join ', '
    Write-Warning "Missing values for: $missingNames. Populate the corresponding environment variables before importing into Postman."
}

if ($PassThru) {
    return $postmanEnv
}
