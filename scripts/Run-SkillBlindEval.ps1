[CmdletBinding()]
param(
    [ValidateSet("skill_pressure_cases.json", "skill_holdout_cases.json")]
    [string]$Suite = "skill_holdout_cases.json",

    [ValidateRange(1, 13)]
    [int]$Limit = 4,

    [int]$Seed = 20261114
)

$ErrorActionPreference = "Stop"
$exitCode = 1
$secureKey = $null
$keyPointer = [IntPtr]::Zero
$environmentNames = @(
    "OPENAI_API_KEY",
    "DGSI_GENERATOR_MODEL",
    "DGSI_JUDGE_MODEL",
    "DGSI_GENERATOR_FAMILY",
    "DGSI_JUDGE_FAMILY",
    "DGSI_JUDGE_INDEPENDENCE_NOTE"
)

try {
    $maximumCases = if ($Suite -eq "skill_holdout_cases.json") { 8 } else { 13 }
    if ($Limit -gt $maximumCases) {
        throw "Limit $Limit exceeds the $maximumCases cases available in $Suite."
    }

    $repoRoot = Split-Path -Parent $PSScriptRoot
    $runner = Join-Path $PSScriptRoot "run_skill_blind_eval.py"
    if (-not (Test-Path -LiteralPath $runner)) {
        throw "Cannot find runner: $runner"
    }
    $null = Get-Command python -ErrorAction Stop

    $env:DGSI_GENERATOR_MODEL = (Read-Host "Generator model ID").Trim()
    $env:DGSI_JUDGE_MODEL = (Read-Host "Judge model ID (must be a different model)").Trim()
    $env:DGSI_GENERATOR_FAMILY = (Read-Host "Generator model family").Trim()
    $env:DGSI_JUDGE_FAMILY = (Read-Host "Judge model family (must be independently different)").Trim()
    $env:DGSI_JUDGE_INDEPENDENCE_NOTE = (Read-Host "Describe why the judge setup is independent").Trim()

    if ([string]::IsNullOrWhiteSpace($env:DGSI_GENERATOR_MODEL) -or
        [string]::IsNullOrWhiteSpace($env:DGSI_JUDGE_MODEL) -or
        [string]::IsNullOrWhiteSpace($env:DGSI_GENERATOR_FAMILY) -or
        [string]::IsNullOrWhiteSpace($env:DGSI_JUDGE_FAMILY) -or
        [string]::IsNullOrWhiteSpace($env:DGSI_JUDGE_INDEPENDENCE_NOTE)) {
        throw "Model IDs, model families and the independence note are required."
    }
    if ($env:DGSI_GENERATOR_MODEL -eq $env:DGSI_JUDGE_MODEL) {
        throw "Generator and judge model IDs must differ."
    }
    if ($env:DGSI_GENERATOR_FAMILY -ieq $env:DGSI_JUDGE_FAMILY) {
        throw "Generator and judge model families must differ."
    }

    $secureKey = Read-Host "OpenAI API key (input is hidden)" -AsSecureString
    $keyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $env:OPENAI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($keyPointer)

    $callCount = $Limit * 3
    Write-Host ""
    Write-Host "Suite: $Suite"
    Write-Host "Cases: $Limit"
    Write-Host "Maximum Responses API calls: $callCount"
    Write-Host "Output: reports/skill_blind_eval/ (local, git-ignored)"
    Write-Host "No raw/private telemetry should be included."
    $confirmation = Read-Host "Type RUN to authorize this live API run"
    if ($confirmation -cne "RUN") {
        Write-Host "Cancelled; no API calls were made."
        $exitCode = 2
    }
    else {
        Push-Location $repoRoot
        try {
            & python $runner --suite $Suite --execute-live --limit $Limit --seed $Seed
            $exitCode = $LASTEXITCODE
        }
        finally {
            Pop-Location
        }
    }
}
catch {
    Write-Host $_ -ForegroundColor Red
    $exitCode = 1
}
finally {
    foreach ($name in $environmentNames) {
        Remove-Item "Env:$name" -ErrorAction SilentlyContinue
    }
    if ($keyPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($keyPointer)
    }
    if ($null -ne $secureKey) {
        $secureKey.Dispose()
    }
}

exit $exitCode
