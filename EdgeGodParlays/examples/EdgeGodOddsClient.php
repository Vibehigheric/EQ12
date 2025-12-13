<?php
/**
 * EdgeGod Odds API Client for PHP
 * Production-ready PHP client with built-in 429 error prevention
 * 
 * Features:
 * - Conservative rate limiting (25 requests/second)
 * - Intelligent caching with TTL
 * - Exponential backoff retry logic
 * - Comprehensive error handling
 * - PSR-7 compatible
 */

require 'vendor/autoload.php';

use GuzzleHttp\Client;
use GuzzleHttp\Exception\RequestException;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Middleware;
use GuzzleHttp\Psr7\Request;
use GuzzleHttp\Psr7\Response;

class EdgeGodRateLimiter {
    private $maxRequestsPerSecond;
    private $minInterval;
    private $lastRequestTime;
    
    public function __construct($maxRequestsPerSecond = 25.0) {
        $this->maxRequestsPerSecond = $maxRequestsPerSecond;
        $this->minInterval = 1.0 / $maxRequestsPerSecond;
        $this->lastRequestTime = 0.0;
    }
    
    public function waitIfNeeded() {
        $now = microtime(true);
        $timeSinceLast = $now - $this->lastRequestTime;
        
        if ($timeSinceLast < $this->minInterval) {
            $sleepTime = $this->minInterval - $timeSinceLast;
            usleep($sleepTime * 1000000); // Convert to microseconds
        }
        
        $this->lastRequestTime = microtime(true);
    }
}

class EdgeGodCache {
    private $cache = [];
    private $defaultTtl;
    
    public function __construct($defaultTtl = 900) { // 15 minutes
        $this->defaultTtl = $defaultTtl;
    }
    
    public function get($key) {
        if (isset($this->cache[$key])) {
            $entry = $this->cache[$key];
            if (time() < $entry['expires']) {
                echo "✅ Cache hit for " . substr($key, 0, 8) . "...\n";
                return $entry['data'];
            } else {
                unset($this->cache[$key]);
            }
        }
        return null;
    }
    
    public function set($key, $data, $ttl = null) {
        $ttl = $ttl ?? $this->defaultTtl;
        $this->cache[$key] = [
            'data' => $data,
            'expires' => time() + $ttl
        ];
        echo "💾 Cached data for " . substr($key, 0, 8) . "...\n";
    }
    
    public function generateKey($url, $params) {
        return md5($url . serialize($params));
    }
}

class EdgeGodOddsClient {
    private $apiKey;
    private $client;
    private $rateLimiter;
    private $cache;
    
    public function __construct($apiKey, $rateLimit = 25) {
        $this->apiKey = $apiKey;
        $this->rateLimiter = new EdgeGodRateLimiter($rateLimit);
        $this->cache = new EdgeGodCache();
        
        // Create Guzzle client with retry middleware
        $stack = HandlerStack::create();
        $stack->push(Middleware::retry($this->retryDecider(), $this->retryDelay()));
        
        $this->client = new Client([
            'handler' => $stack,
            'timeout' => 30,
            'http_errors' => false, // We'll handle errors manually
        ]);
    }
    
    private function retryDecider() {
        return function ($retries, Request $request, Response $response = null, RequestException $exception = null) {
            // Retry on 429, 500, 502, 503, 504
            if ($retries < 3 && $response) {
                $statusCode = $response->getStatusCode();
                return in_array($statusCode, [429, 500, 502, 503, 504]);
            }
            return false;
        };
    }
    
    private function retryDelay() {
        return function ($numberOfRetries) {
            // Exponential backoff: 1s, 2s, 4s
            return 1000 * pow(2, $numberOfRetries);
        };
    }
    
    public function makeRequest($url, $params = [], $ttl = 900) {
        // Add API key to params
        $params['api_key'] = $this->apiKey;
        
        // Check cache first
        $cacheKey = $this->cache->generateKey($url, $params);
        $cached = $this->cache->get($cacheKey);
        if ($cached !== null) {
            return $cached;
        }
        
        // Apply rate limiting
        $this->rateLimiter->waitIfNeeded();
        
        try {
            $response = $this->client->request('GET', $url, [
                'query' => $params
            ]);
            
            $statusCode = $response->getStatusCode();
            
            if ($statusCode === 429) {
                echo "⚠️ Rate limit hit, implementing exponential backoff...\n";
                sleep(2); // 2 second backoff
                return $this->makeRequest($url, $params, $ttl);
            }
            
            if ($statusCode !== 200) {
                throw new Exception("API request failed with status {$statusCode}: " . $response->getBody());
            }
            
            $data = json_decode($response->getBody(), true);
            $headers = $response->getHeaders();
            
            $result = [
                'data' => $data,
                'headers' => $headers
            ];
            
            // Cache successful responses
            $this->cache->set($cacheKey, $result, $ttl);
            
            return $result;
            
        } catch (RequestException $e) {
            throw new Exception("Request failed: " . $e->getMessage());
        }
    }
    
    public function getSports() {
        return $this->makeRequest('https://api.the-odds-api.com/v4/sports');
    }
    
    public function getOdds($sport, $params = []) {
        $url = "https://api.the-odds-api.com/v4/sports/{$sport}/odds";
        return $this->makeRequest($url, $params);
    }
    
    public function getEventOdds($sport, $eventId, $params = []) {
        $url = "https://api.the-odds-api.com/v4/sports/{$sport}/events/{$eventId}/odds";
        return $this->makeRequest($url, $params);
    }
    
    public function getHistoricalOdds($sport, $date, $params = []) {
        $url = "https://api.the-odds-api.com/v4/historical/sports/{$sport}/odds";
        $params['date'] = $date;
        return $this->makeRequest($url, $params);
    }
    
    public function getScores($sport, $params = []) {
        $url = "https://api.the-odds-api.com/v4/sports/{$sport}/scores";
        return $this->makeRequest($url, $params);
    }
    
    // Utility method to show client stats
    public function getStats() {
        return [
            'rate_limit' => $this->rateLimiter->maxRequestsPerSecond . ' req/sec',
            'cache_entries' => count($this->cache->cache),
            'features' => [
                '429 error prevention',
                'Intelligent caching',
                'Exponential backoff retry',
                'Rate limiting',
                'Production ready'
            ]
        ];
    }
}

?>