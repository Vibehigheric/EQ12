<?php
/**
 * EQ12 GODSTACK REST API - Professional Betting Analysis Endpoints
 * 
 * This API serves SGP recommendations, odds data, and integrates with Python algorithms.
 * Follows RESTful principles with proper error handling and authentication.
 * 
 * @package EQ12
 * @version 2.0.0
 * @author EQ12 Platform Team
 */

declare(strict_types=1);

// Load configuration and dependencies
require_once __DIR__ . '/vendor/autoload.php';
require_once __DIR__ . '/intelephense_helper.php';

// CORS Headers for web dashboard
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-API-Key');
header('Content-Type: application/json; charset=utf-8');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

/**
 * EQ12 API Router Class
 */
class EQ12ApiRouter {
    private string $oddsApiKey;
    private array $routes = [];
    private array $middleware = [];
    
    public function __construct() {
        $this->oddsApiKey = $_ENV['ODDS_API_KEY'] ?? 'ODDS_API_KEY_PLACEHOLDER';
        $this->setupRoutes();
        $this->setupMiddleware();
    }
    
    /**
     * Setup API routes
     */
    private function setupRoutes(): void {
        // Health check
        $this->routes['GET']['/api/health'] = [$this, 'healthCheck'];
        
        // Odds endpoints
        $this->routes['GET']['/api/odds/sports'] = [$this, 'getSports'];
        $this->routes['GET']['/api/odds/{sport}'] = [$this, 'getOddsBySport'];
        $this->routes['GET']['/api/odds/live/{sport}'] = [$this, 'getLiveOdds'];
        
        // SGP endpoints
        $this->routes['GET']['/api/sgp/recommendations'] = [$this, 'getSgpRecommendations'];
        $this->routes['POST']['/api/sgp/build'] = [$this, 'buildSgp'];
        $this->routes['POST']['/api/sgp/optimize'] = [$this, 'optimizeSgp'];
        $this->routes['GET']['/api/sgp/nhl/tonight'] = [$this, 'getNhlSgpTonight'];
        
        // Analysis endpoints
        $this->routes['POST']['/api/analysis/kelly'] = [$this, 'calculateKelly'];
        $this->routes['GET']['/api/analysis/market'] = [$this, 'getMarketAnalysis'];
        $this->routes['GET']['/api/analysis/risk/{sport}'] = [$this, 'getRiskAnalysis'];
        
        // Python integration endpoints
        $this->routes['POST']['/api/python/execute'] = [$this, 'executePythonScript'];
        $this->routes['GET']['/api/python/results/{job_id}'] = [$this, 'getPythonResults'];
        
        // Cache management
        $this->routes['DELETE']['/api/cache/clear'] = [$this, 'clearCache'];
        $this->routes['GET']['/api/cache/stats'] = [$this, 'getCacheStats'];
    }
    
    /**
     * Setup middleware
     */
    private function setupMiddleware(): void {
        $this->middleware[] = [$this, 'authenticationMiddleware'];
        $this->middleware[] = [$this, 'rateLimitMiddleware'];
        $this->middleware[] = [$this, 'loggingMiddleware'];
    }
    
    /**
     * Route incoming requests
     */
    public function route(): void {
        try {
            $method = $_SERVER['REQUEST_METHOD'];
            $path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
            
            // Apply middleware
            foreach ($this->middleware as $middleware) {
                $result = call_user_func($middleware, $method, $path);
                if ($result !== true) {
                    $this->sendResponse($result, 403);
                    return;
                }
            }
            
            // Find matching route
            $handler = $this->findRoute($method, $path);
            if ($handler === null) {
                $this->sendResponse(['error' => 'Endpoint not found', 'path' => $path], 404);
                return;
            }
            
            // Execute handler
            $response = call_user_func($handler['callback'], $handler['params']);
            $this->sendResponse($response);
            
        } catch (Exception $e) {
            $this->logError('API Error', $e);
            $this->sendResponse([
                'error' => 'Internal server error',
                'message' => $e->getMessage(),
                'timestamp' => date('c')
            ], 500);
        }
    }
    
    /**
     * Find route handler
     */
    private function findRoute(string $method, string $path): ?array {
        if (!isset($this->routes[$method])) {
            return null;
        }
        
        foreach ($this->routes[$method] as $route => $callback) {
            $params = [];
            $pattern = preg_replace('/\{([^}]+)\}/', '([^/]+)', $route);
            $pattern = '#^' . $pattern . '$#';
            
            if (preg_match($pattern, $path, $matches)) {
                array_shift($matches); // Remove full match
                
                // Extract parameter names
                preg_match_all('/\{([^}]+)\}/', $route, $paramNames);
                foreach ($paramNames[1] as $index => $paramName) {
                    $params[$paramName] = $matches[$index] ?? null;
                }
                
                return ['callback' => $callback, 'params' => $params];
            }
        }
        
        return null;
    }
    
    // ========== MIDDLEWARE ==========
    
    /**
     * Authentication middleware
     */
    private function authenticationMiddleware(string $method, string $path): bool {
        // Skip auth for health check
        if ($path === '/api/health') {
            return true;
        }
        
        $apiKey = $_SERVER['HTTP_X_API_KEY'] ?? $_GET['api_key'] ?? null;
        
        if (!$apiKey) {
            return ['error' => 'API key required', 'code' => 'MISSING_API_KEY'];
        }
        
        if (!$this->validateApiKey($apiKey)) {
            return ['error' => 'Invalid API key', 'code' => 'INVALID_API_KEY'];
        }
        
        return true;
    }
    
    /**
     * Rate limiting middleware
     */
    private function rateLimitMiddleware(string $method, string $path): bool {
        $clientIp = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
        $rateLimitKey = "rate_limit:{$clientIp}";
        
        // Simple file-based rate limiting (60 requests per minute)
        $rateLimitFile = sys_get_temp_dir() . '/' . md5($rateLimitKey) . '.txt';
        $now = time();
        $requests = [];
        
        if (file_exists($rateLimitFile)) {
            $data = json_decode(file_get_contents($rateLimitFile), true);
            $requests = array_filter($data['requests'] ?? [], fn($time) => $now - $time < 60);
        }
        
        if (count($requests) >= 60) {
            return ['error' => 'Rate limit exceeded', 'code' => 'RATE_LIMIT_EXCEEDED'];
        }
        
        $requests[] = $now;
        file_put_contents($rateLimitFile, json_encode(['requests' => $requests]));
        
        return true;
    }
    
    /**
     * Logging middleware
     */
    private function loggingMiddleware(string $method, string $path): bool {
        $this->logApiRequest($method, $path);
        return true;
    }
    
    // ========== API ENDPOINTS ==========
    
    /**
     * Health check endpoint
     */
    public function healthCheck(): array {
        return [
            'status' => 'healthy',
            'timestamp' => date('c'),
            'version' => '2.0.0',
            'system' => [
                'php_version' => PHP_VERSION,
                'memory_usage' => memory_get_usage(true),
                'odds_api_status' => $this->testOddsApiConnection()
            ]
        ];
    }
    
    /**
     * Get available sports
     */
    public function getSports(): array {
        $cacheKey = 'sports_list';
        $cached = $this->getFromCache($cacheKey);
        
        if ($cached !== null) {
            return ['data' => $cached, 'source' => 'cache'];
        }
        
        $url = "https://api.the-odds-api.com/v4/sports?apiKey={$this->oddsApiKey}";
        $response = $this->makeHttpRequest($url);
        
        if ($response === null) {
            return ['error' => 'Failed to fetch sports data'];
        }
        
        $this->setCache($cacheKey, $response, 3600); // Cache for 1 hour
        
        return ['data' => $response, 'source' => 'live'];
    }
    
    /**
     * Get odds by sport
     */
    public function getOddsBySport(array $params): array {
        $sport = $params['sport'] ?? 'icehockey_nhl';
        $region = $_GET['region'] ?? 'us';
        $markets = $_GET['markets'] ?? 'h2h';
        
        $cacheKey = "odds_{$sport}_{$region}_{$markets}";
        $cached = $this->getFromCache($cacheKey);
        
        if ($cached !== null) {
            return ['data' => $cached, 'source' => 'cache'];
        }
        
        $url = "https://api.the-odds-api.com/v4/sports/{$sport}/odds?" . http_build_query([
            'apiKey' => $this->oddsApiKey,
            'regions' => $region,
            'markets' => $markets,
            'oddsFormat' => 'decimal'
        ]);
        
        $response = $this->makeHttpRequest($url);
        
        if ($response === null) {
            return ['error' => 'Failed to fetch odds data'];
        }
        
        $this->setCache($cacheKey, $response, 300); // Cache for 5 minutes
        
        return ['data' => $response, 'source' => 'live'];
    }
    
    /**
     * Get live odds with real-time updates
     */
    public function getLiveOdds(array $params): array {
        $sport = $params['sport'] ?? 'icehockey_nhl';
        
        // Always fetch fresh for live odds
        $url = "https://api.the-odds-api.com/v4/sports/{$sport}/odds?" . http_build_query([
            'apiKey' => $this->oddsApiKey,
            'regions' => 'us',
            'markets' => 'h2h,spreads,totals',
            'oddsFormat' => 'decimal'
        ]);
        
        $response = $this->makeHttpRequest($url);
        
        if ($response === null) {
            return ['error' => 'Failed to fetch live odds'];
        }
        
        return [
            'data' => $response,
            'source' => 'live',
            'timestamp' => date('c'),
            'refresh_rate' => '30s'
        ];
    }
    
    /**
     * Get SGP recommendations
     */
    public function getSgpRecommendations(): array {
        $sport = $_GET['sport'] ?? 'icehockey_nhl';
        $minRoi = (float)($_GET['min_roi'] ?? 10.0);
        $maxRisk = $_GET['max_risk'] ?? 'medium';
        
        // Execute Python SGP builder
        $pythonScript = 'eq12_nhl_sgp_builder.py';
        $result = $this->executePythonCommand($pythonScript, [
            '--sport' => $sport,
            '--min-roi' => $minRoi,
            '--output-format' => 'json'
        ]);
        
        if ($result['success']) {
            $recommendations = json_decode($result['output'], true);
            
            return [
                'data' => $recommendations,
                'filters' => [
                    'sport' => $sport,
                    'min_roi' => $minRoi,
                    'max_risk' => $maxRisk
                ],
                'generated_at' => date('c')
            ];
        }
        
        return ['error' => 'Failed to generate SGP recommendations', 'details' => $result['error']];
    }
    
    /**
     * Build custom SGP
     */
    public function buildSgp(): array {
        $input = json_decode(file_get_contents('php://input'), true);
        
        $gameId = $input['game_id'] ?? null;
        $selections = $input['selections'] ?? [];
        $stake = (float)($input['stake'] ?? 8.0);
        
        if (!$gameId || empty($selections)) {
            return ['error' => 'Game ID and selections required'];
        }
        
        // Execute Python SGP builder with specific selections
        $pythonScript = 'eq12_sgp_calculator.py';
        $result = $this->executePythonCommand($pythonScript, [
            '--game-id' => $gameId,
            '--selections' => json_encode($selections),
            '--stake' => $stake,
            '--output-format' => 'json'
        ]);
        
        if ($result['success']) {
            $sgpData = json_decode($result['output'], true);
            
            return [
                'sgp' => $sgpData,
                'recommendations' => [
                    'confidence' => $sgpData['confidence'] ?? 'medium',
                    'kelly_fraction' => $sgpData['kelly_fraction'] ?? 0.0,
                    'expected_value' => $sgpData['expected_value'] ?? 0.0
                ],
                'created_at' => date('c')
            ];
        }
        
        return ['error' => 'Failed to build SGP', 'details' => $result['error']];
    }
    
    /**
     * Optimize SGP by removing lowest confidence legs
     */
    public function optimizeSgp(): array {
        $input = json_decode(file_get_contents('php://input'), true);
        
        $sgpLegs = $input['legs'] ?? [];
        $targetConfidence = (float)($input['target_confidence'] ?? 0.8);
        
        if (empty($sgpLegs)) {
            return ['error' => 'SGP legs required for optimization'];
        }
        
        // Execute Python optimization script
        $pythonScript = 'eq12_sgp_optimizer.py';
        $result = $this->executePythonCommand($pythonScript, [
            '--legs' => json_encode($sgpLegs),
            '--target-confidence' => $targetConfidence,
            '--output-format' => 'json'
        ]);
        
        if ($result['success']) {
            $optimizedData = json_decode($result['output'], true);
            
            return [
                'original_legs' => count($sgpLegs),
                'optimized_legs' => count($optimizedData['legs'] ?? []),
                'removed_legs' => $optimizedData['removed_legs'] ?? [],
                'improved_probability' => $optimizedData['improved_probability'] ?? 0.0,
                'optimization_summary' => $optimizedData,
                'optimized_at' => date('c')
            ];
        }
        
        return ['error' => 'Failed to optimize SGP', 'details' => $result['error']];
    }
    
    /**
     * Get NHL SGP recommendations for tonight
     */
    public function getNhlSgpTonight(): array {
        // Execute the existing NHL SGP builder
        $pythonScript = 'eq12_nhl_sgp_builder.py';
        $result = $this->executePythonCommand($pythonScript, [
            '--today-only' => true,
            '--min-confidence' => 0.7,
            '--output-format' => 'json'
        ]);
        
        if ($result['success']) {
            $nhlData = json_decode($result['output'], true);
            
            return [
                'games_analyzed' => $nhlData['games_count'] ?? 0,
                'sgp_recommendations' => $nhlData['recommendations'] ?? [],
                'stacked_options' => $nhlData['stacked_sgps'] ?? [],
                'best_roi' => $nhlData['best_roi'] ?? 0.0,
                'analysis_timestamp' => date('c')
            ];
        }
        
        return ['error' => 'Failed to analyze NHL games', 'details' => $result['error']];
    }
    
    /**
     * Calculate Kelly criterion
     */
    public function calculateKelly(): array {
        $input = json_decode(file_get_contents('php://input'), true);
        
        $probability = (float)($input['probability'] ?? 0.0);
        $odds = (float)($input['odds'] ?? 0.0);
        $bankroll = (float)($input['bankroll'] ?? 1000.0);
        $maxKelly = (float)($input['max_kelly'] ?? 0.25);
        
        if ($probability <= 0 || $probability >= 1 || $odds <= 1) {
            return ['error' => 'Invalid probability or odds values'];
        }
        
        // Kelly formula: f = (bp - q) / b
        $b = $odds - 1;
        $q = 1 - $probability;
        $kellyFraction = ($b * $probability - $q) / $b;
        $clampedKelly = min($kellyFraction, $maxKelly);
        $recommendedStake = $bankroll * max($clampedKelly, 0);
        $expectedValue = ($probability * ($odds - 1) - (1 - $probability)) * $recommendedStake;
        
        return [
            'kelly_fraction' => $kellyFraction,
            'clamped_kelly' => $clampedKelly,
            'recommended_stake' => $recommendedStake,
            'expected_value' => $expectedValue,
            'bankroll_percentage' => ($recommendedStake / $bankroll) * 100,
            'calculation_params' => [
                'probability' => $probability,
                'odds' => $odds,
                'bankroll' => $bankroll,
                'max_kelly' => $maxKelly
            ]
        ];
    }
    
    /**
     * Get market analysis
     */
    public function getMarketAnalysis(): array {
        $sport = $_GET['sport'] ?? 'all';
        $timeframe = $_GET['timeframe'] ?? '24h';
        
        // Execute Python market analysis
        $pythonScript = 'eq12_market_analyzer.py';
        $result = $this->executePythonCommand($pythonScript, [
            '--sport' => $sport,
            '--timeframe' => $timeframe,
            '--output-format' => 'json'
        ]);
        
        if ($result['success']) {
            $analysisData = json_decode($result['output'], true);
            
            return [
                'market_efficiency' => $analysisData['efficiency'] ?? 0.0,
                'volatility_index' => $analysisData['volatility'] ?? 0.0,
                'arbitrage_opportunities' => $analysisData['arbitrage'] ?? [],
                'trend_analysis' => $analysisData['trends'] ?? [],
                'analysis_period' => $timeframe,
                'generated_at' => date('c')
            ];
        }
        
        return ['error' => 'Failed to analyze market', 'details' => $result['error']];
    }
    
    /**
     * Get risk analysis for sport
     */
    public function getRiskAnalysis(array $params): array {
        $sport = $params['sport'] ?? 'icehockey_nhl';
        $portfolioSize = (float)($_GET['portfolio_size'] ?? 1000.0);
        
        // Execute Python risk analysis
        $pythonScript = 'eq12_risk_analyzer.py';
        $result = $this->executePythonCommand($pythonScript, [
            '--sport' => $sport,
            '--portfolio-size' => $portfolioSize,
            '--output-format' => 'json'
        ]);
        
        if ($result['success']) {
            $riskData = json_decode($result['output'], true);
            
            return [
                'risk_score' => $riskData['risk_score'] ?? 0.0,
                'var_95' => $riskData['var_95'] ?? 0.0, // Value at Risk
                'max_drawdown' => $riskData['max_drawdown'] ?? 0.0,
                'correlation_risks' => $riskData['correlations'] ?? [],
                'recommendations' => $riskData['recommendations'] ?? [],
                'analysis_date' => date('c')
            ];
        }
        
        return ['error' => 'Failed to analyze risk', 'details' => $result['error']];
    }
    
    /**
     * Execute Python script
     */
    public function executePythonScript(): array {
        $input = json_decode(file_get_contents('php://input'), true);
        
        $script = $input['script'] ?? null;
        $args = $input['args'] ?? [];
        $async = $input['async'] ?? false;
        
        if (!$script) {
            return ['error' => 'Script name required'];
        }
        
        // Validate script exists and is safe to execute
        $allowedScripts = [
            'eq12_nhl_sgp_builder.py',
            'eq12_sgp_calculator.py',
            'eq12_sgp_optimizer.py',
            'eq12_market_analyzer.py',
            'eq12_risk_analyzer.py'
        ];
        
        if (!in_array($script, $allowedScripts)) {
            return ['error' => 'Script not allowed', 'allowed_scripts' => $allowedScripts];
        }
        
        if ($async) {
            $jobId = uniqid('job_');
            $this->executeAsyncPythonScript($script, $args, $jobId);
            return ['job_id' => $jobId, 'status' => 'started'];
        } else {
            $result = $this->executePythonCommand($script, $args);
            return $result;
        }
    }
    
    /**
     * Get Python execution results
     */
    public function getPythonResults(array $params): array {
        $jobId = $params['job_id'] ?? null;
        
        if (!$jobId) {
            return ['error' => 'Job ID required'];
        }
        
        $resultFile = sys_get_temp_dir() . "/eq12_job_{$jobId}.json";
        
        if (!file_exists($resultFile)) {
            return ['error' => 'Job not found or expired'];
        }
        
        $result = json_decode(file_get_contents($resultFile), true);
        
        // Clean up completed job files
        if (($result['status'] ?? null) === 'completed') {
            unlink($resultFile);
        }
        
        return $result;
    }
    
    /**
     * Clear cache
     */
    public function clearCache(): array {
        $pattern = sys_get_temp_dir() . '/eq12_cache_*.json';
        $files = glob($pattern);
        $cleared = 0;
        
        foreach ($files as $file) {
            if (unlink($file)) {
                $cleared++;
            }
        }
        
        return [
            'message' => 'Cache cleared successfully',
            'files_cleared' => $cleared
        ];
    }
    
    /**
     * Get cache statistics
     */
    public function getCacheStats(): array {
        $pattern = sys_get_temp_dir() . '/eq12_cache_*.json';
        $files = glob($pattern);
        
        $stats = [
            'total_entries' => count($files),
            'total_size' => 0,
            'entries' => []
        ];
        
        foreach ($files as $file) {
            $size = filesize($file);
            $stats['total_size'] += $size;
            $stats['entries'][] = [
                'key' => basename($file, '.json'),
                'size' => $size,
                'created' => filemtime($file)
            ];
        }
        
        return $stats;
    }
    
    // ========== UTILITY METHODS ==========
    
    /**
     * Execute Python command
     */
    private function executePythonCommand(string $script, array $args = []): array {
        $scriptPath = __DIR__ . '/' . $script;
        
        if (!file_exists($scriptPath)) {
            return ['success' => false, 'error' => "Script not found: {$script}"];
        }
        
        // Build command
        $pythonPath = 'C:/EQ12/.venv/Scripts/python.exe';
        $command = escapeshellarg($pythonPath) . ' ' . escapeshellarg($scriptPath);
        
        foreach ($args as $key => $value) {
            $command .= ' ' . escapeshellarg($key) . ' ' . escapeshellarg($value);
        }
        
        // Execute command
        $output = [];
        $returnCode = 0;
        exec($command . ' 2>&1', $output, $returnCode);
        
        return [
            'success' => $returnCode === 0,
            'output' => implode("\n", $output),
            'error' => $returnCode !== 0 ? implode("\n", $output) : null,
            'command' => $command
        ];
    }
    
    /**
     * Execute Python script asynchronously
     */
    private function executeAsyncPythonScript(string $script, array $args, string $jobId): void {
        $resultFile = sys_get_temp_dir() . "/eq12_job_{$jobId}.json";
        file_put_contents($resultFile, json_encode(['status' => 'running', 'started_at' => date('c')]));
        
        // Execute in background (Windows compatible)
        $pythonPath = 'C:/EQ12/.venv/Scripts/python.exe';
        $scriptPath = __DIR__ . '/' . $script;
        $command = "start /B \"{$pythonPath}\" \"{$scriptPath}\"";
        
        foreach ($args as $key => $value) {
            $command .= ' ' . escapeshellarg($key) . ' ' . escapeshellarg($value);
        }
        
        $command .= " > \"{$resultFile}.output\" 2>&1";
        
        pclose(popen($command, 'r'));
    }
    
    /**
     * Make HTTP request
     */
    private function makeHttpRequest(string $url): ?array {
        $context = stream_context_create([
            'http' => [
                'timeout' => 10,
                'user_agent' => 'EQ12-API/2.0'
            ]
        ]);
        
        $response = @file_get_contents($url, false, $context);
        
        if ($response === false) {
            return null;
        }
        
        return json_decode($response, true);
    }
    
    /**
     * Validate API key
     */
    private function validateApiKey(string $apiKey): bool {
        // Simple validation - you can enhance this
        return strlen($apiKey) >= 32 && preg_match('/^[a-f0-9]+$/', $apiKey);
    }
    
    /**
     * Test odds API connection
     */
    private function testOddsApiConnection(): string {
        $url = "https://api.the-odds-api.com/v4/sports?apiKey={$this->oddsApiKey}";
        $response = $this->makeHttpRequest($url);
        
        return $response !== null ? 'connected' : 'error';
    }
    
    /**
     * Cache management
     */
    private function getFromCache(string $key): ?array {
        $cacheFile = sys_get_temp_dir() . "/eq12_cache_{$key}.json";
        
        if (!file_exists($cacheFile)) {
            return null;
        }
        
        $data = json_decode(file_get_contents($cacheFile), true);
        
        if ($data['expires'] < time()) {
            unlink($cacheFile);
            return null;
        }
        
        return $data['value'];
    }
    
    private function setCache(string $key, array $value, int $ttl): void {
        $cacheFile = sys_get_temp_dir() . "/eq12_cache_{$key}.json";
        $data = [
            'value' => $value,
            'expires' => time() + $ttl,
            'created' => time()
        ];
        
        file_put_contents($cacheFile, json_encode($data));
    }
    
    /**
     * Send JSON response
     */
    private function sendResponse(array $data, int $statusCode = 200): void {
        http_response_code($statusCode);
        echo json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    }
    
    /**
     * Log API request
     */
    private function logApiRequest(string $method, string $path): void {
        $logData = [
            'timestamp' => date('c'),
            'method' => $method,
            'path' => $path,
            'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown',
            'user_agent' => $_SERVER['HTTP_USER_AGENT'] ?? 'unknown'
        ];
        
        $logFile = __DIR__ . '/logs/api_requests.log';
        file_put_contents($logFile, json_encode($logData) . "\n", FILE_APPEND | LOCK_EX);
    }
    
    /**
     * Log error
     */
    private function logError(string $message, Exception $e): void {
        $logData = [
            'timestamp' => date('c'),
            'message' => $message,
            'error' => $e->getMessage(),
            'file' => $e->getFile(),
            'line' => $e->getLine(),
            'trace' => $e->getTraceAsString()
        ];
        
        $logFile = __DIR__ . '/logs/api_errors.log';
        file_put_contents($logFile, json_encode($logData) . "\n", FILE_APPEND | LOCK_EX);
    }
}

// Initialize and route
try {
    $router = new EQ12ApiRouter();
    $router->route();
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Fatal server error',
        'message' => $e->getMessage(),
        'timestamp' => date('c')
    ]);
}