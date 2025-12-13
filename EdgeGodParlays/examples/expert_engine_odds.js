#!/usr/bin/env node
/**
 * Enhanced Expert Engine Odds Client - Node.js Version
 * Combines your sample odds.js with EdgeGod rate limiting + expert engine integration
 * 
 * Features:
 * - Built-in 429 error prevention (EdgeGod rate limiting)
 * - Expert filter integration hooks
 * - Time window filtering (commenceTimeFrom/commenceTimeTo)
 * - Best price detection
 * - Implied probability calculations
 * - Value threshold analysis
 * - Production-ready async/await patterns
 */

const axios = require('axios');
const crypto = require('crypto');

/**
 * Expert filter configuration for the engine
 */
class ExpertFilter {
  constructor(config = {}) {
    this.minImpliedProbability = config.minImpliedProbability || 0.40;  // 40% minimum
    this.maxImpliedProbability = config.maxImpliedProbability || 0.65;  // 65% maximum
    this.minValueThreshold = config.minValueThreshold || 0.05;          // 5% minimum edge
    this.preferredMarkets = config.preferredMarkets || ['h2h', 'spreads', 'totals'];
    this.preferredSports = config.preferredSports || ['americanfootball_nfl', 'basketball_nba', 'soccer_epl'];
    this.timeWindowHours = config.timeWindowHours || 24;               // Next 24 hours
  }
}

/**
 * Enhanced Odds API client with expert engine integration
 */
class EdgeGodExpertOddsClient {
  constructor(apiKey, expertFilter = null) {
    this.apiKey = apiKey;
    this.expertFilter = expertFilter || new ExpertFilter();
    this.baseUrl = 'https://api.the-odds-api.com/v4';
    
    // EdgeGod rate limiting
    this.rateLimit = 25.0;  // Conservative 25 req/sec
    this.minInterval = 1000 / this.rateLimit; // milliseconds
    this.lastRequestTime = 0;
    this.cache = new Map();
    
    // Setup axios with retry logic
    this.setupAxiosRetry();
  }
  
  setupAxiosRetry() {
    // Configure axios interceptors for retry logic
    this.axiosInstance = axios.create({
      timeout: 30000,
    });
    
    // Response interceptor for 429 handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 429) {
          console.log('⚠️ Rate limit hit, applying exponential backoff...');
          await this.sleep(2000); // 2 second backoff
          return this.axiosInstance.request(error.config);
        }
        return Promise.reject(error);
      }
    );
  }
  
  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  async waitForRateLimit() {
    /**
     * EdgeGod rate limiting implementation
     */
    const now = Date.now();
    const timeSinceLast = now - this.lastRequestTime;
    
    if (timeSinceLast < this.minInterval) {
      const waitTime = this.minInterval - timeSinceLast;
      await this.sleep(waitTime);
    }
    
    this.lastRequestTime = Date.now();
  }
  
  getCacheKey(url, params) {
    const cacheData = url + JSON.stringify(params);
    return crypto.createHash('md5').update(cacheData).digest('hex');
  }
  
  async makeRequest(url, params = {}) {
    /**
     * Make rate-limited API request with caching
     */
    params = { ...params, apiKey: this.apiKey };
    
    // Check cache (15 min TTL)
    const cacheKey = this.getCacheKey(url, params);
    if (this.cache.has(cacheKey)) {
      const { data, timestamp } = this.cache.get(cacheKey);
      if (Date.now() - timestamp < 900000) { // 15 minutes
        console.log(`✅ Cache hit for ${url.split('/').pop()}`);
        return data;
      }
      this.cache.delete(cacheKey);
    }
    
    // Apply rate limiting
    await this.waitForRateLimit();
    
    try {
      const response = await this.axiosInstance.get(url, { params });
      const data = response.data;
      
      // Cache successful response
      this.cache.set(cacheKey, { data, timestamp: Date.now() });
      
      return data;
      
    } catch (error) {
      console.error(`❌ API request failed: ${error.message}`);
      throw error;
    }
  }
  
  async getSports() {
    /**
     * Get available sports - enhanced version of your original
     */
    const url = `${this.baseUrl}/sports/`;
    let sports = await this.makeRequest(url);
    
    // 🎯 EXPERT ENGINE INTEGRATION POINT
    if (this.expertFilter.preferredSports.length > 0) {
      sports = sports.filter(s => this.expertFilter.preferredSports.includes(s.key));
      console.log(`🎯 Filtered to ${sports.length} preferred sports`);
    }
    
    return sports;
  }
  
  async getOdds(sportKey, regions = 'us', markets = 'h2h', oddsFormat = 'american', withTimeFilter = true) {
    /**
     * Get odds with expert engine enhancements
     */
    const url = `${this.baseUrl}/sports/${sportKey}/odds`;
    const params = {
      regions,
      markets,
      oddsFormat,
    };
    
    // 🎯 EXPERT ENGINE TIME FILTERING
    if (withTimeFilter) {
      const now = new Date();
      const commenceFrom = now.toISOString();
      const commenceTo = new Date(now.getTime() + (this.expertFilter.timeWindowHours * 60 * 60 * 1000)).toISOString();
      params.commenceTimeFrom = commenceFrom;
      params.commenceTimeTo = commenceTo;
      console.log(`🕒 Filtering events: next ${this.expertFilter.timeWindowHours} hours`);
    }
    
    const oddsData = await this.makeRequest(url, params);
    
    // 🎯 EXPERT ENGINE FILTERING
    const filteredOdds = [];
    for (const event of oddsData) {
      const expertAnalysis = this.analyzeEventForExpertEngine(event);
      if (expertAnalysis.passesFilters) {
        event.expertAnalysis = expertAnalysis;
        filteredOdds.push(event);
      }
    }
    
    console.log(`🎯 Expert filter: ${filteredOdds.length}/${oddsData.length} events passed`);
    return filteredOdds;
  }
  
  analyzeEventForExpertEngine(event) {
    /**
     * 🎯 EXPERT ENGINE CORE ANALYSIS
     * This is where you'd plug in your expert logic
     */
    const analysis = {
      passesFilters: false,
      bestPrices: {},
      impliedProbabilities: {},
      valueOpportunities: [],
      recommendedBets: []
    };
    
    try {
      // Find best prices across all bookmakers for each market
      for (const bookmaker of (event.bookmakers || [])) {
        for (const market of (bookmaker.markets || [])) {
          const marketKey = market.key;
          
          // Skip if not in preferred markets
          if (!this.expertFilter.preferredMarkets.includes(marketKey)) {
            continue;
          }
          
          for (const outcome of (market.outcomes || [])) {
            const outcomeName = outcome.name;
            const price = outcome.price;
            
            // Track best price for each outcome
            const key = `${marketKey}_${outcomeName}`;
            if (!analysis.bestPrices[key] || price > analysis.bestPrices[key].price) {
              analysis.bestPrices[key] = {
                price: price,
                bookmaker: bookmaker.key,
                market: marketKey,
                outcome: outcomeName
              };
            }
            
            // Calculate implied probability
            let impliedProb;
            if (price > 0) { // American odds
              impliedProb = 100 / (price + 100);
            } else {
              impliedProb = (-price) / (-price + 100);
            }
            
            analysis.impliedProbabilities[key] = impliedProb;
            
            // 🎯 EXPERT FILTER: Check if within probability range
            if (impliedProb >= this.expertFilter.minImpliedProbability && 
                impliedProb <= this.expertFilter.maxImpliedProbability) {
              
              // Calculate potential value (simplified - you'd use your model here)
              const estimatedTrueProb = this.estimateTrueProbability(event, outcome);
              const value = estimatedTrueProb - impliedProb;
              
              if (value >= this.expertFilter.minValueThreshold) {
                analysis.valueOpportunities.push({
                  market: marketKey,
                  outcome: outcomeName,
                  price: price,
                  impliedProb: impliedProb,
                  estimatedProb: estimatedTrueProb,
                  value: value,
                  bookmaker: bookmaker.key
                });
                
                analysis.recommendedBets.push({
                  confidence: value > 0.10 ? 'HIGH' : 'MEDIUM',
                  betType: marketKey,
                  selection: outcomeName,
                  odds: price,
                  valueEdge: `${(value * 100).toFixed(1)}%`,
                  bookmaker: bookmaker.key
                });
              }
            }
          }
        }
      }
      
      // Event passes if it has value opportunities
      analysis.passesFilters = analysis.valueOpportunities.length > 0;
      
    } catch (error) {
      console.error(`⚠️ Error analyzing event ${event.id || 'unknown'}: ${error.message}`);
    }
    
    return analysis;
  }
  
  estimateTrueProbability(event, outcome) {
    /**
     * 🎯 EXPERT ENGINE: Your probability model goes here
     * This is a placeholder - replace with your actual model
     */
    // Placeholder logic - you'd implement your sophisticated model here
    // Consider factors like: team strength, historical performance, injuries, etc.
    
    // For now, return a simple estimate based on market consensus
    return 0.50; // Replace with your model
  }
  
  async getExpertRecommendations(sportsList = null) {
    /**
     * 🎯 EXPERT ENGINE MAIN FUNCTION
     * Get recommendations across multiple sports
     */
    sportsList = sportsList || this.expertFilter.preferredSports;
    const allRecommendations = [];
    
    console.log('🎯 Running Expert Engine Analysis...');
    console.log('='.repeat(50));
    
    for (const sport of sportsList) {
      try {
        console.log(`\n🏆 Analyzing ${sport}...`);
        const oddsData = await this.getOdds(
          sport,
          'us',
          this.expertFilter.preferredMarkets.join(','),
          'american'
        );
        
        for (const event of oddsData) {
          if (event.expertAnalysis && event.expertAnalysis.recommendedBets.length > 0) {
            const eventInfo = {
              sport: sport,
              homeTeam: event.home_team,
              awayTeam: event.away_team,
              commenceTime: event.commence_time,
              recommendations: event.expertAnalysis.recommendedBets
            };
            allRecommendations.push(eventInfo);
          }
        }
        
      } catch (error) {
        console.error(`❌ Error processing ${sport}: ${error.message}`);
      }
    }
    
    return {
      totalEventsAnalyzed: await this.getTotalEventsCount(sportsList),
      eventsWithValue: allRecommendations.length,
      recommendations: allRecommendations,
      filterSettings: {
        minProbability: `${(this.expertFilter.minImpliedProbability * 100).toFixed(1)}%`,
        maxProbability: `${(this.expertFilter.maxImpliedProbability * 100).toFixed(1)}%`,
        minValue: `${(this.expertFilter.minValueThreshold * 100).toFixed(1)}%`,
        timeWindow: `${this.expertFilter.timeWindowHours} hours`
      }
    };
  }
  
  async getTotalEventsCount(sportsList) {
    let total = 0;
    for (const sport of sportsList) {
      try {
        const odds = await this.getOdds(sport, 'us', 'h2h', 'american', false);
        total += odds.length;
      } catch (error) {
        // Continue on error
      }
    }
    return total;
  }
}

/**
 * Enhanced main function with expert engine integration
 */
async function main() {
  // Setup
  const API_KEY = process.env.ODDS_API_KEY || process.env.API_KEY || 'YOUR_API_KEY';
  
  if (API_KEY === 'YOUR_API_KEY') {
    console.error('❌ Please set ODDS_API_KEY environment variable');
    process.exit(1);
  }
  
  // Configure expert filters
  const expertConfig = new ExpertFilter({
    minImpliedProbability: 0.35,    // 35% minimum
    maxImpliedProbability: 0.70,    // 70% maximum
    minValueThreshold: 0.03,        // 3% minimum edge
    preferredSports: ['americanfootball_nfl', 'basketball_nba'],
    timeWindowHours: 48             // Next 48 hours
  });
  
  // Initialize enhanced client
  const client = new EdgeGodExpertOddsClient(API_KEY, expertConfig);
  
  console.log('🎯 EdgeGod Expert Engine - Enhanced Odds Analysis');
  console.log('='.repeat(60));
  console.log('✅ Built-in 429 error prevention');
  console.log('✅ Expert filter integration');
  console.log('✅ Best price detection');
  console.log('✅ Value opportunity analysis');
  console.log('✅ Time window filtering');
  console.log('='.repeat(60));
  
  try {
    // Get expert recommendations
    const recommendations = await client.getExpertRecommendations();
    
    console.log(`\n📊 EXPERT ENGINE RESULTS:`);
    console.log(`   📈 Events analyzed: ${recommendations.totalEventsAnalyzed}`);
    console.log(`   🎯 Events with value: ${recommendations.eventsWithValue}`);
    console.log(`   ⚙️ Filter settings: ${JSON.stringify(recommendations.filterSettings, null, 6)}`);
    
    if (recommendations.recommendations.length > 0) {
      console.log(`\n🏆 TOP RECOMMENDATIONS:`);
      recommendations.recommendations.slice(0, 5).forEach((rec, i) => {
        console.log(`\n   ${i + 1}. ${rec.homeTeam} vs ${rec.awayTeam}`);
        console.log(`      🕒 ${rec.commenceTime}`);
        console.log(`      🏆 ${rec.sport}`);
        
        rec.recommendations.forEach(bet => {
          console.log(`      💰 ${bet.confidence} confidence: ${bet.selection} @ ${bet.odds} ` +
                     `(Edge: ${bet.valueEdge}) via ${bet.bookmaker}`);
        });
      });
    } else {
      console.log('\n📋 No value opportunities found with current filters');
      console.log('💡 Try adjusting ExpertFilter settings for different results');
    }
    
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
  }
}

// Export for module use
module.exports = { EdgeGodExpertOddsClient, ExpertFilter };

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}