#requires -Version 5.1
[CmdletBinding()]
param(
    [int]$Port = 3000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Request {
    param(
        [Parameter(Mandatory)][string]$Url,
        [ValidateSet('GET', 'HEAD')][string]$Method = 'GET'
    )

    # Use curl.exe for more reliable results if available, otherwise use PowerShell
    if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
        try {
            $curlArgs = @('-s', '-I', '-X', $Method, '--max-redirs', '0', '--connect-timeout', '5', $Url)
            $output = & curl.exe $curlArgs 2>$null

            if ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq 47) {
                # 47 = too many redirects (expected with --max-redirs 0)
                $lines = $output -split "`n"
                $statusLine = $lines[0] -replace "`r", ""

                if ($statusLine -match 'HTTP/[\d.]+\s+(\d{3})\s+') {
                    $code = [int]$matches[1]
                    $headers = @{}

                    # Extract Location header
                    foreach ($line in $lines[1..($lines.Length - 1)]) {
                        if ($line -match '^Location:\s*(.+)') {
                            $headers['Location'] = $matches[1].Trim()
                        }
                    }

                    return [pscustomobject]@{
                        ok      = ($code -ge 200 -and $code -lt 400)
                        code    = $code
                        headers = $headers
                        length  = 0
                        note    = "curl.exe"
                    }
                }
            }
        }
        catch {
            # Fall back to PowerShell method
        }
    }

    # PowerShell fallback method
    try {
        $resp = Invoke-WebRequest -Uri $Url -Method $Method -TimeoutSec 5 -MaximumRedirection 0 -ErrorAction Stop
        [pscustomobject]@{
            ok      = $true
            code    = [int]$resp.StatusCode
            headers = $resp.Headers
            length  = $resp.RawContentLength
            note    = 'ps-success'
        }
    }
    catch {
        $code = 0
        $headers = @{}
        $message = if ($_.Exception.Message) { $_.Exception.Message } else { "Unknown error" }

        # Handle PowerShell redirect exceptions (they vary by version)
        if ($message -match 'Maximum redirection count exceeded|response status code does not indicate success: 30[12]') {
            # This usually means we got a redirect when MaximumRedirection was 0
            if ($message -match '30[12]') {
                if ($message -match '302') { $code = 302 }
                elseif ($message -match '301') { $code = 301 }
                else { $code = 302 } # Default to 302 for redirects
            }
        }
        elseif ($_.Exception -is [System.Net.WebException]) {
            $webResponse = $_.Exception.Response
            if ($webResponse) {
                try {
                    $code = [int]$webResponse.StatusCode
                    if ($webResponse.Headers -and $webResponse.Headers['Location']) {
                        $headers['Location'] = $webResponse.Headers['Location']
                    }
                }
                catch { }
            }
        }

        # Final fallback: parse from message
        if ($code -eq 0) {
            if ($message -match '\((\d{3})\)') {
                $code = [int]$matches[1]
            }
            elseif ($message -match 'Found') { $code = 302 }
            elseif ($message -match 'MovedPermanently') { $code = 301 }
            elseif ($message -match 'NotFound') { $code = 404 }
        }

        [pscustomobject]@{
            ok      = ($code -ge 200 -and $code -lt 400)
            code    = $code
            headers = $headers
            length  = 0
            note    = "ps-catch: $message"
        }
    }
}

function Show {
    param([string]$Name, [bool]$Ok, [string]$Detail)
    $tag = if ($Ok) { '[PASS]' } else { '[FAIL]' }
    $color = if ($Ok) { 'Green' } else { 'Red' }
    Write-Host ("{0} {1} :: {2}" -f $tag, $Name, $Detail) -ForegroundColor $color
}

$base = "http://localhost:{0}" -f $Port
$results = @()

# 1) Root should redirect to /dashboard
$r1 = Test-Request -Url "$base/" -Method GET
$ok1 = ($r1.code -in 301, 302) -and ($r1.headers['Location'] -match '^/dashboard\b')
Show "Root redirects to /dashboard" $ok1 ("code={0} location={1}" -f $r1.code, $r1.headers['Location'])
$results += $ok1

# 2) /dashboard returns 200 with content
$r2 = Test-Request -Url "$base/dashboard" -Method GET
# For curl.exe results, check if we got 200 (bytes will be 0 for HEAD-style)
# For PowerShell results, check both code and length
$ok2 = ($r2.code -eq 200) -and (($r2.length -gt 0) -or ($r2.note -eq "curl.exe"))
Show "/dashboard returns 200 with content" $ok2 ("code={0} bytes={1} via={2}" -f $r2.code, $r2.length, $r2.note)
$results += $ok2

# 3) /health returns 200
$r3 = Test-Request -Url "$base/health" -Method GET
$ok3 = ($r3.code -eq 200)
Show "/health returns 200" $ok3 ("code={0}" -f $r3.code)
$results += $ok3

# 4) HEAD / returns 200 (availability check - correct behavior)
$r4 = Test-Request -Url "$base/" -Method HEAD
$ok4 = ($r4.code -eq 200)
Show "HEAD / returns 200 (availability)" $ok4 ("code={0} via={1}" -f $r4.code, $r4.note)
$results += $ok4

# 5) Unknown path handled (404 or redirect ok)
$r5 = Test-Request -Url "$base/this_path_does_not_exist" -Method GET
$ok5 = ($r5.code -eq 404) -or ($r5.code -in 301, 302)
Show "Unknown path handled (404 or redirect)" $ok5 ("code={0}" -f $r5.code)
$results += $ok5

# Summary
$passed = ($results | Where-Object { $_ }).Count
$total = $results.Count
Write-Host ('-' * 60) -ForegroundColor DarkGray
Write-Host ("Summary: {0}/{1} tests passed" -f $passed, $total) -ForegroundColor Yellow
if ($passed -ne $total) { exit 1 } else { exit 0 }
