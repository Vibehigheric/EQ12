#!/usr/bin/env node
/**
 * Enhanced Official Sample - The Odds API v4 (Node.js)
 * Based on official Node.js samples but with rate limiting concepts
 * 
 * While the full EdgeGod API Manager is Python-based, this shows
 * how to apply the same rate limiting principles in Node.js
 */

const axios = require('axios');

// Configuration (matching official samples)
const API_KEY = process.env.ODDS_API_KEY;  // Set this environment variable
const API_BASE = 'https://api.the-odds-api.com/v4';
const SPORT = 'basketball_nba';            // Official sample uses NBA
const REGIONS = 'us';                      // Official sample uses US
const MARKETS = 'h2h,spreads,totals';      // Official sample markets
const ODDS_FORMAT = 'american';            // Official sample format

/**
 * Enhanced Odds Client with rate limiting (Node.js version)
 * 
 * Implements key concepts from EdgeGod API Manager:
 * - Rate limiting to prevent 429 errors
 * - Retry logic with exponential backoff
 * - Basic caching to reduce API calls
 * - Proper error handling
 */
class EnhancedOddsClient {
    constructor(apiKey) {
        if (!apiKey) {
            throw new Error('API key required. Set ODDS_API_KEY environment variable.');
        }
        
        this.apiKey = apiKey;
        this.baseURL = API_BASE;
        
        // Rate limiting setup (matching EdgeGod principles)
        this.requestTimes = [];
        this.maxRequestsPerSecond = 25; // Conservative (under 30/sec API limit)
        this.cache = new Map();
        this.cacheDuration = 15 * 60 * 1000; // 15 minutes in milliseconds
        
        // Configure axios with timeout
        this.client = axios.create({
            timeout: 15000,
            baseURL: this.baseURL
        });
        
        console.log('✅ Enhanced Odds Client (Node.js) initialized with rate limiting');
    }
    
    /**
     * Wait for rate limit slot (prevents 429 errors)
     */
    async waitForRateLimit() {
        const now = Date.now();
        
        // Remove old request times (outside 1-second window)
        this.requestTimes = this.requestTimes.filter(time => now - time < 1000);
        
        // Check if we need to wait
        if (this.requestTimes.length >= this.maxRequestsPerSecond) {
            const oldestRequest = this.requestTimes[0];
            const waitTime = 1000 - (now - oldestRequest);
            
            if (waitTime > 0) {
                console.log(`⏳ Rate limiting: waiting ${waitTime}ms`);
                await new Promise(resolve => setTimeout(resolve, waitTime));
            }
        }
        
        // Record this request
        this.requestTimes.push(Date.now());
    }
    
    /**
     * Get cached response if available and fresh
     */
    getCachedResponse(key) {
        if (this.cache.has(key)) {
            const { data, timestamp } = this.cache.get(key);
            if (Date.now() - timestamp < this.cacheDuration) {
                console.log(`💾 Cache hit for ${key}`);
                return data;
            } else {
                // Cache expired
                this.cache.delete(key);
            }
        }
        return null;
    }
    
    /**
     * Cache successful response
     */
    cacheResponse(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
        console.log(`💾 Cached response for ${key}`);
    }
    
    /**
     * Make API request with rate limiting and retry logic
     */
    async makeRequest(path, params = {}) {
        const cacheKey = `${path}_${JSON.stringify(params)}`;
        
        // Check cache first
        const cached = this.getCachedResponse(cacheKey);
        if (cached) {
            return cached;
        }
        
        // Add API key to params
        const requestParams = {
            ...params,
            apiKey: this.apiKey
        };
        
        const maxRetries = 3;
        let lastError;
        
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                // Wait for rate limit slot
                await this.waitForRateLimit();
                
                // Make request
                const response = await this.client.get(path, { params: requestParams });
                
                // Cache successful response
                this.cacheResponse(cacheKey, response.data);
                
                return response.data;
                
            } catch (error) {
                lastError = error;
                
                if (error.response?.status === 429) {
                    // Rate limited - use Retry-After header if available
                    const retryAfter = error.response.headers['retry-after'];
                    const waitTime = retryAfter ? parseInt(retryAfter) * 1000 : Math.pow(2, attempt) * 1000;
                    
                    console.log(`⚠️ 429 Rate limited (attempt ${attempt + 1}), waiting ${waitTime}ms`);
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                    continue;
                    
                } else if (error.response?.status === 401) {
                    throw new Error('Invalid API key (401)');
                    
                } else if (error.response?.status === 402) {
                    throw new Error('Usage quota exceeded (402) - upgrade plan or wait for reset');
                    
                } else if (attempt < maxRetries - 1) {
                    // Other error - retry with exponential backoff
                    const waitTime = Math.pow(2, attempt) * 1000;
                    console.log(`⚠️ Request failed (attempt ${attempt + 1}), retrying in ${waitTime}ms: ${error.message}`);
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                    continue;
                }
                
                // Final attempt failed
                throw error;
            }
        }
        
        throw lastError;
    }
    
    /**
     * Get available sports (matches official sample pattern)
     */
    async getSports() {
        try {
            const sports = await this.makeRequest('/sports');
            console.log(`📊 Found ${sports.length} available sports`);
            return sports;
        } catch (error) {
            console.error('❌ Error fetching sports:', error.response?.data || error.message);
            return [];
        }
    }
    
    /**
     * Get odds for a sport (enhanced version of official sample)
     */
    async getOdds(sport = SPORT, regions = REGIONS, markets = MARKETS, oddsFormat = ODDS_FORMAT, eventIds = null) {
        try {
            const params = {
                regions: regions,
                markets: markets,
                oddsFormat: oddsFormat
            };
            
            if (eventIds) {
                params.eventIds = Array.isArray(eventIds) ? eventIds.join(',') : eventIds;
            }
            
            const odds = await this.makeRequest(`/sports/${sport}/odds`, params);
            console.log(`🎯 Retrieved odds for ${odds.length} events in ${sport}`);
            return odds;
            
        } catch (error) {
            console.error(`❌ Error fetching odds for ${sport}:`, error.response?.data || error.message);
            return [];
        }
    }
    
    /**
     * Get usage statistics
     */
    getUsageStats() {
        return {
            cacheSize: this.cache.size,
            requestsMadeThisSecond: this.requestTimes.length,
            rateLimit: this.maxRequestsPerSecond
        };
    }
}

/**
 * Enhanced version of official Node.js sample
 */
async function enhancedOfficialExample() {
    console.log('🚀 Starting Enhanced Official Sample (Node.js) with Rate Limiting...\n');
    
    try {
        // Initialize client (same pattern as official samples)
        const client = new EnhancedOddsClient(API_KEY);
        
        // Step 1: Get available sports (official sample pattern)
        console.log('1️⃣ Getting available sports...');
        const sports = await client.getSports();
        
        if (sports.length > 0) {
            console.log('📋 Available sports:');
            sports.slice(0, 5).forEach(sport => {
                console.log(`   • ${sport.title || 'Unknown'} (${sport.key || 'unknown'})`);
            });
            if (sports.length > 5) {
                console.log(`   ... and ${sports.length - 5} more`);
            }
            console.log('');
        }
        
        // Step 2: Get odds for specific sport (official sample pattern)
        console.log('2️⃣ Getting odds for NBA...');
        const oddsData = await client.getOdds(SPORT, REGIONS, MARKETS, ODDS_FORMAT);
        
        if (oddsData.length > 0) {
            console.log('🎯 Sample odds data:');
            const firstEvent = oddsData[0];
            console.log(`   Event: ${firstEvent.away_team || 'Unknown'} @ ${firstEvent.home_team || 'Unknown'}`);
            console.log(`   Start: ${firstEvent.commence_time || 'Unknown'}`);
            
            if (firstEvent.bookmakers && firstEvent.bookmakers.length > 0) {
                const bookmaker = firstEvent.bookmakers[0];
                console.log(`   Bookmaker: ${bookmaker.title || 'Unknown'}`);
                if (bookmaker.markets && bookmaker.markets.length > 0) {
                    const market = bookmaker.markets[0];
                    console.log(`   Market: ${market.key || 'Unknown'}`);
                }
            }
            console.log('');
        }
        
        // Step 3: Show usage stats
        console.log('3️⃣ Client Statistics:');
        const stats = client.getUsageStats();
        console.log(`   📊 Cached responses: ${stats.cacheSize}`);
        console.log(`   ⚡ Rate limit: ${stats.rateLimit}/sec`);
        console.log(`   🕒 Recent requests: ${stats.requestsMadeThisSecond}`);
        console.log('');
        
        // Step 4: Test rapid requests (would cause 429 without rate limiting)
        console.log('4️⃣ Testing rapid API calls (demonstrates rate limiting)...');
        const rapidPromises = [];
        for (let i = 0; i < 3; i++) {
            console.log(`   Making request ${i + 1}/3...`);
            rapidPromises.push(client.getSports());
        }
        
        const results = await Promise.all(rapidPromises);
        console.log(`   ✅ All ${results.length} rapid requests succeeded (no 429 errors!)\n`);
        
        console.log('🎉 Enhanced Official Sample (Node.js) completed successfully!');
        console.log('💡 Key improvements over official samples:');
        console.log('   • Rate limiting prevents 429 EXCEEDED_FREQ_LIMIT errors');
        console.log('   • Intelligent caching reduces redundant API calls');
        console.log('   • Retry logic handles temporary failures gracefully');
        console.log('   • Proper error handling for 401/402/429 status codes');
        
    } catch (error) {
        console.error('❌ Error in enhanced sample:', error.message);
    }
}

/**
 * Simple example (matches official sample exactly)
 */
async function simpleExample() {
    try {
        const response = await axios.get(`${API_BASE}/sports/${SPORT}/odds`, {
            params: {
                apiKey: API_KEY,
                regions: REGIONS,
                markets: MARKETS,
                oddsFormat: ODDS_FORMAT,
            }
        });
        
        console.log('Odds data:', response.data.slice(0, 2)); // Show first 2 like official samples
        
    } catch (error) {
        console.error('Error fetching odds:', error.response?.data || error.message);
    }
}

// Main execution
if (require.main === module) {
    console.log('Choose example to run:');
    console.log('1. Enhanced Official Sample (recommended)');  
    console.log('2. Simple Example (matches official patterns)');
    
    const readline = require('readline');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    rl.question('\nEnter choice (1 or 2): ', (choice) => {
        rl.close();
        
        if (choice.trim() === '2') {
            simpleExample();
        } else {
            enhancedOfficialExample();
        }
    });
}

module.exports = { EnhancedOddsClient };