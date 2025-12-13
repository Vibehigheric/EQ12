# EQ12 PowerShell XML Repair Utilities
# Quick XML validation, repair, and normalization functions for scripts

function Test-RepairXml {
    <#
    .SYNOPSIS
        Validates and repairs XML files with entity escaping and encoding normalization.
        
    .DESCRIPTION
        Loads an XML file, escapes illegal entities (&), handles encoding issues, 
        and validates proper XML structure. Outputs detailed error messages with 
        line/column information and creates a *.fixed.xml file for repairs.
        
    .PARAMETER Path
        Path to the XML file to validate and repair
        
    .PARAMETER OutputPath
        Optional output path for repaired XML. Defaults to *.fixed.xml
        
    .PARAMETER Force
        Overwrite existing repaired files without prompting
        
    .EXAMPLE
        Test-RepairXml -Path "C:\EQ12\configs\task.xml"
        
    .EXAMPLE
        Test-RepairXml -Path "C:\EQ12\configs\*.xml" -Force
        
    .EXAMPLE
        Get-ChildItem -Path "C:\EQ12" -Filter "*.xml" -Recurse | Test-RepairXml
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true, ValueFromPipelineByPropertyName = $true)]
        [Alias("FullName")]
        [string[]]$Path,
        
        [Parameter(Mandatory = $false)]
        [string]$OutputPath,
        
        [Parameter(Mandatory = $false)]
        [switch]$Force
    )
    
    begin {
        $ErrorActionPreference = "Stop"
        $results = @()
        
        Write-Verbose "Starting XML repair validation for paths: $($Path -join ', ')"
    }
    
    process {
        foreach ($filePath in $Path) {
            # Handle wildcards and multiple files
            $files = Get-ChildItem -Path $filePath -ErrorAction SilentlyContinue
            
            if (-not $files) {
                Write-Warning "No files found matching: $filePath"
                continue
            }
            
            foreach ($file in $files) {
                $result = @{
                    Path = $file.FullName
                    Status = 'Unknown'
                    ErrorMessage = $null
                    LineNumber = $null
                    ColumnNumber = $null
                    OutputPath = $null
                    BytesFixed = 0
                }
                
                try {
                    Write-Verbose "Processing: $($file.FullName)"
                    
                    # Read content with encoding detection
                    $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
                    $originalLength = $content.Length
                    
                    # Track if we made any changes
                    $modified = $false
                    
                    # Fix encoding issues - ensure proper XML declaration
                    $xmlDeclPattern = '^\s*<\?xml\s+version\s*=\s*["\x27]1\.0["\x27]\s+encoding\s*=\s*["\x27](UTF-8|utf-8)["\x27]\s*\?>'
                    if ($content -notmatch $xmlDeclPattern) {
                        # Remove existing XML declaration and add UTF-8 one
                        $content = $content -replace '^\s*<\?xml[^>]*\?>', ''
                        $content = "<?xml version=`"1.0`" encoding=`"UTF-8`"?>`r`n$($content.TrimStart())"
                        $modified = $true
                        Write-Verbose "Fixed XML declaration"
                    }
                    
                    # Fix unescaped ampersands (& not followed by valid XML entities)
                    $ampPattern = '(?<!&)&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)'
                    if ($content -match $ampPattern) {
                        $content = $content -replace $ampPattern, '&amp;'
                        $modified = $true
                        Write-Verbose "Fixed unescaped ampersands"
                    }
                    
                    # Validate XML structure
                    try {
                        $xmlDoc = New-Object System.Xml.XmlDocument
                        $xmlDoc.LoadXml($content)
                        
                        if ($modified) {
                            $result.Status = 'Fixed'
                        } else {
                            $result.Status = 'Valid'
                        }
                        $result.BytesFixed = $originalLength - $content.Length
                        
                        # Save repaired content if modified
                        if ($modified) {
                            if (-not $OutputPath) {
                                $result.OutputPath = [System.IO.Path]::ChangeExtension($file.FullName, ".fixed.xml")
                            } else {
                                $result.OutputPath = $OutputPath
                            }
                            
                            if ((Test-Path $result.OutputPath) -and -not $Force) {
                                $response = Read-Host "File $($result.OutputPath) exists. Overwrite? (y/N)"
                                if ($response -ne 'y' -and $response -ne 'Y') {
                                    Write-Warning "Skipped overwrite for: $($result.OutputPath)"
                                    $result.Status = 'Skipped'
                                    $results += $result
                                    continue
                                }
                            }
                            
                            Set-Content -Path $result.OutputPath -Value $content -Encoding UTF8 -NoNewline
                            Write-Host "✅ FIXED: $($file.Name) → $([System.IO.Path]::GetFileName($result.OutputPath))" -ForegroundColor Green
                        } else {
                            Write-Host "✅ VALID: $($file.Name)" -ForegroundColor Green
                        }
                        
                    } catch {
                        $result.Status = 'Invalid'
                        $result.ErrorMessage = $_.Exception.Message
                        
                        # Try to extract line/column from error message
                        if ($_.Exception.Message -match 'line\s+(\d+).*position\s+(\d+)') {
                            $result.LineNumber = [int]$Matches[1]
                            $result.ColumnNumber = [int]$Matches[2]
                        }
                        
                        Write-Host "❌ INVALID XML: $($file.Name)" -ForegroundColor Red
                        Write-Host "   Error: $($result.ErrorMessage)" -ForegroundColor Yellow
                        if ($result.LineNumber) {
                            Write-Host "   Location: Line $($result.LineNumber), Column $($result.ColumnNumber)" -ForegroundColor Yellow
                        }
                    }
                    
                } catch {
                    $result.Status = 'Error'
                    $result.ErrorMessage = $_.Exception.Message
                    Write-Host "❌ ERROR: $($file.Name) - $($_.Exception.Message)" -ForegroundColor Red
                }
                
                $results += $result
            }
        }
    }
    
    end {
        # Summary report
        $summary = $results | Group-Object Status | ForEach-Object {
            [PSCustomObject]@{
                Status = $_.Name
                Count = $_.Count
                Files = $_.Group.Path
            }
        }
        
        Write-Host "`n📊 XML Repair Summary:" -ForegroundColor Cyan
        foreach ($group in $summary) {
            $color = switch ($group.Status) {
                'Valid' { 'Green' }
                'Fixed' { 'Yellow' }
                'Invalid' { 'Red' }
                'Error' { 'Magenta' }
                'Skipped' { 'Gray' }
                default { 'White' }
            }
            Write-Host "   $($group.Status): $($group.Count) files" -ForegroundColor $color
        }
        
        return $results
    }
}

function Repair-AllXmlTasks {
    <#
    .SYNOPSIS
        Bulk repair all XML files in the EQ12 project structure.
        
    .DESCRIPTION
        Scans for XML files in common EQ12 locations and repairs encoding/entity issues.
        
    .PARAMETER RootPath
        Root path to scan for XML files. Defaults to C:\EQ12
        
    .EXAMPLE
        Repair-AllXmlTasks
        
    .EXAMPLE
        Repair-AllXmlTasks -RootPath "D:\Projects\EQ12" -Verbose
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$RootPath = "C:\EQ12"
    )
    
    Write-Host "🔧 EQ12 Bulk XML Repair Starting..." -ForegroundColor Cyan
    Write-Host "   Root Path: $RootPath" -ForegroundColor Gray
    
    # Common XML locations in EQ12 structure
    $searchPaths = @(
        "$RootPath\configs\*.xml"
        "$RootPath\scripts\**\*.xml"
        "$RootPath\data\**\*.xml"
    )
    
    $allResults = @()
    
    foreach ($searchPath in $searchPaths) {
        Write-Verbose "Scanning: $searchPath"
        try {
            $results = Test-RepairXml -Path $searchPath -Force -Verbose:$VerbosePreference
            $allResults += $results
        } catch {
            Write-Warning "Failed to process path ${searchPath}: $($_.Exception.Message)"
        }
    }
    
    # Generate detailed report
    $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    $reportPath = Join-Path $RootPath "logs\xml_repair_$timestamp.json"
    $allResults | ConvertTo-Json -Depth 3 | Set-Content $reportPath -Encoding UTF8
    
    Write-Host "`n📋 Detailed report saved to: $reportPath" -ForegroundColor Green
    
    return $allResults
}

# Export functions for module usage
Export-ModuleMember -Function Test-RepairXml, Repair-AllXmlTasks