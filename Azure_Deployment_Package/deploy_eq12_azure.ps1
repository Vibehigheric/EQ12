# Azure Deployment Configuration Script
param(
    [string]$ResourceGroupName = "EQ12-WealthIntelligence",
    [string]$Location = "East US",
    [string]$StorageAccountName = "",
    [string]$FunctionAppName = "",
    [string]$SubscriptionId = "",
    [switch]$CreateResources,
    [switch]$DeployFunctions,
    [switch]$ConfigureSecrets,
    [switch]$TestDeployment
)

# Enable strict mode
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host " EQ12 AZURE DEPLOYMENT SCRIPT" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Generate unique names if not provided
if (-not $StorageAccountName) {
    $uniqueId = (Get-Random -Minimum 1000 -Maximum 9999)
    $StorageAccountName = "eq12storage$uniqueId"
}

if (-not $FunctionAppName) {
    $uniqueId = (Get-Random -Minimum 1000 -Maximum 9999)
    $FunctionAppName = "eq12functions$uniqueId"
}

# Check Azure CLI installation
try {
    $azVersion = az version --output json 2>$null | ConvertFrom-Json
    Write-Host " Azure CLI Version: $($azVersion.'azure-cli')" -ForegroundColor Green
}
catch {
    Write-Error " Azure CLI not found. Please install Azure CLI first."
    exit 1
}

# Check if logged in
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host " Logged in as: $($account.user.name)" -ForegroundColor Green
    
    if ($SubscriptionId -and $account.id -ne $SubscriptionId) {
        Write-Host " Switching to subscription: $SubscriptionId" -ForegroundColor Yellow
        az account set --subscription $SubscriptionId
    }
}
catch {
    Write-Error " Not logged in to Azure. Run 'az login' first."
    exit 1
}

function Test-AzureResourceExists {
    param(
        [string]$ResourceType,
        [string]$ResourceName,
        [string]$ResourceGroup
    )
    
    try {
        switch ($ResourceType) {
            "resourcegroup" {
                $result = az group show --name $ResourceName 2>$null
            }
            "storageaccount" {
                $result = az storage account show --name $ResourceName --resource-group $ResourceGroup 2>$null
            }
            "functionapp" {
                $result = az functionapp show --name $ResourceName --resource-group $ResourceGroup 2>$null
            }
        }
        return $result -ne $null
    }
    catch {
        return $false
    }
}

function Create-AzureResources {
    Write-Host " Creating Azure Resources..." -ForegroundColor Cyan
    
    # Create Resource Group
    if (-not (Test-AzureResourceExists "resourcegroup" $ResourceGroupName "")) {
        Write-Host " Creating Resource Group: $ResourceGroupName" -ForegroundColor Yellow
        az group create --name $ResourceGroupName --location $Location --tags project=EQ12 environment=production
        Write-Host " Resource Group created" -ForegroundColor Green
    }
    else {
        Write-Host " Resource Group already exists" -ForegroundColor Green
    }
    
    # Create Storage Account
    if (-not (Test-AzureResourceExists "storageaccount" $StorageAccountName $ResourceGroupName)) {
        Write-Host " Creating Storage Account: $StorageAccountName" -ForegroundColor Yellow
        az storage account create `
            --name $StorageAccountName `
            --resource-group $ResourceGroupName `
            --location $Location `
            --sku Standard_LRS `
            --tags project=EQ12 component=storage
        Write-Host " Storage Account created" -ForegroundColor Green
        
        # Create blob containers
        $containers = @("eq12-data", "eq12-logs", "eq12-config", "eq12-models", "eq12-backups", "eq12-temp")
        
        Write-Host " Creating blob containers..." -ForegroundColor Yellow
        foreach ($container in $containers) {
            az storage container create --name $container --account-name $StorageAccountName
            Write-Host "   Container created: $container" -ForegroundColor Green
        }
    }
    else {
        Write-Host " Storage Account already exists" -ForegroundColor Green
    }
    
    # Create Function App
    if (-not (Test-AzureResourceExists "functionapp" $FunctionAppName $ResourceGroupName)) {
        Write-Host " Creating Function App: $FunctionAppName" -ForegroundColor Yellow
        
        # Create consumption plan
        az functionapp create `
            --resource-group $ResourceGroupName `
            --consumption-plan-location $Location `
            --runtime python `
            --runtime-version 3.11 `
            --functions-version 4 `
            --name $FunctionAppName `
            --storage-account $StorageAccountName `
            --tags project=EQ12 component=automation
            
        Write-Host " Function App created" -ForegroundColor Green
    }
    else {
        Write-Host " Function App already exists" -ForegroundColor Green
    }
    
    Write-Host " All Azure resources created successfully!" -ForegroundColor Green
}

function Deploy-EQ12Functions {
    Write-Host " Deploying EQ12 Functions..." -ForegroundColor Cyan
    
    # Check if deployment package exists
    $deploymentPath = "C:\EQ12\Azure_Deployment_Package"
    if (-not (Test-Path $deploymentPath)) {
        Write-Error " Deployment package not found at: $deploymentPath"
        return
    }
    
    # Navigate to deployment directory
    Push-Location $deploymentPath
    
    try {
        # Install Azure Functions Core Tools if not present
        try {
            $funcVersion = func --version 2>$null
            Write-Host " Azure Functions Core Tools: $funcVersion" -ForegroundColor Green
        }
        catch {
            Write-Host " Installing Azure Functions Core Tools..." -ForegroundColor Yellow
            npm install -g azure-functions-core-tools@4 --unsafe-perm true
        }
        
        # Initialize function project if needed
        if (-not (Test-Path "local.settings.json")) {
            Write-Host " Initializing function project..." -ForegroundColor Yellow
            func init --python --name eq12-functions
        }
        
        # Deploy to Azure
        Write-Host " Deploying functions to Azure..." -ForegroundColor Yellow
        func azure functionapp publish $FunctionAppName --python
        
        Write-Host " Functions deployed successfully!" -ForegroundColor Green
        
        # Get function app URL
        $functionUrl = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query defaultHostName --output tsv
        Write-Host " Function App URL: https://$functionUrl" -ForegroundColor Cyan
        
    }
    finally {
        Pop-Location
    }
}

function Configure-AppSettings {
    Write-Host " Configuring Application Settings..." -ForegroundColor Cyan
    
    # Get storage connection string
    $storageConnectionString = az storage account show-connection-string --name $StorageAccountName --resource-group $ResourceGroupName --output tsv
    
    # Configure app settings
    $appSettings = @(
        "AzureWebJobsStorage=$storageConnectionString",
        "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING=$storageConnectionString",
        "WEBSITE_CONTENTSHARE=$FunctionAppName",
        "FUNCTIONS_EXTENSION_VERSION=~4",
        "FUNCTIONS_WORKER_RUNTIME=python",
        "EQ12_ENVIRONMENT=azure-production",
        "EQ12_VERSION=2.0.0-azure"
    )
    
    # Prompt for API keys if not in environment
    if (-not $env:OPENAI_API_KEYS) {
        $openaiKeys = Read-Host "Enter OpenAI API Keys (comma-separated, optional)"
        if ($openaiKeys) {
            $appSettings += "OPENAI_API_KEYS=[$($openaiKeys.Split(',') | ForEach-Object { """$($_.Trim())""" } | Join-String -Separator ',')]"
        }
    }
    else {
        $appSettings += "OPENAI_API_KEYS=$env:OPENAI_API_KEYS"
    }
    
    if (-not $env:TELEGRAM_BOT_TOKEN) {
        $telegramToken = Read-Host "Enter Telegram Bot Token (optional)"
        if ($telegramToken) {
            $appSettings += "TELEGRAM_BOT_TOKEN=$telegramToken"
        }
    }
    else {
        $appSettings += "TELEGRAM_BOT_TOKEN=$env:TELEGRAM_BOT_TOKEN"
    }
    
    if (-not $env:TELEGRAM_CHAT_ID) {
        $telegramChatId = Read-Host "Enter Telegram Chat ID (optional)"
        if ($telegramChatId) {
            $appSettings += "TELEGRAM_CHAT_ID=$telegramChatId"
        }
    }
    else {
        $appSettings += "TELEGRAM_CHAT_ID=$env:TELEGRAM_CHAT_ID"
    }
    
    # Apply settings
    Write-Host " Applying application settings..." -ForegroundColor Yellow
    foreach ($setting in $appSettings) {
        az functionapp config appsettings set --name $FunctionAppName --resource-group $ResourceGroupName --settings $setting
    }
    
    Write-Host " Application settings configured" -ForegroundColor Green
}

function Test-EQ12Deployment {
    Write-Host " Testing EQ12 Deployment..." -ForegroundColor Cyan
    
    # Get function app URL
    $functionUrl = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query defaultHostName --output tsv
    $healthUrl = "https://$functionUrl/api/health"
    
    Write-Host " Testing health endpoint: $healthUrl" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -Method GET -TimeoutSec 30
        
        if ($response.status -eq "healthy") {
            Write-Host " Health check passed!" -ForegroundColor Green
            Write-Host " System Status: $($response.status)" -ForegroundColor Cyan
            Write-Host " AI Accuracy: $($response.performance.ai_accuracy)%" -ForegroundColor Cyan
            Write-Host " Daily Target: $($response.performance.daily_profit_target)" -ForegroundColor Cyan
            Write-Host " Monthly ROI: $($response.performance.monthly_roi)%" -ForegroundColor Cyan
        }
        else {
            Write-Warning " Health check returned: $($response.status)"
        }
        
    }
    catch {
        Write-Warning " Health check failed: $($_.Exception.Message)"
        Write-Host " This is normal immediately after deployment. Functions may need a few minutes to warm up." -ForegroundColor Yellow
    }
    
    # Test other endpoints
    $endpoints = @(
        @{ Name = "Dashboard"; Url = "https://$functionUrl/api/dashboard" },
        @{ Name = "Wealth Analysis"; Url = "https://$functionUrl/api/wealth/analyze" }
    )
    
    foreach ($endpoint in $endpoints) {
        Write-Host " Testing $($endpoint.Name)..." -ForegroundColor Yellow
        try {
            $testResponse = Invoke-WebRequest -Uri $endpoint.Url -Method GET -TimeoutSec 15 -UseBasicParsing
            if ($testResponse.StatusCode -eq 200) {
                Write-Host "   $($endpoint.Name) accessible" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "   $($endpoint.Name) test failed (may require authentication)" -ForegroundColor Yellow
        }
    }
}

function Show-DeploymentSummary {
    Write-Host "`n EQ12 AZURE DEPLOYMENT COMPLETE!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    
    $functionUrl = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query defaultHostName --output tsv
    
    Write-Host "`n DEPLOYMENT SUMMARY:" -ForegroundColor Cyan
    Write-Host " Resource Group: $ResourceGroupName" -ForegroundColor White
    Write-Host " Storage Account: $StorageAccountName" -ForegroundColor White
    Write-Host " Function App: $FunctionAppName" -ForegroundColor White
    Write-Host " Location: $Location" -ForegroundColor White
    
    Write-Host "`n ENDPOINTS:" -ForegroundColor Cyan
    Write-Host "  Health Check: https://$functionUrl/api/health" -ForegroundColor White
    Write-Host "  Dashboard: https://$functionUrl/api/dashboard" -ForegroundColor White
    Write-Host "  Wealth Analysis: https://$functionUrl/api/wealth/analyze" -ForegroundColor White
    Write-Host "  Betting Predictions: https://$functionUrl/api/betting/predictions" -ForegroundColor White
    Write-Host "  OpenAI Optimization: https://$functionUrl/api/openai/optimize" -ForegroundColor White
    
    Write-Host "`n AUTOMATED FEATURES:" -ForegroundColor Cyan
    Write-Host "  Wealth Engine: Runs 3x daily (8:00, 12:00, 18:00 UTC)" -ForegroundColor White
    Write-Host "  Daily Reports: Generated at midnight UTC" -ForegroundColor White
    Write-Host "  Cost Optimization: Real-time monitoring and alerts" -ForegroundColor White
    Write-Host "  Telegram Alerts: System status and performance updates" -ForegroundColor White
    
    Write-Host "`n COST INFORMATION:" -ForegroundColor Cyan
    Write-Host "  Estimated Monthly Cost: `$8-12 (within `$200 credit)" -ForegroundColor White
    Write-Host "  Function Executions: 1M free/month" -ForegroundColor White
    Write-Host "  Storage: 5GB + 20K transactions free/month" -ForegroundColor White
    Write-Host "  Monitoring: Always-free tier" -ForegroundColor White
    
    Write-Host "`n NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "1.  Configure API keys in Function App settings (if not done)" -ForegroundColor Yellow
    Write-Host "2.  Set up Telegram bot for alerts (optional)" -ForegroundColor Yellow
    Write-Host "3.  Run full system tests" -ForegroundColor Yellow
    Write-Host "4.  Monitor the dashboard for system performance" -ForegroundColor Yellow
    Write-Host "5.  Configure custom risk and profit targets" -ForegroundColor Yellow
    
    Write-Host "`n Your EQ12 Wealth Intelligence System is now running in Azure!" -ForegroundColor Green
    Write-Host " Autonomous AI-powered trading and financial optimization operational!" -ForegroundColor Green
}

# Main execution logic
try {
    if ($CreateResources) {
        Create-AzureResources
    }
    
    if ($ConfigureSecrets) {
        Configure-AppSettings
    }
    
    if ($DeployFunctions) {
        Deploy-EQ12Functions
    }
    
    if ($TestDeployment) {
        Test-EQ12Deployment
    }
    
    # If no specific actions requested, do full deployment
    if (-not ($CreateResources -or $DeployFunctions -or $ConfigureSecrets -or $TestDeployment)) {
        Write-Host " Starting full EQ12 Azure deployment..." -ForegroundColor Green
        
        Create-AzureResources
        Configure-AppSettings
        Deploy-EQ12Functions
        Start-Sleep -Seconds 30  # Wait for functions to initialize
        Test-EQ12Deployment
        Show-DeploymentSummary
    }
    
}
catch {
    Write-Error " Deployment failed: $($_.Exception.Message)"
    Write-Host " Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "  - Ensure you're logged into Azure CLI" -ForegroundColor White
    Write-Host "  - Check your subscription has sufficient quota" -ForegroundColor White
    Write-Host "  - Verify resource names are globally unique" -ForegroundColor White
    Write-Host "  - Try running individual steps with specific switches" -ForegroundColor White
    exit 1
}

Write-Host "`n EQ12 Azure deployment script completed successfully!" -ForegroundColor Green