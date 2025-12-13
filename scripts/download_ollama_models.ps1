# EQ12 Local LLM Downloader
# Downloads the necessary Ollama models for the AI Super-Cluster.

Write-Host "🚀 Starting EQ12 Local LLM Setup..." -ForegroundColor Cyan

# 1. Check for Ollama
if (Get-Command "ollama" -ErrorAction SilentlyContinue) {
    Write-Host "✅ Ollama is installed." -ForegroundColor Green
}
else {
    Write-Error "❌ Ollama is NOT installed."
    Write-Host "👉 Please download and install Ollama from https://ollama.com/download/windows" -ForegroundColor Yellow
    Write-Host "   After installation, run this script again."
    exit 1
}

# 2. Define Models to Download
$models = @(
    "llama3",           # General Intelligence (8B) - Fast & Capable
    "mistral",          # Backup General Intelligence
    "codellama",        # Code Generation (Code-Genesis)
    "nomic-embed-text", # Embeddings (for RAG/Memory)
    "llava"             # Vision (Image Analysis)
)

# 3. Pull Models
foreach ($model in $models) {
    Write-Host "`n⬇️ Pulling model: $model..." -ForegroundColor Cyan
    ollama pull $model
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $model downloaded successfully." -ForegroundColor Green
    }
    else {
        Write-Error "❌ Failed to download $model."
    }
}

# 4. List Installed Models
Write-Host "`n📋 Installed Ollama Models:" -ForegroundColor Yellow
ollama list

Write-Host "`n🎉 Local LLM Setup Complete!" -ForegroundColor Cyan
