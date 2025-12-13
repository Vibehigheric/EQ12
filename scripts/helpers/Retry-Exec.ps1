<#
EQ12 patch
Retry-Exec: Run a ScriptBlock with retries and exponential backoff.
#>

## EQ12 patch: Retry helper functions only; no script-level param to allow dot-sourcing in module
function Retry-Exec_Internal {
    param($ScriptBlock, $MaxRetries, $BaseDelaySeconds, $OnError)
    $attempt = 0
    while ($true) {
        try {
            $attempt++
            Write-Verbose "Retry-Exec: attempt $attempt"
            return & $ScriptBlock
        } catch {
            Write-Warning "Retry-Exec: attempt $attempt failed: $_"
            if ($OnError) { & $OnError $_ }
            if ($attempt -ge $MaxRetries) {
                throw "Retry-Exec: failed after $attempt attempts: $_"
            }
            $delay = $BaseDelaySeconds * [math]::Pow(2, $attempt - 1) * (0.8 + (Get-Random -Minimum 0 -Maximum 0.4))
            Write-Verbose "Retry-Exec: sleeping $delay seconds before retry"
            Start-Sleep -Seconds $delay
        }
    }
}

# EQ12 patch: removed CmdletBinding() for compatibility in this environment
function Invoke-Eq12Retry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [ScriptBlock]$ScriptBlock,

        [Parameter(Mandatory=$false)]
        [int]$MaxRetries = 3,

        [Parameter(Mandatory=$false)]
        [double]$BaseDelaySeconds = 1.0,

        [Parameter(Mandatory=$false)]
        [ScriptBlock]$OnError
    )

    # Validate inputs
    if ($MaxRetries -lt 1) { throw [System.ArgumentOutOfRangeException]::new('MaxRetries','Must be >= 1') }
    if ($BaseDelaySeconds -le 0) { throw [System.ArgumentOutOfRangeException]::new('BaseDelaySeconds','Must be > 0') }

    return Retry-Exec_Internal -ScriptBlock $ScriptBlock -MaxRetries $MaxRetries -BaseDelaySeconds $BaseDelaySeconds -OnError $OnError
}

Export-ModuleMember -Function Invoke-Eq12Retry, Retry-Exec_Internal
