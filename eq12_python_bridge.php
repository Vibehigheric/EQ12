<?php

/**
 * EQ12 PHP-Python Integration Bridge
 * 
 * Seamlessly integrates PHP web interface with Python betting algorithms.
 * Provides type-safe execution of Python scripts with proper error handling.
 * 
 * @package EQ12
 * @version 2.0.0
 * @author EQ12 Platform Team
 */

declare(strict_types=1);

require_once __DIR__ . '/intelephense_helper.php';

/**
 * EQ12 Python Integration Manager
 */
class EQ12PythonIntegration
{
    private string $pythonPath;
    private string $scriptsPath;
    private string $venvPath;
    private array $environmentVars;

    public function __construct()
    {
        $this->pythonPath = 'C:/EQ12/.venv/Scripts/python.exe';
        $this->scriptsPath = __DIR__ . '/';
        $this->venvPath = 'C:/EQ12/.venv';
        $this->environmentVars = [
            'ODDS_API_KEY' => $_ENV['ODDS_API_KEY'] ?? '8eb822610b7753d45f76dcac8230a7d1',
            'PYTHONPATH' => __DIR__,
            'PYTHONUNBUFFERED' => '1'
        ];
    }

    /**
     * Execute NHL SGP Builder
     * 
     * @param array{min_roi?: float, target_games?: array<string>, stake?: float} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function executeNhlSgpBuilder(array $options = []): array
    {
        $args = [
            '--output-format' => 'json',
            '--verbose' => true
        ];

        if (isset($options['min_roi'])) {
            $args['--min-roi'] = (string)$options['min_roi'];
        }

        if (isset($options['target_games'])) {
            $args['--target-games'] = json_encode($options['target_games']);
        }

        if (isset($options['stake'])) {
            $args['--stake'] = (string)$options['stake'];
        }

        return $this->executePythonScript('eq12_nhl_sgp_builder.py', $args);
    }

    /**
     * Execute Stacked NHL SGP Builder
     * 
     * @param array{games: array<string>, max_legs?: int, min_confidence?: float} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function executeStackedSgpBuilder(array $options): array
    {
        if (!isset($options['games']) || empty($options['games'])) {
            return ['success' => false, 'error' => 'Games array required'];
        }

        $args = [
            '--games' => json_encode($options['games']),
            '--output-format' => 'json',
            '--verbose' => true
        ];

        if (isset($options['max_legs'])) {
            $args['--max-legs'] = (string)$options['max_legs'];
        }

        if (isset($options['min_confidence'])) {
            $args['--min-confidence'] = (string)$options['min_confidence'];
        }

        return $this->executePythonScript('eq12_stacked_nhl_sgp.py', $args);
    }

    /**
     * Execute SGP Optimizer (remove lowest confidence legs)
     * 
     * @param array{sgp_data: array, optimization_target?: string} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function optimizeSgp(array $options): array
    {
        if (!isset($options['sgp_data'])) {
            return ['success' => false, 'error' => 'SGP data required for optimization'];
        }

        // Create temporary file for SGP data
        $tempFile = tempnam(sys_get_temp_dir(), 'eq12_sgp_');
        file_put_contents($tempFile, json_encode($options['sgp_data']));

        $args = [
            '--sgp-file' => $tempFile,
            '--output-format' => 'json',
            '--optimize-method' => $options['optimization_target'] ?? 'confidence'
        ];

        $result = $this->executePythonScript('eq12_sgp_optimizer.py', $args);

        // Clean up temp file
        unlink($tempFile);

        return $result;
    }

    /**
     * Execute Market Analysis
     * 
     * @param array{sport?: string, timeframe?: string, analysis_type?: string} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function executeMarketAnalysis(array $options = []): array
    {
        $args = [
            '--sport' => $options['sport'] ?? 'all',
            '--timeframe' => $options['timeframe'] ?? '24h',
            '--analysis-type' => $options['analysis_type'] ?? 'full',
            '--output-format' => 'json'
        ];

        return $this->executePythonScript('eq12_market_analyzer.py', $args);
    }

    /**
     * Execute Risk Analysis
     * 
     * @param array{portfolio?: array, bankroll?: float, risk_level?: string} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function executeRiskAnalysis(array $options = []): array
    {
        $args = [
            '--bankroll' => (string)($options['bankroll'] ?? 1000.0),
            '--risk-level' => $options['risk_level'] ?? 'medium',
            '--output-format' => 'json'
        ];

        if (isset($options['portfolio'])) {
            $tempFile = tempnam(sys_get_temp_dir(), 'eq12_portfolio_');
            file_put_contents($tempFile, json_encode($options['portfolio']));
            $args['--portfolio-file'] = $tempFile;
        }

        $result = $this->executePythonScript('eq12_risk_analyzer.py', $args);

        // Clean up temp file if created
        if (isset($tempFile)) {
            unlink($tempFile);
        }

        return $result;
    }

    /**
     * Execute Kelly Criterion Calculator
     * 
     * @param array{probability: float, odds: float, bankroll: float, max_kelly?: float} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function calculateKellyCriterion(array $options): array
    {
        $required = ['probability', 'odds', 'bankroll'];
        foreach ($required as $field) {
            if (!isset($options[$field])) {
                return ['success' => false, 'error' => "Required field missing: {$field}"];
            }
        }

        $args = [
            '--probability' => (string)$options['probability'],
            '--odds' => (string)$options['odds'],
            '--bankroll' => (string)$options['bankroll'],
            '--max-kelly' => (string)($options['max_kelly'] ?? 0.25),
            '--output-format' => 'json'
        ];

        return $this->executePythonScript('eq12_kelly_calculator.py', $args);
    }

    /**
     * Execute Live Odds Fetcher
     * 
     * @param array{sport: string, markets?: array<string>, bookmakers?: array<string>} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function fetchLiveOdds(array $options): array
    {
        if (!isset($options['sport'])) {
            return ['success' => false, 'error' => 'Sport parameter required'];
        }

        $args = [
            '--sport' => $options['sport'],
            '--output-format' => 'json',
            '--live-mode' => true
        ];

        if (isset($options['markets'])) {
            $args['--markets'] = implode(',', $options['markets']);
        }

        if (isset($options['bookmakers'])) {
            $args['--bookmakers'] = implode(',', $options['bookmakers']);
        }

        return $this->executePythonScript('eq12_odds_fetcher.py', $args);
    }

    /**
     * Execute Arbitrage Finder
     * 
     * @param array{sport?: string, min_profit?: float, max_stake?: float} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function findArbitrageOpportunities(array $options = []): array
    {
        $args = [
            '--sport' => $options['sport'] ?? 'all',
            '--min-profit' => (string)($options['min_profit'] ?? 2.0),
            '--max-stake' => (string)($options['max_stake'] ?? 500.0),
            '--output-format' => 'json'
        ];

        return $this->executePythonScript('eq12_arbitrage_finder.py', $args);
    }

    /**
     * Execute Correlation Analysis
     * 
     * @param array{games: array<string>, analysis_depth?: string} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function analyzeCorrelations(array $options): array
    {
        if (!isset($options['games']) || empty($options['games'])) {
            return ['success' => false, 'error' => 'Games array required'];
        }

        $args = [
            '--games' => json_encode($options['games']),
            '--analysis-depth' => $options['analysis_depth'] ?? 'standard',
            '--output-format' => 'json'
        ];

        return $this->executePythonScript('eq12_correlation_analyzer.py', $args);
    }

    /**
     * Execute Portfolio Optimization
     * 
     * @param array{bets: array, optimization_method?: string, constraints?: array} $options
     * @return array{success: bool, data?: array, error?: string}
     */
    public function optimizePortfolio(array $options): array
    {
        if (!isset($options['bets']) || empty($options['bets'])) {
            return ['success' => false, 'error' => 'Bets array required'];
        }

        $tempFile = tempnam(sys_get_temp_dir(), 'eq12_portfolio_');
        file_put_contents($tempFile, json_encode($options['bets']));

        $args = [
            '--bets-file' => $tempFile,
            '--optimization-method' => $options['optimization_method'] ?? 'kelly',
            '--output-format' => 'json'
        ];

        if (isset($options['constraints'])) {
            $constraintsFile = tempnam(sys_get_temp_dir(), 'eq12_constraints_');
            file_put_contents($constraintsFile, json_encode($options['constraints']));
            $args['--constraints-file'] = $constraintsFile;
        }

        $result = $this->executePythonScript('eq12_portfolio_optimizer.py', $args);

        // Clean up temp files
        unlink($tempFile);
        if (isset($constraintsFile)) {
            unlink($constraintsFile);
        }

        return $result;
    }

    /**
     * Execute custom Python script with validation
     * 
     * @param string $scriptName Name of Python script (must be whitelisted)
     * @param array<string, mixed> $args Script arguments
     * @return array{success: bool, data?: array, error?: string, execution_time?: float}
     */
    private function executePythonScript(string $scriptName, array $args = []): array
    {
        $startTime = microtime(true);

        // Validate script is allowed
        if (!$this->isScriptAllowed($scriptName)) {
            return [
                'success' => false,
                'error' => "Script not allowed: {$scriptName}",
                'allowed_scripts' => $this->getAllowedScripts()
            ];
        }

        $scriptPath = $this->scriptsPath . $scriptName;

        if (!file_exists($scriptPath)) {
            return ['success' => false, 'error' => "Script not found: {$scriptPath}"];
        }

        // Build command
        $command = $this->buildPythonCommand($scriptPath, $args);

        // Execute with proper environment
        $result = $this->executeCommand($command);

        $executionTime = microtime(true) - $startTime;

        if ($result['success'] && !empty($result['output'])) {
            // Try to decode JSON output
            $decodedOutput = json_decode($result['output'], true);
            if (json_last_error() === JSON_ERROR_NONE) {
                $result['data'] = $decodedOutput;
                unset($result['output']); // Remove raw output if JSON parsing successful
            }
        }

        $result['execution_time'] = $executionTime;
        $result['script'] = $scriptName;

        // Log execution
        $this->logExecution($scriptName, $args, $result, $executionTime);

        return $result;
    }

    /**
     * Build Python command with proper escaping and environment
     */
    private function buildPythonCommand(string $scriptPath, array $args): string
    {
        $command = escapeshellarg($this->pythonPath) . ' ' . escapeshellarg($scriptPath);

        foreach ($args as $key => $value) {
            if (is_bool($value)) {
                if ($value) {
                    $command .= ' ' . escapeshellarg($key);
                }
            } else {
                $command .= ' ' . escapeshellarg($key) . ' ' . escapeshellarg((string)$value);
            }
        }

        return $command;
    }

    /**
     * Execute command with proper error handling
     */
    private function executeCommand(string $command): array
    {
        // Set environment variables
        $env = array_merge($_ENV, $this->environmentVars);

        $descriptorSpec = [
            0 => ['pipe', 'r'],  // stdin
            1 => ['pipe', 'w'],  // stdout
            2 => ['pipe', 'w']   // stderr
        ];

        $process = proc_open($command, $descriptorSpec, $pipes, $this->scriptsPath, $env);

        if (!is_resource($process)) {
            return ['success' => false, 'error' => 'Failed to start process'];
        }

        // Close stdin
        fclose($pipes[0]);

        // Read outputs
        $stdout = stream_get_contents($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);

        fclose($pipes[1]);
        fclose($pipes[2]);

        $returnCode = proc_close($process);

        return [
            'success' => $returnCode === 0,
            'output' => $stdout,
            'error' => $returnCode !== 0 ? $stderr : null,
            'return_code' => $returnCode,
            'command' => $command
        ];
    }

    /**
     * Check if script is allowed to be executed
     */
    private function isScriptAllowed(string $scriptName): bool
    {
        return in_array($scriptName, $this->getAllowedScripts(), true);
    }

    /**
     * Get list of allowed Python scripts
     */
    private function getAllowedScripts(): array
    {
        return [
            'eq12_nhl_sgp_builder.py',
            'eq12_stacked_nhl_sgp.py',
            'eq12_sgp_optimizer.py',
            'eq12_market_analyzer.py',
            'eq12_risk_analyzer.py',
            'eq12_kelly_calculator.py',
            'eq12_odds_fetcher.py',
            'eq12_arbitrage_finder.py',
            'eq12_correlation_analyzer.py',
            'eq12_portfolio_optimizer.py'
        ];
    }

    /**
     * Log Python script execution
     */
    private function logExecution(string $script, array $args, array $result, float $executionTime): void
    {
        $logData = [
            'timestamp' => date('c'),
            'script' => $script,
            'args' => $args,
            'success' => $result['success'],
            'execution_time' => $executionTime,
            'return_code' => $result['return_code'] ?? null,
            'error' => $result['error'] ?? null
        ];

        $logFile = __DIR__ . '/logs/python_executions.log';

        // Ensure logs directory exists
        $logDir = dirname($logFile);
        if (!is_dir($logDir)) {
            mkdir($logDir, 0755, true);
        }

        file_put_contents($logFile, json_encode($logData) . "\n", FILE_APPEND | LOCK_EX);
    }

    /**
     * Get execution statistics
     */
    public function getExecutionStats(): array
    {
        $logFile = __DIR__ . '/logs/python_executions.log';

        if (!file_exists($logFile)) {
            return ['total_executions' => 0, 'recent_executions' => []];
        }

        $lines = file($logFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        $executions = array_map('json_decode', array_slice($lines, -100), array_fill(0, 100, true));

        $stats = [
            'total_executions' => count($lines),
            'recent_executions' => array_slice($executions, -10),
            'success_rate' => 0.0,
            'average_execution_time' => 0.0,
            'most_used_scripts' => []
        ];

        if (!empty($executions)) {
            $successful = array_filter($executions, fn($exec) => $exec['success'] ?? false);
            $stats['success_rate'] = count($successful) / count($executions) * 100;

            $executionTimes = array_column($executions, 'execution_time');
            $stats['average_execution_time'] = array_sum($executionTimes) / count($executionTimes);

            $scriptCounts = array_count_values(array_column($executions, 'script'));
            arsort($scriptCounts);
            $stats['most_used_scripts'] = array_slice($scriptCounts, 0, 5, true);
        }

        return $stats;
    }
}

/**
 * EQ12 Python Script Factory
 * 
 * Provides convenient factory methods for creating and executing common Python operations
 */
class EQ12PythonFactory
{
    private EQ12PythonIntegration $integration;

    public function __construct()
    {
        $this->integration = new EQ12PythonIntegration();
    }

    /**
     * Quick NHL analysis for tonight's games
     */
    public static function quickNhlAnalysis(float $stake = 8.0, float $minRoi = 10.0): array
    {
        $factory = new self();
        return $factory->integration->executeNhlSgpBuilder([
            'stake' => $stake,
            'min_roi' => $minRoi
        ]);
    }

    /**
     * Quick Kelly calculation
     */
    public static function quickKelly(float $probability, float $odds, float $bankroll = 1000.0): array
    {
        $factory = new self();
        return $factory->integration->calculateKellyCriterion([
            'probability' => $probability,
            'odds' => $odds,
            'bankroll' => $bankroll
        ]);
    }

    /**
     * Quick arbitrage scan
     */
    public static function quickArbitrageScan(string $sport = 'icehockey_nhl'): array
    {
        $factory = new self();
        return $factory->integration->findArbitrageOpportunities([
            'sport' => $sport,
            'min_profit' => 1.0
        ]);
    }

    /**
     * Quick market analysis
     */
    public static function quickMarketAnalysis(string $sport = 'icehockey_nhl'): array
    {
        $factory = new self();
        return $factory->integration->executeMarketAnalysis([
            'sport' => $sport,
            'timeframe' => '24h'
        ]);
    }
}

// Example usage and testing functions
if (basename(__FILE__) === basename($_SERVER['SCRIPT_NAME'] ?? '')) {
    echo "🐍 EQ12 PHP-Python Integration Bridge\n";
    echo "=====================================\n\n";

    $integration = new EQ12PythonIntegration();

    // Test NHL SGP Builder
    echo "Testing NHL SGP Builder...\n";
    $result = $integration->executeNhlSgpBuilder(['stake' => 8.0]);
    echo "Result: " . ($result['success'] ? 'SUCCESS' : 'FAILED') . "\n";
    if (!$result['success']) {
        echo "Error: " . ($result['error'] ?? 'Unknown error') . "\n";
    }
    echo "\n";

    // Test Kelly Calculator
    echo "Testing Kelly Calculator...\n";
    $kellyResult = $integration->calculateKellyCriterion([
        'probability' => 0.55,
        'odds' => 2.0,
        'bankroll' => 1000.0
    ]);
    echo "Result: " . ($kellyResult['success'] ? 'SUCCESS' : 'FAILED') . "\n";
    if ($kellyResult['success'] && isset($kellyResult['data'])) {
        echo "Kelly Fraction: " . ($kellyResult['data']['kelly_fraction'] ?? 'N/A') . "\n";
    }
    echo "\n";

    // Show execution stats
    echo "Execution Statistics:\n";
    $stats = $integration->getExecutionStats();
    echo "Total Executions: " . $stats['total_executions'] . "\n";
    echo "Success Rate: " . number_format($stats['success_rate'], 2) . "%\n";
    echo "Average Execution Time: " . number_format($stats['average_execution_time'], 3) . "s\n";

    echo "\n✅ PHP-Python Integration Bridge is ready!\n";
}
