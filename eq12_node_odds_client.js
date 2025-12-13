// EQ12 Enhanced Node.js Odds API Client
// Advanced Node.js integration for The Odds API with EQ12 platform capabilities
// Author: EQ12 Platform
// Version: 1.0.0

import axios from 'axios';
import fs from 'fs';
import path from 'path';

class EQ12NodeOddsClient {
    constructor(apiKey = null) {
        this.apiKey = apiKey || process.env.ODDS_API_KEY || process.argv[2];
        this.baseUrl = 'https://api.the-odds-api.com/v4';
        this.logDir = 'C:/EQ12/logs';
        this.dataDir = 'C:/EQ12/data';

        // Ensure directories exist
        this.ensureDirectories();

        // Request tracking
        this.requestCount = 0;
        this.remainingRequests = null;

        console.log('🏆 EQ12 Enhanced Node.js Odds API Client initialized');

        if (!this.apiKey || this.apiKey === 'YOUR_API_KEY') {
            console.log('⚠️ API key required. Set ODDS_API_KEY environment variable or pass as argument');
        }
    }

    ensureDirectories() {
        try {
            if (!fs.existsSync(this.logDir)) {
                fs.mkdirSync(this.logDir, { recursive: true });
            }
            if (!fs.existsSync(this.dataDir)) {
                fs.mkdirSync(this.dataDir, { recursive: true });
            }
        } catch (error) {
            console.log('⚠️ Could not create directories:', error.message);
        }
    }

    log(message, level = 'INFO') {
        const timestamp = new Date().toISOString();
        const logMessage = `${timestamp} - ${level} - ${message}`;
        console.log(logMessage);

        try {
            const logFile = path.join(this.logDir, 'eq12_node_odds.log');
            fs.appendFileSync(logFile, logMessage + '\\n');
        } catch (error) {
            console.log('⚠️ Could not write to log file:', error.message);
        }
    }

    async makeRequest(endpoint, params = {}) {
        if (!this.apiKey || this.apiKey === 'YOUR_API_KEY') {
            throw new Error('Valid API key required');
        }

        try {
            this.requestCount++;
            const response = await axios.get(`${this.baseUrl}${endpoint}`, {
                params: { apiKey: this.apiKey, ...params },
                timeout: 30000
            });

            // Track usage
            this.remainingRequests = response.headers['x-requests-remaining'];
            const usedRequests = response.headers['x-requests-used'];

            this.log(`API Request: ${endpoint} | Used: ${usedRequests} | Remaining: ${this.remainingRequests}`);

            return response.data;
        } catch (error) {
            this.log(`API Error: ${error.response?.status} - ${error.response?.data || error.message}`, 'ERROR');
            throw error;
        }
    }

    async getSports() {
        this.log('🏈 Fetching available sports...');
        const sports = await this.makeRequest('/sports');

        // Save to file
        this.saveToFile('sports', sports);

        console.log(`📊 Found ${sports.length} available sports`);
        sports.forEach(sport => {
            console.log(`  - ${sport.title} (${sport.key})`);
        });

        return sports;
    }

    async getOdds(sportKey = 'upcoming', options = {}) {
        const defaultOptions = {
            regions: 'us',
            markets: 'h2h',
            oddsFormat: 'american',
            dateFormat: 'iso'
        };

        const params = { ...defaultOptions, ...options };

        this.log(`🎯 Fetching odds for ${sportKey} with markets: ${params.markets}`);

        const odds = await this.makeRequest(`/sports/${sportKey}/odds`, params);

        // Save to file with timestamp
        const filename = `odds_${sportKey}_${new Date().toISOString().replace(/[:.]/g, '-')}`;
        this.saveToFile(filename, odds);

        console.log(`📊 Found ${odds.length} events with odds`);

        return odds;
    }

    async findArbitrageOpportunities(sportKey = 'upcoming') {
        this.log(`🔍 Scanning for arbitrage opportunities in ${sportKey}...`);

        const odds = await this.getOdds(sportKey, {
            regions: 'us,uk,eu',
            markets: 'h2h',
            oddsFormat: 'american'
        });

        const arbitrages = [];

        odds.forEach(event => {
            if (event.bookmakers && event.bookmakers.length >= 2) {
                const arb = this.calculateArbitrage(event);
                if (arb && arb.profit > 0) {
                    arbitrages.push(arb);
                }
            }
        });

        // Sort by profit margin
        arbitrages.sort((a, b) => b.profit - a.profit);

        this.log(`💰 Found ${arbitrages.length} arbitrage opportunities`);

        arbitrages.slice(0, 10).forEach((arb, index) => {
            console.log(`${index + 1}. ${arb.event} | Profit: ${arb.profit.toFixed(2)}% | ${arb.description}`);
        });

        // Save arbitrage opportunities
        this.saveToFile('arbitrage_opportunities', arbitrages);

        return arbitrages;
    }

    calculateArbitrage(event) {
        try {
            const bestOdds = {};

            // Find best odds for each outcome
            event.bookmakers.forEach(bookmaker => {
                bookmaker.markets.forEach(market => {
                    if (market.key === 'h2h') {
                        market.outcomes.forEach(outcome => {
                            const impliedProb = this.americanToImpliedProbability(outcome.price);

                            if (!bestOdds[outcome.name] || impliedProb < bestOdds[outcome.name].impliedProb) {
                                bestOdds[outcome.name] = {
                                    price: outcome.price,
                                    impliedProb: impliedProb,
                                    bookmaker: bookmaker.title
                                };
                            }
                        });
                    }
                });
            });

            // Calculate total implied probability
            const totalImpliedProb = Object.values(bestOdds).reduce((sum, odd) => sum + odd.impliedProb, 0);

            if (totalImpliedProb < 1.0) {
                const profitMargin = ((1 / totalImpliedProb) - 1) * 100;

                return {
                    event: `${event.home_team} vs ${event.away_team}`,
                    sport: event.sport_title,
                    commence_time: event.commence_time,
                    profit: profitMargin,
                    bestOdds: bestOdds,
                    totalImpliedProb: totalImpliedProb,
                    description: `${Object.keys(bestOdds).length} outcomes across multiple bookmakers`
                };
            }

            return null;
        } catch (error) {
            this.log(`Error calculating arbitrage for ${event.home_team} vs ${event.away_team}: ${error.message}`, 'ERROR');
            return null;
        }
    }

    americanToImpliedProbability(americanOdds) {
        if (americanOdds > 0) {
            return 100 / (americanOdds + 100);
        } else {
            return Math.abs(americanOdds) / (Math.abs(americanOdds) + 100);
        }
    }

    async getNFLAnalysis() {
        this.log('🏈 Performing NFL analysis...');

        const nflOdds = await this.getOdds('americanfootball_nfl', {
            regions: 'us',
            markets: 'h2h,spreads,totals',
            oddsFormat: 'american'
        });

        const analysis = {
            totalGames: nflOdds.length,
            upcomingGames: nflOdds.filter(game => new Date(game.commence_time) > new Date()).length,
            averageTotal: 0,
            highestFavorite: null,
            biggestSpread: 0
        };

        // Analyze each game
        nflOdds.forEach(game => {
            game.bookmakers.forEach(bookmaker => {
                bookmaker.markets.forEach(market => {
                    if (market.key === 'totals') {
                        const total = market.outcomes[0]?.point;
                        if (total && total > analysis.averageTotal) {
                            analysis.averageTotal = total;
                        }
                    }

                    if (market.key === 'spreads') {
                        market.outcomes.forEach(outcome => {
                            if (Math.abs(outcome.point) > analysis.biggestSpread) {
                                analysis.biggestSpread = Math.abs(outcome.point);
                                analysis.biggestSpreadGame = `${game.home_team} vs ${game.away_team}`;
                            }
                        });
                    }
                });
            });
        });

        console.log('🏈 NFL Analysis Results:');
        console.log(`  📊 Total Games: ${analysis.totalGames}`);
        console.log(`  ⏰ Upcoming Games: ${analysis.upcomingGames}`);
        console.log(`  📈 Biggest Spread: ${analysis.biggestSpread} (${analysis.biggestSpreadGame})`);

        this.saveToFile('nfl_analysis', analysis);
        return analysis;
    }

    async getPlayerProps(sportKey = 'americanfootball_nfl') {
        this.log(`🎯 Fetching player props for ${sportKey}...`);

        try {
            const props = await this.makeRequest(`/sports/${sportKey}/odds`, {
                regions: 'us',
                markets: 'player_pass_tds,player_pass_yds,player_rush_yds,player_receptions',
                oddsFormat: 'american'
            });

            console.log(`🎲 Found ${props.length} events with player props`);

            this.saveToFile('player_props', props);
            return props;
        } catch (error) {
            this.log(`Player props not available for ${sportKey}: ${error.message}`, 'WARNING');
            return [];
        }
    }

    saveToFile(filename, data) {
        try {
            const filepath = path.join(this.dataDir, `${filename}.json`);
            fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
            this.log(`💾 Data saved to ${filepath}`);
        } catch (error) {
            this.log(`Error saving file: ${error.message}`, 'ERROR');
        }
    }

    async getUsageStats() {
        if (this.remainingRequests !== null) {
            console.log(`📊 API Usage Statistics:`);
            console.log(`  🔢 Requests made this session: ${this.requestCount}`);
            console.log(`  ⏳ Remaining requests: ${this.remainingRequests}`);

            return {
                sessionRequests: this.requestCount,
                remainingRequests: parseInt(this.remainingRequests)
            };
        }

        return null;
    }

    // Demo method that showcases all capabilities
    async runDemo() {
        console.log('🚀 EQ12 Node.js Odds API Demo Starting...');
        console.log('====================================');

        try {
            // Get available sports
            await this.getSports();
            console.log('\\n');

            // Get NFL odds and analysis
            await this.getNFLAnalysis();
            console.log('\\n');

            // Find arbitrage opportunities
            await this.findArbitrageOpportunities('americanfootball_nfl');
            console.log('\\n');

            // Get player props
            await this.getPlayerProps();
            console.log('\\n');

            // Show usage stats
            await this.getUsageStats();

            console.log('\\n🎉 EQ12 Node.js Demo Complete!');

        } catch (error) {
            console.log(`❌ Demo error: ${error.message}`);
        }
    }
}

// Export for use as module
export default EQ12NodeOddsClient;

// If run directly, execute demo
if (import.meta.url === `file://${process.argv[1]}`) {
    const client = new EQ12NodeOddsClient();
    client.runDemo().catch(console.error);
}
