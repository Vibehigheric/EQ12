/**
 * EQ12 Enhanced Sports Betting Dashboard - Google Apps Script
 * ==========================================================
 * 
 * Advanced Google Sheets integration for EQ12 sports betting platform.
 * Combines The Odds API with intelligent automation for comprehensive
 * betting analytics and real-time monitoring.
 * 
 * Features:
 * - Real-time odds updates with multi-sport support
 * - Automated arbitrage opportunity detection
 * - Advanced betting analytics and performance tracking
 * - Integration with EQ12 AI recommendations
 * - Professional dashboard with visual indicators
 * 
 * Setup Instructions:
 * 1. Copy this code to Google Apps Script (Extensions → Apps Script)
 * 2. Set your API_KEY and configure parameters
 * 3. Set up time-driven triggers for automatic updates
 * 4. Share spreadsheet with EQ12 service account for Python integration
 * 
 * Author: EQ12 Development Team
 * Date: October 5, 2025
 */

// =============================================================================
// CONFIGURATION - UPDATE THESE VALUES
// =============================================================================

const CONFIG = {
  // The Odds API Configuration
  API_KEY: 'YOUR_ODDS_API_KEY', // Get from https://the-odds-api.com
  BASE_URL: 'https://api.the-odds-api.com/v4',
  
  // Default Parameters
  SPORT: 'upcoming', // 'upcoming' or specific sport like 'americanfootball_nfl'
  MARKETS: 'h2h,spreads,totals', // Available: h2h, spreads, totals, player_props
  REGIONS: 'us', // us, uk, eu, au
  ODDS_FORMAT: 'american', // american, decimal
  DATE_FORMAT: 'iso', // iso, unix
  
  // Update Settings
  MAX_EVENTS: 50, // Limit events to avoid API quota issues
  ARBITRAGE_MIN_PROFIT: 1.5, // Minimum profit % for arbitrage alerts
  
  // Sheet Names
  SHEETS: {
    LIVE_ODDS: 'Live Odds',
    ARBITRAGE: 'Arbitrage Opportunities', 
    PLAYER_PROPS: 'Player Props',
    BET_TRACKING: 'Bet Tracking',
    PERFORMANCE: 'Performance Analytics',
    AI_RECOMMENDATIONS: 'AI Recommendations',
    DASHBOARD: 'Dashboard'
  }
}

// =============================================================================
// MAIN FUNCTIONS
// =============================================================================

function updateEQ12Dashboard() {
  /**
   * Main function to update entire EQ12 betting dashboard
   */
  try {
    console.log('🚀 Starting EQ12 Dashboard update...')
    
    // Validate API key
    if (CONFIG.API_KEY === 'YOUR_ODDS_API_KEY') {
      throw new Error('Please set your Odds API key in CONFIG.API_KEY')
    }
    
    // Update all dashboard components
    updateLiveOdds()
    updateArbitrageOpportunities() 
    updatePlayerProps()
    updatePerformanceAnalytics()
    updateDashboardSummary()
    
    console.log('✅ EQ12 Dashboard updated successfully')
    
    // Show success notification
    SpreadsheetApp.getUi().alert(
      'EQ12 Dashboard Updated', 
      'All betting data has been refreshed successfully!', 
      SpreadsheetApp.getUi().AlertType.INFO
    )
    
  } catch (error) {
    console.error('❌ EQ12 Dashboard update failed:', error)
    SpreadsheetApp.getUi().alert(
      'Update Failed', 
      'Error: ' + error.message, 
      SpreadsheetApp.getUi().AlertType.ERROR
    )
  }
}

function updateLiveOdds() {
  /**
   * Update live odds for multiple sports
   */
  console.log('📊 Updating live odds...')
  
  const sheet = getOrCreateSheet(CONFIG.SHEETS.LIVE_ODDS)
  
  // Setup headers
  const headers = [
    'Event ID', 'Start Time', 'Home Team', 'Away Team', 'Sport',
    'Bookmaker', 'Market', 'Outcome', 'Odds', 'Point', 'Last Updated',
    'Value Indicator', 'Best Odds', 'Profit Margin'
  ]
  
  // Clear and set headers
  sheet.clear()
  sheet.getRange(1, 1, 1, headers.length).setValues([headers])
  
  // Format headers
  const headerRange = sheet.getRange(1, 1, 1, headers.length)
  headerRange.setBackground('#1f4e79')
  headerRange.setFontColor('#ffffff')
  headerRange.setFontWeight('bold')
  
  // Fetch odds data
  const oddsData = fetchOddsData(CONFIG.SPORT, CONFIG.MARKETS)
  
  if (!oddsData || oddsData.length === 0) {
    sheet.getRange(2, 1).setValue('No odds data available')
    return
  }
  
  // Process and format odds data
  const rows = []
  let bestOdds = {}
  
  // First pass: find best odds for each outcome
  oddsData.forEach(event => {
    event.bookmakers.forEach(bookmaker => {
      bookmaker.markets.forEach(market => {
        market.outcomes.forEach(outcome => {
          const key = `${event.id}_${market.key}_${outcome.name}`
          if (!bestOdds[key] || outcome.price > bestOdds[key]) {
            bestOdds[key] = outcome.price
          }
        })
      })
    })
  })
  
  // Second pass: create rows with value indicators
  oddsData.forEach(event => {
    event.bookmakers.forEach(bookmaker => {
      bookmaker.markets.forEach(market => {
        market.outcomes.forEach(outcome => {
          const key = `${event.id}_${market.key}_${outcome.name}`
          const isBestOdds = outcome.price === bestOdds[key]
          const valueIndicator = isBestOdds ? '⭐ BEST' : ''
          const profitMargin = calculateImpliedProfitMargin(outcome.price, CONFIG.ODDS_FORMAT)
          
          const row = [
            event.id,
            formatDateTime(event.commence_time),
            event.home_team,
            event.away_team,
            event.sport_title,
            bookmaker.title,
            market.key.toUpperCase(),
            formatOutcome(outcome, event),
            outcome.price,
            outcome.point || '',
            formatDateTime(bookmaker.last_update),
            valueIndicator,
            bestOdds[key],
            profitMargin + '%'
          ]
          rows.push(row)
        })
      })
    })
  })
  
  // Insert data
  if (rows.length > 0) {
    sheet.getRange(2, 1, rows.length, headers.length).setValues(rows)
    
    // Apply conditional formatting
    applyLiveOddsFormatting(sheet, rows.length)
  }
  
  console.log(`✅ Updated ${rows.length} odds entries`)
}

function updateArbitrageOpportunities() {
  /**
   * Detect and display arbitrage opportunities
   */
  console.log('🔍 Scanning arbitrage opportunities...')
  
  const sheet = getOrCreateSheet(CONFIG.SHEETS.ARBITRAGE)
  
  const headers = [
    'Opportunity ID', 'Game', 'Sport', 'Market', 'Profit %', 
    'Total Stake', 'Expected Return', 'Side 1', 'Book 1', 'Odds 1', 'Stake 1',
    'Side 2', 'Book 2', 'Odds 2', 'Stake 2', 'Status', 'Detected At'
  ]
  
  sheet.clear()
  sheet.getRange(1, 1, 1, headers.length).setValues([headers])
  
  // Format headers
  const headerRange = sheet.getRange(1, 1, 1, headers.length)
  headerRange.setBackground('#8B0000')
  headerRange.setFontColor('#ffffff')
  headerRange.setFontWeight('bold')
  
  // Fetch odds and detect arbitrage
  const oddsData = fetchOddsData(CONFIG.SPORT, 'h2h,spreads,totals')
  const arbitrageOps = detectArbitrageOpportunities(oddsData)
  
  if (arbitrageOps.length === 0) {
    sheet.getRange(2, 1).setValue('No arbitrage opportunities found')
    sheet.getRange(2, 2).setValue(`Last scan: ${new Date().toLocaleString()}`)
    return
  }
  
  // Prepare arbitrage rows
  const rows = []
  arbitrageOps.forEach((opp, index) => {
    const row = [
      `ARB_${index + 1}`,
      `${opp.awayTeam} @ ${opp.homeTeam}`,
      opp.sport,
      opp.market.toUpperCase(),
      opp.profitPercent.toFixed(2),
      opp.totalStake.toFixed(2),
      opp.expectedReturn.toFixed(2),
      opp.side1.outcome,
      opp.side1.bookmaker,
      opp.side1.odds,
      opp.side1.stake.toFixed(2),
      opp.side2.outcome,
      opp.side2.bookmaker, 
      opp.side2.odds,
      opp.side2.stake.toFixed(2),
      opp.profitPercent >= CONFIG.ARBITRAGE_MIN_PROFIT ? '🚨 HIGH VALUE' : 'ACTIVE',
      new Date().toLocaleString()
    ]
    rows.push(row)
  })
  
  // Insert data
  sheet.getRange(2, 1, rows.length, headers.length).setValues(rows)
  
  // Apply formatting
  applyArbitrageFormatting(sheet, rows.length)
  
  console.log(`🎯 Found ${arbitrageOps.length} arbitrage opportunities`)
  
  // Alert for high-value opportunities
  const highValueOps = arbitrageOps.filter(opp => opp.profitPercent >= CONFIG.ARBITRAGE_MIN_PROFIT)
  if (highValueOps.length > 0) {
    const message = `🚨 ${highValueOps.length} HIGH VALUE arbitrage opportunities detected!`
    console.log(message)
  }
}

function updatePlayerProps() {
  /**
   * Update player props data for supported sports
   */
  console.log('🏀 Updating player props...')
  
  const sheet = getOrCreateSheet(CONFIG.SHEETS.PLAYER_PROPS)
  
  const headers = [
    'Game', 'Player', 'Market', 'Line', 'Over Odds', 'Under Odds', 
    'Best Over', 'Best Under', 'Value Analysis', 'Updated At'
  ]
  
  sheet.clear()
  sheet.getRange(1, 1, 1, headers.length).setValues([headers])
  
  // Format headers
  const headerRange = sheet.getRange(1, 1, 1, headers.length)
  headerRange.setBackground('#006400')
  headerRange.setFontColor('#ffffff')
  headerRange.setFontWeight('bold')
  
  try {
    // Try to fetch player props for NBA/NFL
    const playerPropsData = fetchPlayerPropsData()
    
    if (playerPropsData.length === 0) {
      sheet.getRange(2, 1).setValue('No player props available')
      return
    }
    
    const rows = []
    playerPropsData.forEach(prop => {
      const row = [
        `${prop.awayTeam} @ ${prop.homeTeam}`,
        prop.player,
        prop.market,
        prop.line,
        prop.overOdds || 'N/A',
        prop.underOdds || 'N/A',
        prop.bestOver || 'N/A',
        prop.bestUnder || 'N/A',
        prop.valueAnalysis || 'Standard',
        new Date().toLocaleString()
      ]
      rows.push(row)
    })
    
    sheet.getRange(2, 1, rows.length, headers.length).setValues(rows)
    console.log(`✅ Updated ${rows.length} player props`)
    
  } catch (error) {
    console.log('⚠️ Player props not available:', error.message)
    sheet.getRange(2, 1).setValue('Player props not available for current sports')
  }
}

function updatePerformanceAnalytics() {
  /**
   * Calculate and update performance metrics from bet tracking
   */
  console.log('📈 Updating performance analytics...')
  
  const trackingSheet = getOrCreateSheet(CONFIG.SHEETS.BET_TRACKING)
  const performanceSheet = getOrCreateSheet(CONFIG.SHEETS.PERFORMANCE)
  
  const headers = [
    'Date', 'Total Bets', 'Winning Bets', 'Win Rate %', 
    'Total Staked', 'Total Returned', 'Net Profit', 'ROI %',
    'Best Sport', 'Avg Stake', 'Biggest Win', 'Biggest Loss'
  ]
  
  performanceSheet.clear()
  performanceSheet.getRange(1, 1, 1, headers.length).setValues([headers])
  
  // Get bet tracking data
  const betData = trackingSheet.getDataRange().getValues()
  
  if (betData.length <= 1) {
    performanceSheet.getRange(2, 1).setValue('No bet data available')
    return
  }
  
  // Calculate metrics (skip header row)
  const bets = betData.slice(1)
  const totalBets = bets.length
  const winningBets = bets.filter(bet => bet[9] === 'Win').length
  const winRate = totalBets > 0 ? (winningBets / totalBets) * 100 : 0
  
  const stakes = bets.map(bet => parseFloat(bet[7]) || 0)
  const returns = bets.map(bet => parseFloat(bet[10]) || 0)
  const profits = bets.map(bet => parseFloat(bet[11]) || 0)
  
  const totalStaked = stakes.reduce((sum, stake) => sum + stake, 0)
  const totalReturned = returns.reduce((sum, ret) => sum + ret, 0)
  const netProfit = totalReturned - totalStaked
  const roi = totalStaked > 0 ? (netProfit / totalStaked) * 100 : 0
  
  const avgStake = totalBets > 0 ? totalStaked / totalBets : 0
  const biggestWin = Math.max(...profits)
  const biggestLoss = Math.min(...profits)
  
  // Sport analysis
  const sportPerformance = {}
  bets.forEach(bet => {
    const sport = bet[2] || 'Unknown'
    if (!sportPerformance[sport]) {
      sportPerformance[sport] = { profit: 0, bets: 0 }
    }
    sportPerformance[sport].profit += parseFloat(bet[11]) || 0
    sportPerformance[sport].bets += 1
  })
  
  const bestSport = Object.keys(sportPerformance).reduce((best, sport) => 
    sportPerformance[sport].profit > (sportPerformance[best]?.profit || -Infinity) ? sport : best
  , 'N/A')
  
  const performanceRow = [
    new Date().toLocaleDateString(),
    totalBets,
    winningBets,
    winRate.toFixed(2),
    totalStaked.toFixed(2),
    totalReturned.toFixed(2), 
    netProfit.toFixed(2),
    roi.toFixed(2),
    bestSport,
    avgStake.toFixed(2),
    biggestWin.toFixed(2),
    biggestLoss.toFixed(2)
  ]
  
  performanceSheet.getRange(2, 1, 1, headers.length).setValues([performanceRow])
  
  // Apply performance formatting
  applyPerformanceFormatting(performanceSheet, netProfit, roi)
  
  console.log(`✅ Performance updated - ROI: ${roi.toFixed(2)}%`)
}

function updateDashboardSummary() {
  /**
   * Create executive summary dashboard
   */
  console.log('📊 Updating dashboard summary...')
  
  const sheet = getOrCreateSheet(CONFIG.SHEETS.DASHBOARD)
  sheet.clear()
  
  // Dashboard title
  sheet.getRange('A1').setValue('🏆 EQ12 SPORTS BETTING DASHBOARD')
  sheet.getRange('A1').setFontSize(16).setFontWeight('bold').setBackground('#1f4e79').setFontColor('#ffffff')
  sheet.getRange('A1:F1').merge()
  
  const timestamp = new Date().toLocaleString()
  sheet.getRange('A2').setValue(`Last Updated: ${timestamp}`)
  
  // Quick stats
  const stats = [
    ['📊 LIVE ODDS', getLiveOddsCount()],
    ['🔍 ARBITRAGE OPS', getArbitrageCount()],
    ['🏀 PLAYER PROPS', getPlayerPropsCount()],
    ['📈 TOTAL BETS', getTotalBets()],
    ['💰 NET PROFIT', getNetProfit()],
    ['📊 WIN RATE', getWinRate()]
  ]
  
  sheet.getRange(4, 1, stats.length, 2).setValues(stats)
  
  // Format dashboard
  sheet.getRange('A4:B9').setBackground('#f0f0f0')
  sheet.getRange('A4:A9').setFontWeight('bold')
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function fetchOddsData(sport, markets) {
  /**
   * Fetch odds data from The Odds API
   */
  const url = `${CONFIG.BASE_URL}/sports/${sport}/odds?apiKey=${CONFIG.API_KEY}&regions=${CONFIG.REGIONS}&markets=${markets}&oddsFormat=${CONFIG.ODDS_FORMAT}&dateFormat=${CONFIG.DATE_FORMAT}`
  
  try {
    const response = UrlFetchApp.fetch(url)
    const data = JSON.parse(response.getContentText())
    
    // Log API usage
    const remaining = response.getHeaders()['x-requests-remaining'] || 'Unknown'
    console.log(`📊 API Usage - Remaining: ${remaining}`)
    
    return data.slice(0, CONFIG.MAX_EVENTS) // Limit events
    
  } catch (error) {
    console.error('❌ Failed to fetch odds data:', error)
    throw new Error('Failed to fetch odds: ' + error.message)
  }
}

function fetchPlayerPropsData() {
  /**
   * Fetch player props data
   */
  const markets = 'player_points,player_rebounds,player_assists'
  
  // Try NBA first
  try {
    return fetchOddsData('basketball_nba', markets)
  } catch (error) {
    // Try NFL if NBA fails
    try {
      return fetchOddsData('americanfootball_nfl', 'player_pass_yds,player_pass_tds')
    } catch (error2) {
      return []
    }
  }
}

function detectArbitrageOpportunities(oddsData) {
  /**
   * Detect arbitrage opportunities in odds data
   */
  const opportunities = []
  
  oddsData.forEach(event => {
    ['h2h', 'spreads', 'totals'].forEach(marketType => {
      const marketData = {}
      
      // Collect all odds for this market
      event.bookmakers.forEach(bookmaker => {
        const market = bookmaker.markets.find(m => m.key === marketType)
        if (market) {
          market.outcomes.forEach(outcome => {
            const key = outcome.point ? `${outcome.name}_${outcome.point}` : outcome.name
            if (!marketData[key] || outcome.price > marketData[key].odds) {
              marketData[key] = {
                odds: outcome.price,
                bookmaker: bookmaker.title,
                outcome: outcome.name
              }
            }
          })
        }
      })
      
      // Check for arbitrage (simplified)
      const outcomes = Object.values(marketData)
      if (outcomes.length >= 2) {
        const arbitrageCheck = checkArbitrage(outcomes)
        if (arbitrageCheck.isArbitrage && arbitrageCheck.profit >= 0.5) {
          opportunities.push({
            homeTeam: event.home_team,
            awayTeam: event.away_team,
            sport: event.sport_title,
            market: marketType,
            profitPercent: arbitrageCheck.profit,
            totalStake: 1000, // Base stake
            expectedReturn: arbitrageCheck.expectedReturn,
            side1: outcomes[0],
            side2: outcomes[1]
          })
        }
      }
    })
  })
  
  return opportunities
}

function checkArbitrage(outcomes) {
  /**
   * Check if outcomes represent an arbitrage opportunity
   */
  if (outcomes.length < 2) return { isArbitrage: false, profit: 0 }
  
  // Calculate implied probabilities
  let totalImpliedProb = 0
  outcomes.forEach(outcome => {
    const odds = outcome.odds
    const impliedProb = CONFIG.ODDS_FORMAT === 'american' 
      ? (odds > 0 ? 100 / (odds + 100) : Math.abs(odds) / (Math.abs(odds) + 100))
      : 1 / odds
    totalImpliedProb += impliedProb
    
    // Add stake calculation
    outcome.stake = 1000 * (impliedProb / totalImpliedProb)
  })
  
  const profit = (1 - totalImpliedProb) * 100
  const isArbitrage = totalImpliedProb < 1
  
  return {
    isArbitrage,
    profit,
    expectedReturn: 1000 * (1 + profit / 100)
  }
}

function getOrCreateSheet(sheetName) {
  /**
   * Get existing sheet or create new one
   */
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet()
  let sheet = spreadsheet.getSheetByName(sheetName)
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet(sheetName)
  }
  
  return sheet
}

function formatDateTime(dateString) {
  /**
   * Format datetime for display
   */
  try {
    const date = new Date(dateString)
    return date.toLocaleString()
  } catch (error) {
    return dateString
  }
}

function formatOutcome(outcome, event) {
  /**
   * Format outcome name for display
   */
  if (outcome.point) {
    return `${outcome.name} ${outcome.point > 0 ? '+' : ''}${outcome.point}`
  }
  return outcome.name
}

function calculateImpliedProfitMargin(odds, format) {
  /**
   * Calculate bookmaker profit margin
   */
  try {
    const impliedProb = format === 'american' 
      ? (odds > 0 ? 100 / (odds + 100) : Math.abs(odds) / (Math.abs(odds) + 100))
      : 1 / odds
    return ((impliedProb - (1/2)) * 100).toFixed(1) // Assuming fair odds at 50%
  } catch (error) {
    return '0.0'
  }
}

// =============================================================================
// FORMATTING FUNCTIONS
// =============================================================================

function applyLiveOddsFormatting(sheet, dataRows) {
  /**
   * Apply conditional formatting to live odds
   */
  // Highlight best odds
  const valueRange = sheet.getRange(2, 12, dataRows, 1) // Value Indicator column
  const rule = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo('⭐ BEST')
    .setBackground('#FFD700')
    .setFontColor('#000000')
    .setRanges([valueRange])
    .build()
  
  sheet.setConditionalFormatRules([rule])
}

function applyArbitrageFormatting(sheet, dataRows) {
  /**
   * Apply conditional formatting to arbitrage opportunities
   */
  // Highlight high-value opportunities
  const statusRange = sheet.getRange(2, 16, dataRows, 1) // Status column
  const rule = SpreadsheetApp.newConditionalFormatRule()
    .whenTextEqualTo('🚨 HIGH VALUE')
    .setBackground('#FF6B6B')
    .setFontColor('#FFFFFF')
    .setRanges([statusRange])
    .build()
    
  sheet.setConditionalFormatRules([rule])
}

function applyPerformanceFormatting(sheet, netProfit, roi) {
  /**
   * Apply conditional formatting to performance metrics
   */
  // Color code profit/loss
  const profitCell = sheet.getRange(2, 7) // Net Profit column
  const roiCell = sheet.getRange(2, 8) // ROI column
  
  if (netProfit > 0) {
    profitCell.setBackground('#90EE90')
    roiCell.setBackground('#90EE90')
  } else if (netProfit < 0) {
    profitCell.setBackground('#FFB6C1')
    roiCell.setBackground('#FFB6C1')
  }
}

// =============================================================================
// DASHBOARD HELPER FUNCTIONS
// =============================================================================

function getLiveOddsCount() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.LIVE_ODDS)
    return sheet ? (sheet.getLastRow() - 1) : 0
  } catch (e) { return 0 }
}

function getArbitrageCount() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.ARBITRAGE)
    return sheet ? (sheet.getLastRow() - 1) : 0
  } catch (e) { return 0 }
}

function getPlayerPropsCount() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.PLAYER_PROPS)
    return sheet ? (sheet.getLastRow() - 1) : 0
  } catch (e) { return 0 }
}

function getTotalBets() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.BET_TRACKING)
    return sheet ? (sheet.getLastRow() - 1) : 0
  } catch (e) { return 0 }
}

function getNetProfit() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.PERFORMANCE)
    if (sheet && sheet.getLastRow() >= 2) {
      const profit = sheet.getRange(2, 7).getValue()
      return typeof profit === 'number' ? `$${profit.toFixed(2)}` : '$0.00'
    }
    return '$0.00'
  } catch (e) { return '$0.00' }
}

function getWinRate() {
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEETS.PERFORMANCE)
    if (sheet && sheet.getLastRow() >= 2) {
      const winRate = sheet.getRange(2, 4).getValue()
      return typeof winRate === 'number' ? `${winRate.toFixed(1)}%` : '0.0%'
    }
    return '0.0%'
  } catch (e) { return '0.0%' }
}

// =============================================================================
// TRIGGER SETUP FUNCTIONS
// =============================================================================

function setupAutomaticUpdates() {
  /**
   * Setup time-driven triggers for automatic updates
   * Run this once to enable automatic dashboard updates
   */
  // Delete existing triggers
  ScriptApp.getProjectTriggers().forEach(trigger => {
    if (trigger.getHandlerFunction() === 'updateEQ12Dashboard') {
      ScriptApp.deleteTrigger(trigger)
    }
  })
  
  // Create new trigger for every 15 minutes
  ScriptApp.newTrigger('updateEQ12Dashboard')
    .timeBased()
    .everyMinutes(15)
    .create()
    
  console.log('✅ Automatic updates enabled (every 15 minutes)')
}

function onOpen() {
  /**
   * Add custom menu when spreadsheet opens
   */
  const ui = SpreadsheetApp.getUi()
  ui.createMenu('🏆 EQ12 Betting')
    .addItem('🔄 Update Dashboard', 'updateEQ12Dashboard')
    .addItem('📊 Update Live Odds', 'updateLiveOdds') 
    .addItem('🔍 Scan Arbitrage', 'updateArbitrageOpportunities')
    .addItem('🏀 Update Player Props', 'updatePlayerProps')
    .addItem('📈 Update Performance', 'updatePerformanceAnalytics')
    .addSeparator()
    .addItem('⚡ Setup Auto Updates', 'setupAutomaticUpdates')
    .addToUi()
}