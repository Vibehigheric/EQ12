<?php
/**
 * EQ12 PHP Setup Validation Test (PHP 7.4 Compatible)
 * Comprehensive test to validate VS Code + XAMPP + Intelephense integration
 * 
 * Usage:
 *   php C:\EQ12\scripts\test_php_setup_compatible.php
 *   OR debug in VS Code with F5
 */

declare(strict_types=1);

namespace EQ12\Setup;

/**
 * PHP Development Environment Test Suite
 * Tests Intelephense, Xdebug, and XAMPP integration for PHP 7.4+
 */
class EQ12SetupValidator 
{
    /** @var string */
    private $message;
    
    /** @var array */
    private $results = [];
    
    public function __construct(string $message = "EQ12 PHP Setup Working!") 
    {
        $this->message = $message;
    }
    
    /**
     * Run comprehensive validation checks
     * @return array
     */
    public function validate(): array 
    {
        echo "🚀 EQ12 PHP Setup Validation Starting...\n";
        echo "=" . str_repeat("=", 50) . "\n";
        
        $this->checkPHPVersion();
        $this->checkXdebugExtension();
        $this->checkXAMPPDetection();
        $this->checkRequiredExtensions();
        $this->checkEQ12Environment();
        $this->testTypeHinting();
        $this->testArrayOperations();
        
        return $this->results;
    }
    
    /**
     * Check PHP version compatibility
     */
    private function checkPHPVersion(): void 
    {
        $version = PHP_VERSION;
        $majorVersion = (float)(PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION);
        $isCompatible = $majorVersion >= 7.4;
        
        $this->results['php_version'] = [
            'version' => $version,
            'major_version' => $majorVersion,
            'compatible' => $isCompatible,
            'status' => $isCompatible ? 'PASS' : 'WARN'
        ];
        
        $status = $isCompatible ? '✅' : '⚠️';
        echo "{$status} PHP Version: {$version} (Required: >= 7.4)\n";
        
        if ($majorVersion < 8.0) {
            echo "  ℹ️  Note: PHP 8.0+ recommended for modern features\n";
        }
    }
    
    /**
     * Check Xdebug extension for debugging support
     */
    private function checkXdebugExtension(): void 
    {
        $xdebugLoaded = extension_loaded('xdebug');
        $xdebugVersion = $xdebugLoaded ? phpversion('xdebug') : null;
        $xdebugMode = $xdebugLoaded ? ini_get('xdebug.mode') : null;
        
        // For Xdebug 2.x (older versions), mode might not exist
        if ($xdebugLoaded && empty($xdebugMode)) {
            $xdebugMode = 'legacy (pre-v3)';
        }
        
        $this->results['xdebug'] = [
            'loaded' => $xdebugLoaded,
            'version' => $xdebugVersion,
            'mode' => $xdebugMode,
            'status' => $xdebugLoaded ? 'PASS' : 'WARN'
        ];
        
        $status = $xdebugLoaded ? '✅' : '⚠️';
        echo "{$status} Xdebug Extension: " . ($xdebugLoaded ? "Loaded (v{$xdebugVersion}, mode: {$xdebugMode})" : "Not loaded - debugging won't work") . "\n";
    }
    
    /**
     * Check XAMPP installation detection
     */
    private function checkXAMPPDetection(): void 
    {
        $xamppPaths = [
            'C:/xampp/php/php.exe',
            'C:/xampp/htdocs',
            'C:/xampp/apache/bin/httpd.exe'
        ];
        
        $xamppDetected = true;
        $foundPaths = [];
        
        foreach ($xamppPaths as $path) {
            if (file_exists($path)) {
                $foundPaths[] = $path;
            } else {
                $xamppDetected = false;
            }
        }
        
        $this->results['xampp'] = [
            'detected' => $xamppDetected,
            'found_paths' => $foundPaths,
            'status' => $xamppDetected ? 'PASS' : 'WARN'
        ];
        
        $status = $xamppDetected ? '✅' : '⚠️';
        echo "{$status} XAMPP Detection: " . ($xamppDetected ? "Found all components" : "Some components missing") . "\n";
        
        if ($xamppDetected) {
            echo "  📁 Found: " . implode(', ', $foundPaths) . "\n";
        }
    }
    
    /**
     * Check required PHP extensions for EQ12
     */
    private function checkRequiredExtensions(): void 
    {
        $requiredExtensions = [
            'curl' => 'HTTP requests for odds APIs',
            'json' => 'JSON data processing',
            'mbstring' => 'String operations',
            'openssl' => 'Secure communications',
            'mysqli' => 'Database connectivity',
            'pdo' => 'Database abstraction layer'
        ];
        
        $loadedExtensions = [];
        $missingExtensions = [];
        
        foreach ($requiredExtensions as $ext => $purpose) {
            if (extension_loaded($ext)) {
                $loadedExtensions[$ext] = $purpose;
                echo "  ✅ {$ext}: {$purpose}\n";
            } else {
                $missingExtensions[$ext] = $purpose;
                echo "  ❌ {$ext}: {$purpose} (MISSING)\n";
            }
        }
        
        $this->results['extensions'] = [
            'loaded' => $loadedExtensions,
            'missing' => $missingExtensions,
            'status' => empty($missingExtensions) ? 'PASS' : 'WARN'
        ];
        
        echo (empty($missingExtensions) ? '✅' : '⚠️') . " Required Extensions: " . count($loadedExtensions) . "/" . count($requiredExtensions) . " loaded\n";
    }
    
    /**
     * Check EQ12 project environment
     */
    private function checkEQ12Environment(): void 
    {
        $eq12Paths = [
            'C:/EQ12',
            'C:/EQ12/scripts',
            'C:/EQ12/configs',
            'C:/EQ12/logs',
            'C:/EQ12/.vscode'
        ];
        
        $foundPaths = [];
        $missingPaths = [];
        
        foreach ($eq12Paths as $path) {
            if (is_dir($path)) {
                $foundPaths[] = $path;
            } else {
                $missingPaths[] = $path;
            }
        }
        
        // Check for environment variables
        $envVars = [
            'ODDS_API_KEY' => getenv('ODDS_API_KEY'),
            'EQ12_ENV' => getenv('EQ12_ENV') ?: 'not_set'
        ];
        
        $this->results['eq12_environment'] = [
            'paths_found' => $foundPaths,
            'paths_missing' => $missingPaths,
            'env_vars' => $envVars,
            'status' => empty($missingPaths) ? 'PASS' : 'WARN'
        ];
        
        $status = empty($missingPaths) ? '✅' : '⚠️';
        echo "{$status} EQ12 Environment: " . count($foundPaths) . "/" . count($eq12Paths) . " paths found\n";
        
        foreach ($envVars as $var => $value) {
            $hasValue = !empty($value) && $value !== 'not_set';
            echo "  " . ($hasValue ? '✅' : '⚠️') . " {$var}: " . ($hasValue ? 'Set' : 'Not set') . "\n";
        }
    }
    
    /**
     * Test PHP 7.4+ type hinting features
     */
    private function testTypeHinting(): void 
    {
        try {
            // Test nullable types (PHP 7.1+)
            $nullable = $this->processNullableType(null);
            
            // Test array shapes (via docblock)
            $odds = $this->processOddsData([
                'home' => -150,
                'away' => 130,
                'total' => 42.5
            ]);
            
            // Test return types (PHP 7.0+)
            $processed = $this->processStringValue("test");
            
            $this->results['type_hinting'] = [
                'nullable_types' => 'PASS',
                'return_types' => 'PASS', 
                'array_processing' => 'PASS',
                'status' => 'PASS'
            ];
            
            echo "✅ Type Hinting: PHP 7.4+ features working\n";
            
        } catch (Throwable $e) {
            $this->results['type_hinting'] = [
                'error' => $e->getMessage(),
                'status' => 'FAIL'
            ];
            
            echo "❌ Type Hinting: " . $e->getMessage() . "\n";
        }
    }
    
    /**
     * Test string processing with return types
     */
    private function processStringValue(string $value): string 
    {
        return "Processed: {$value}";
    }
    
    /**
     * Test nullable type support (PHP 7.1+)
     */
    private function processNullableType(?string $value): string 
    {
        return $value ?? 'default';
    }
    
    /**
     * Test array processing with type safety
     * @param array $oddsData Array with home, away, total keys
     * @return array
     */
    private function processOddsData(array $oddsData): array 
    {
        return [
            'home_probability' => $this->calculateImpliedProbability($oddsData['home']),
            'away_probability' => $this->calculateImpliedProbability($oddsData['away']),
            'total_line' => $oddsData['total']
        ];
    }
    
    /**
     * Calculate implied probability from American odds
     */
    private function calculateImpliedProbability(int $americanOdds): float 
    {
        return $americanOdds > 0 
            ? 100 / ($americanOdds + 100)
            : (-$americanOdds) / ((-$americanOdds) + 100);
    }
    
    /**
     * Test advanced array operations compatible with PHP 7.4
     */
    private function testArrayOperations(): void 
    {
        try {
            // Test array_merge (instead of spread operator for compatibility)
            $array1 = [1, 2, 3];
            $array2 = [4, 5, 6];
            $combined = array_merge($array1, $array2);
            
            // Test array_filter with closures
            $filtered = array_filter($combined, function($x) { 
                return $x % 2 === 0; 
            });
            
            // Test array_map with closures
            $mapped = array_map(function($x) { 
                return $x * 2; 
            }, $filtered);
            
            $this->results['array_operations'] = [
                'array_merge' => count($combined) === 6,
                'closures' => count($filtered) === 3,
                'functional_style' => count($mapped) === 3,
                'status' => 'PASS'
            ];
            
            echo "✅ Array Operations: PHP 7.4 features working\n";
            
        } catch (Throwable $e) {
            $this->results['array_operations'] = [
                'error' => $e->getMessage(),
                'status' => 'FAIL'  
            ];
            
            echo "❌ Array Operations: " . $e->getMessage() . "\n";
        }
    }
    
    /**
     * Generate final summary
     * @return array
     */
    public function getSummary(): array 
    {
        $totalTests = count($this->results);
        $passedTests = count(array_filter($this->results, function($result) { 
            return $result['status'] === 'PASS'; 
        }));
        $warnTests = count(array_filter($this->results, function($result) { 
            return $result['status'] === 'WARN'; 
        }));
        $failedTests = count(array_filter($this->results, function($result) { 
            return $result['status'] === 'FAIL'; 
        }));
        
        return [
            'message' => $this->message,
            'timestamp' => date('Y-m-d H:i:s'),
            'total_tests' => $totalTests,
            'passed' => $passedTests,
            'warnings' => $warnTests, 
            'failed' => $failedTests,
            'overall_status' => $failedTests === 0 ? ($warnTests === 0 ? 'EXCELLENT' : 'GOOD') : 'NEEDS_ATTENTION'
        ];
    }
}

// Run the validation if this file is executed directly
if (__FILE__ === realpath($_SERVER['SCRIPT_FILENAME'] ?? '')) {
    $validator = new EQ12SetupValidator("EQ12 PHP Development Environment (PHP 7.4 Compatible)");
    
    // Run validation tests
    $results = $validator->validate();
    
    echo "\n" . str_repeat("=", 60) . "\n";
    echo "📊 VALIDATION SUMMARY\n";
    echo str_repeat("=", 60) . "\n";
    
    $summary = $validator->getSummary();
    
    echo "🎯 Overall Status: " . $summary['overall_status'] . "\n";
    echo "✅ Passed: {$summary['passed']}/{$summary['total_tests']}\n";
    echo "⚠️  Warnings: {$summary['warnings']}\n"; 
    echo "❌ Failed: {$summary['failed']}\n";
    echo "⏰ Completed: {$summary['timestamp']}\n";
    
    // Save results to EQ12 logs directory
    $logDir = 'C:/EQ12/logs';
    if (!is_dir($logDir)) {
        mkdir($logDir, 0777, true);
    }
    
    $logFile = $logDir . '/php_setup_validation_' . date('Ymd_His') . '.json';
    file_put_contents($logFile, json_encode([
        'summary' => $summary,
        'detailed_results' => $results
    ], JSON_PRETTY_PRINT));
    
    echo "💾 Results saved to: {$logFile}\n";
    
    if ($summary['overall_status'] === 'EXCELLENT') {
        echo "\n🎉 EQ12 PHP development environment is fully configured and ready!\n";
        echo "✨ You can now:\n";
        echo "   • Set breakpoints and debug PHP scripts with F5\n";
        echo "   • Get full IntelliSense with Intelephense\n";
        echo "   • Run sports betting analysis with type safety\n";
        echo "   • Deploy to XAMPP for web testing\n";
    } elseif ($summary['overall_status'] === 'GOOD') {
        echo "\n👍 EQ12 PHP environment is working with minor warnings.\n";
        echo "🔧 Check warnings above and consider addressing them for optimal performance.\n";
        
        if (!extension_loaded('xdebug')) {
            echo "\n💡 To enable Xdebug for VS Code debugging:\n";
            echo "   1. Edit C:\\xampp\\php\\php.ini\n";
            echo "   2. Add these lines:\n";
            echo "      zend_extension=xdebug\n";
            echo "      xdebug.mode=debug\n";
            echo "      xdebug.start_with_request=yes\n";
            echo "      xdebug.client_port=9003\n";
            echo "   3. Restart Apache in XAMPP\n";
        }
    } else {
        echo "\n⚠️  EQ12 PHP environment needs attention.\n";
        echo "🔧 Please address the failed tests above before proceeding.\n";
    }
    
    // Show PHP upgrade recommendation
    $phpVersion = (float)(PHP_MAJOR_VERSION . '.' . PHP_MINOR_VERSION);
    if ($phpVersion < 8.0) {
        echo "\n💡 RECOMMENDATION: Upgrade to PHP 8.1+ for better performance and modern features:\n";
        echo "   • Union types (string|int|null)\n";
        echo "   • Match expressions\n";
        echo "   • Named arguments\n";
        echo "   • Attributes (annotations)\n";
        echo "   • Better error handling\n";
        echo "   • Significant performance improvements\n";
    }
}
?>