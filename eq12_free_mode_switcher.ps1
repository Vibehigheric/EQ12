
# EQ12 Auto-Switcher for Free Alternatives
param([string]$Service)

switch ($Service) {
    "odds" {
        if (-not $env:ODDS_API_KEY) {
            Write-Host " Switching to cached odds data"
            python "C:/EQ12/cache/eq12_odds_backup.py"
        }
    }
    "weather" {
        if (-not $env:OPENWEATHER_API_KEY) {
            Write-Host " Using Open-Meteo (free weather API)"
            $weather = Invoke-RestMethod "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true"
            return $weather
        }
    }
    "ai" {
        if (-not $env:OPENAI_API_KEY) {
            Write-Host " Switching to Groq (free AI API)"
            # Implement Groq fallback
        }
    }
}
