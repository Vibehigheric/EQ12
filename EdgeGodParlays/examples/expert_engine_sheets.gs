/**
 * EdgeGod Expert Engine for Google Apps Script
 * Enhanced version for Google Sheets integration with expert betting analysis
 * 
 * Features:
 * - Built-in 429 error prevention (EdgeGod rate limiting)
 * - Expert filter integration for betting analysis
 * - Automatic Google Sheets population
 * - Best price detection across bookmakers
 * - Value opportunity identification
 * - Production-ready for automated triggers
 */

/**
 * Expert Filter Configuration
 */
class ExpertFilter {
  constructor(config = {}) {
    this.minImpliedProbability = config.minImpliedProbability || 0.40;  // 40% minimum
    this.maxImpliedProbability = config.maxImpliedProbability || 0.65;  // 65% maximum
    this.minValueThreshold = config.minValueThreshold || 0.05;          // 5% minimum edge
    this.preferredMarkets = config.preferredMarkets || ['h2h', 'spreads', 'totals'];
    this.preferredSports = config.preferredSports || ['americanfootball_nfl', 'basketball_nba'];
    this.timeWindowHours = config.timeWindowHours || 24;               // Next 24 hours
  }
}

/**
 * EdgeGod Expert Engine Client for Apps Script
 */
class EdgeGodExpertSheetsClient {
  constructor(apiKey, expertFilter = null) {
    this.apiKey = apiKey;
    this.expertFilter = expertFilter || new ExpertFilter();
    this.baseUrl = 'https://api.the-odds-api.com/v4';
    
    // EdgeGod rate limiting
    this.rateLimit = 25; // 25 requests per second
    this.minInterval = 1000 / this.rateLimit;
    this.lastRequestTime = 0;
    this.cache = new Map();
  }
  
  waitForRateLimit() {
    const now = Date.now();
    const timeSinceLast = now - this.lastRequestTime;
    
    if (timeSinceLast < this.minInterval) {
      const waitTime = this.minInterval - timeSinceLast;
      Utilities.sleep(waitTime);
    }
    
    this.lastRequestTime = Date.now();
  }
  
  getCacheKey(url, params) {
    const cacheData = url + JSON.stringify(params);
    return Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, cacheData)
      .map(byte => (byte < 0 ? byte + 256 : byte).toString(16).padStart(2, '0'))
      .join('');
  }
  
  makeRequest(url, params = {}) {
    params.apiKey = this.apiKey;
    
    // Check cache (15 min TTL)
    const cacheKey = this.getCacheKey(url, params);
    if (this.cache.has(cacheKey)) {
      const entry = this.cache.get(cacheKey);
      if (Date.now() - entry.timestamp < 900000) { // 15 minutes
        Logger.log(`✅ Cache hit for ${url.split('/').pop()}`);
        return entry.data;
      }
      this.cache.delete(cacheKey);
    }
    
    // Apply rate limiting
    this.waitForRateLimit();
    
    const queryString = Object.keys(params)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
      .join('&');
    
    const fullUrl = `${url}?${queryString}`;
    
    try {
      const response = UrlFetchApp.fetch(fullUrl, {
        method: 'GET',
        headers: { 'content-type': 'application/json' },
        muteHttpExceptions: true
      });
      
      if (response.getResponseCode() === 429) {
        Logger.log('⚠️ Rate limit hit, applying backoff...');
        Utilities.sleep(2000);
        return this.makeRequest(url, params);
      }
      
      if (response.getResponseCode() !== 200) {
        throw new Error(`API request failed: ${response.getResponseCode()}`);
      }
      
      const data = JSON.parse(response.getContentText());
      
      // Cache successful response
      this.cache.set(cacheKey, { data, timestamp: Date.now() });
      
      return data;
      
    } catch (error) {
      Logger.log(`❌ Request failed: ${error.toString()}`);
      throw error;
    }
  }
  
  getSports() {
    const url = `${this.baseUrl}/sports/`;
    let sports = this.makeRequest(url);
    
    // Filter to preferred sports
    if (this.expertFilter.preferredSports.length > 0) {
      sports = sports.filter(s => this.expertFilter.preferredSports.includes(s.key));
      Logger.log(`🎯 Filtered to ${sports.length} preferred sports`);
    }
    
    return sports;
  }
  
  getOdds(sportKey, regions = 'us', markets = 'h2h', oddsFormat = 'american', withTimeFilter = true) {
    const url = `${this.baseUrl}/sports/${sportKey}/odds`;
    const params = { regions, markets, oddsFormat };
    
    // Add time filtering for expert engine
    if (withTimeFilter) {
      const now = new Date();
      const commenceFrom = now.toISOString();
      const commenceTo = new Date(now.getTime() + (this.expertFilter.timeWindowHours * 60 * 60 * 1000)).toISOString();
      params.commenceTimeFrom = commenceFrom;
      params.commenceTimeTo = commenceTo;
      Logger.log(`🕒 Filtering events: next ${this.expertFilter.timeWindowHours} hours`);
    }
    
    const oddsData = this.makeRequest(url, params);
    
    // Apply expert filtering
    const filteredOdds = [];
    for (const event of oddsData) {
      const expertAnalysis = this.analyzeEventForExpertEngine(event);
      if (expertAnalysis.passesFilters) {
        event.expertAnalysis = expertAnalysis;
        filteredOdds.push(event);
      }
    }
    
    Logger.log(`🎯 Expert filter: ${filteredOdds.length}/${oddsData.length} events passed`);
    return filteredOdds;
  }
  
  analyzeEventForExpertEngine(event) {
    const analysis = {
      passesFilters: false,
      bestPrices: {},
      impliedProbabilities: {},
      valueOpportunities: [],
      recommendedBets: []
    };
    
    try {
      // Analyze all bookmakers and markets
      for (const bookmaker of (event.bookmakers || [])) {
        for (const market of (bookmaker.markets || [])) {
          const marketKey = market.key;
          
          // Skip if not preferred market
          if (!this.expertFilter.preferredMarkets.includes(marketKey)) {
            continue;
          }
          
          for (const outcome of (market.outcomes || [])) {
            const outcomeName = outcome.name;
            const price = outcome.price;
            
            // Track best prices
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
            if (price > 0) {
              impliedProb = 100 / (price + 100);
            } else {
              impliedProb = (-price) / (-price + 100);
            }
            
            analysis.impliedProbabilities[key] = impliedProb;
            
            // Check if within filter range
            if (impliedProb >= this.expertFilter.minImpliedProbability && 
                impliedProb <= this.expertFilter.maxImpliedProbability) {
              
              // Simple value calculation (replace with your model)
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
      
      analysis.passesFilters = analysis.valueOpportunities.length > 0;
      
    } catch (error) {
      Logger.log(`⚠️ Analysis error for event ${event.id}: ${error.toString()}`);
    }
    
    return analysis;
  }
  
  estimateTrueProbability(event, outcome) {
    // Placeholder - implement your probability model here
    return 0.50;
  }
}

/**
 * Main function - Expert Engine for Google Sheets
 */
function runExpertEngine() {
  // Configuration
  const SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit';
  const RECOMMENDATIONS_SHEET = 'Expert_Recommendations';
  const SUMMARY_SHEET = 'Expert_Summary';
  const API_KEY = 'YOUR_API_KEY'; // Set your API key here
  
  if (API_KEY === 'YOUR_API_KEY') {
    Logger.log('❌ Please set your API key in the script');
    return;
  }
  
  Logger.log('🎯 Starting EdgeGod Expert Engine Analysis...');
  
  try {
    // Configure expert filters
    const expertConfig = new ExpertFilter({
      minImpliedProbability: 0.35,
      maxImpliedProbability: 0.70,
      minValueThreshold: 0.03,
      preferredSports: ['americanfootball_nfl', 'basketball_nba'],
      timeWindowHours: 48
    });
    
    // Initialize client
    const client = new EdgeGodExpertSheetsClient(API_KEY, expertConfig);
    
    // Get all recommendations
    const allRecommendations = [];
    let totalEvents = 0;
    
    for (const sport of expertConfig.preferredSports) {
      try {
        Logger.log(`🏆 Analyzing ${sport}...`);
        const oddsData = client.getOdds(
          sport,
          'us',
          expertConfig.preferredMarkets.join(','),
          'american'
        );
        
        totalEvents += oddsData.length;
        
        for (const event of oddsData) {
          if (event.expertAnalysis && event.expertAnalysis.recommendedBets.length > 0) {
            // Flatten recommendations for spreadsheet
            for (const bet of event.expertAnalysis.recommendedBets) {
              allRecommendations.push([
                new Date().toISOString(),
                sport,
                event.home_team,
                event.away_team,
                event.commence_time,
                bet.confidence,
                bet.betType,
                bet.selection,
                bet.odds,
                bet.valueEdge,
                bet.bookmaker,
                `${event.home_team} vs ${event.away_team}`
              ]);
            }
          }
        }
      } catch (error) {
        Logger.log(`❌ Error processing ${sport}: ${error.toString()}`);
      }
    }
    
    // Open spreadsheet
    const ss = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
    
    // Update recommendations sheet
    let recSheet = ss.getSheetByName(RECOMMENDATIONS_SHEET);
    if (!recSheet) {
      recSheet = ss.insertSheet(RECOMMENDATIONS_SHEET);
    }
    
    // Clear and add headers
    recSheet.clear();
    const headers = [
      'Timestamp', 'Sport', 'Home Team', 'Away Team', 'Commence Time',
      'Confidence', 'Bet Type', 'Selection', 'Odds', 'Value Edge', 'Bookmaker', 'Match'
    ];
    recSheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    // Add recommendations
    if (allRecommendations.length > 0) {
      recSheet.getRange(2, 1, allRecommendations.length, headers.length)
        .setValues(allRecommendations);
    }
    
    // Update summary sheet
    let summarySheet = ss.getSheetByName(SUMMARY_SHEET);
    if (!summarySheet) {
      summarySheet = ss.insertSheet(SUMMARY_SHEET);
    }
    
    summarySheet.clear();
    const summaryData = [
      ['Metric', 'Value'],
      ['Last Update', new Date().toISOString()],
      ['Total Events Analyzed', totalEvents],
      ['Events with Value', allRecommendations.length],
      ['High Confidence Bets', allRecommendations.filter(r => r[5] === 'HIGH').length],
      ['Medium Confidence Bets', allRecommendations.filter(r => r[5] === 'MEDIUM').length],
      ['Filter Settings', ''],
      ['Min Probability', `${(expertConfig.minImpliedProbability * 100).toFixed(1)}%`],
      ['Max Probability', `${(expertConfig.maxImpliedProbability * 100).toFixed(1)}%`],
      ['Min Value Threshold', `${(expertConfig.minValueThreshold * 100).toFixed(1)}%`],
      ['Time Window', `${expertConfig.timeWindowHours} hours`]
    ];
    
    summarySheet.getRange(1, 1, summaryData.length, 2).setValues(summaryData);
    
    // Format sheets
    recSheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
    summarySheet.getRange(1, 1, 1, 2).setFontWeight('bold');
    summarySheet.getRange(7, 1, 1, 2).setFontWeight('bold');
    
    Logger.log(`✅ Analysis complete: ${allRecommendations.length} recommendations from ${totalEvents} events`);
    
  } catch (error) {
    Logger.log(`❌ Expert Engine error: ${error.toString()}`);
  }
}

/**
 * Set up time-driven trigger for automatic analysis
 */
function setupAutomaticTrigger() {
  // Delete existing triggers
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'runExpertEngine') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  
  // Create new trigger to run every 4 hours
  ScriptApp.newTrigger('runExpertEngine')
    .timeBased()
    .everyHours(4)
    .create();
    
  Logger.log('✅ Automatic trigger set up to run every 4 hours');
}

/**
 * Manual trigger setup function
 */
function setupManualTrigger() {
  setupAutomaticTrigger();
}