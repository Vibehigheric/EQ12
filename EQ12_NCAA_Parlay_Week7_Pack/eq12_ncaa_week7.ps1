# EQ12 NCAA Week 7 Parlay Suite Runner
# [Unverified] Helper script to run the builder and open outputs.
param(
    [string]$Python = "python",
    [int]$Week = 7
)

Write-Host "[EQ12] Generating NCAA Week $Week parlays ..."
& $Python ".\eq12_ncaa_week7_parlay_builder.py"

Write-Host "[EQ12] Done. See .\logs\parlays and .\outputs"
