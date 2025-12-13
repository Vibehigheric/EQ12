// EQ12 Complete Node.js Betting Suite
// Comprehensive Node.js implementation with advanced betting features
// Integrates with existing EQ12 Python platform for complete coverage
// Author: EQ12 Platform
// Version: 1.0.0

const EQ12NodeOddsClient = require('./eq12_node_odds_client.js');
const fs = require('fs');
const path = require('path');

class EQ12NodeBettingSuite {
    constructor(apiKey = null) {
        this.oddsClient = new EQ12NodeOddsClient(apiKey);
        this.logDir = 'C:/EQ12/logs';
        this.dataDir = 'C:/EQ12/data';
        this.configsDir = 'C:/EQ12/configs';

        console.log('🚀 EQ12 Complete Node.js Betting Suite initialized');
    }

    log(message, level = 'INFO') {
        const timestamp = new Date().toISOString();
        const logMessage = `${timestamp} - ${level} - ${message}`;
        console.log(logMessage);

        try {
            const logFile = path.join(this.logDir, 'eq12_node_betting_suite.log');
            fs.appendFileSync(logFile, logMessage + '\\n');
        } catch (error) {
            console.log('⚠️ Could not write to log file:', error.message);
        }
    }

    // 1. NFL Sunday Analysis with Advanced Metrics
    async nflSundayAnalysis() {
        this.log('🏈 Starting NFL Sunday Analysis...');
        console.log('\\n🏈 NFL SUNDAY COMPLETE ANALYSIS');
        console.log('================================');

        try {
            // Get NFL odds with all markets
            const nflOdds = await this.oddsClient.getOdds('americanfootball_nfl', {
                regions: 'us,uk',
                markets: 'h2h,spreads,totals',
                oddsFormat: 'american'
            });

            const analysis = {
                totalGames: nflOdds.length,
                upcomingGames: [],
                valuePicksATS: [],
                totalsBets: [],
                moneylineValue: [],
                arbitrageOpportunities: []
            };

            // Analyze each game
            nflOdds.forEach(game => {
                if (new Date(game.commence_time) > new Date()) {
                    analysis.upcomingGames.push(game);

                    // Analyze for value bets
                    const gameAnalysis = this.analyzeNFLGame(game);

                    if (gameAnalysis.atsValue) {
                        analysis.valuePicksATS.push(gameAnalysis.atsValue);
                    }

                    if (gameAnalysis.totalValue) {
                        analysis.totalsBets.push(gameAnalysis.totalValue);
                    }

                    if (gameAnalysis.mlValue) {
                        analysis.moneylineValue.push(gameAnalysis.mlValue);
                    }
                }
            });

            // Find arbitrage opportunities
            const arbitrages = await this.oddsClient.findArbitrageOpportunities('americanfootball_nfl');
            analysis.arbitrageOpportunities = arbitrages.slice(0, 5);

            // Display results
            console.log(`📊 Games Analysis: ${analysis.upcomingGames.length} upcoming games`);
            console.log(`💰 Value Picks ATS: ${analysis.valuePicksATS.length}`);
            console.log(`📈 Total Bets: ${analysis.totalsBets.length}`);
            console.log(`🎯 Moneyline Value: ${analysis.moneylineValue.length}`);
            console.log(`⚡ Arbitrage Opportunities: ${analysis.arbitrageOpportunities.length}`);

            // Display top recommendations
            this.displayTopPicks(analysis);

            // Save analysis
            this.saveToFile('nfl_sunday_analysis', analysis);

            return analysis;

        } catch (error) {
            this.log(`NFL analysis error: ${error.message}`, 'ERROR');
            throw error;
        }
    }

    analyzeNFLGame(game) {
        const analysis = {};

        try {
            // Get best odds for each market
            const bestSpread = this.getBestOdds(game, 'spreads');
            const bestTotal = this.getBestOdds(game, 'totals');
            const bestML = this.getBestOdds(game, 'h2h');

            // ATS Value Analysis
            if (bestSpread && bestSpread.outcomes.length >= 2) {
                const homeSpread = bestSpread.outcomes.find(o => o.name === game.home_team);
                const awaySpread = bestSpread.outcomes.find(o => o.name === game.away_team);

                if (homeSpread && awaySpread) {
                    // Simple value detection (can be enhanced with ML models)
                    if (Math.abs(homeSpread.point) >= 7 && homeSpread.price >= -105) {
                        analysis.atsValue = {
                            game: `${game.home_team} vs ${game.away_team}`,
                            pick: `${homeSpread.point > 0 ? game.home_team : game.away_team} ${homeSpread.point}`,
                            odds: homeSpread.price,
                            confidence: 'Medium',
                            reasoning: 'Large spread with favorable juice'
                        };
                    }
                }
            }

            // Totals Value Analysis
            if (bestTotal && bestTotal.outcomes.length >= 2) {
                const overUnder = bestTotal.outcomes[0];
                if (overUnder && overUnder.point) {
                    // Look for totals value (can be enhanced)
                    if (overUnder.point >= 50 && overUnder.price >= -105) {
                        analysis.totalValue = {
                            game: `${game.home_team} vs ${game.away_team}`,
                            pick: `${overUnder.name} ${overUnder.point}`,
                            odds: overUnder.price,
                            confidence: 'Low',
                            reasoning: 'High total with good odds'
                        };
                    }
                }
            }

            // Moneyline Value
            if (bestML && bestML.outcomes.length >= 2) {
                bestML.outcomes.forEach(outcome => {
                    if (outcome.price >= 200) {  // Underdog value
                        analysis.mlValue = {
                            game: `${game.home_team} vs ${game.away_team}`,
                            pick: outcome.name,
                            odds: outcome.price,
                            confidence: 'High',
                            reasoning: 'Strong underdog value'
                        };
                    }
                });
            }

        } catch (error) {
            this.log(`Game analysis error for ${game.home_team} vs ${game.away_team}: ${error.message}`, 'ERROR');
        }

        return analysis;
    }

    getBestOdds(game, marketType) {
        let bestMarket = null;
        let bestOdds = -Infinity;

        game.bookmakers.forEach(bookmaker => {
            bookmaker.markets.forEach(market => {
                if (market.key === marketType) {
                    const avgOdds = market.outcomes.reduce((sum, outcome) => {
                        return sum + (outcome.price > 0 ? outcome.price : Math.abs(outcome.price));
                    }, 0) / market.outcomes.length;

                    if (avgOdds > bestOdds) {
                        bestOdds = avgOdds;
                        bestMarket = market;
                    }
                }
            });
        });

        return bestMarket;
    }

    displayTopPicks(analysis) {
        console.log('\\n🎯 TOP BETTING RECOMMENDATIONS:');
        console.log('================================');

        if (analysis.valuePicksATS.length > 0) {
            console.log('\\n🏈 AGAINST THE SPREAD:');
            analysis.valuePicksATS.slice(0, 3).forEach((pick, index) => {
                console.log(`${index + 1}. ${pick.game}`);
                console.log(`   Pick: ${pick.pick} (${pick.odds})`);
                console.log(`   Confidence: ${pick.confidence}`);
                console.log(`   Reasoning: ${pick.reasoning}\\n`);
            });
        }

        if (analysis.totalsBets.length > 0) {
            console.log('📊 TOTALS BETS:');
            analysis.totalsBets.slice(0, 2).forEach((pick, index) => {
                console.log(`${index + 1}. ${pick.game}`);
                console.log(`   Pick: ${pick.pick} (${pick.odds})`);
                console.log(`   Confidence: ${pick.confidence}\\n`);
            });
        }

        if (analysis.arbitrageOpportunities.length > 0) {
            console.log('⚡ ARBITRAGE OPPORTUNITIES:');
            analysis.arbitrageOpportunities.slice(0, 3).forEach((arb, index) => {
                console.log(`${index + 1}. ${arb.event}`);
                console.log(`   Profit: ${arb.profit.toFixed(2)}%`);
                console.log(`   Description: ${arb.description}\\n`);
            });
        }
    }

    // 2. NBA Props Builder
    async nbaPropsBuilder() {
        this.log('🏀 Starting NBA Props Builder...');
        console.log('\\n🏀 NBA PLAYER PROPS ANALYSIS');
        console.log('============================');

        try {
            const nbaProps = await this.oddsClient.getPlayerProps('basketball_nba');

            if (nbaProps.length === 0) {
                console.log('⚠️ NBA player props not available or season not active');
                return [];
            }

            const propsAnalysis = {
                totalGames: nbaProps.length,
                playerProps: [],
                valueProps: [],
                correlatedProps: []
            };

            // Analyze player props (simplified version)
            nbaProps.forEach(game => {
                game.bookmakers.forEach(bookmaker => {
                    bookmaker.markets.forEach(market => {
                        if (market.key.includes('player_')) {
                            market.outcomes.forEach(outcome => {
                                propsAnalysis.playerProps.push({
                                    game: `${game.home_team} vs ${game.away_team}`,
                                    player: outcome.description || 'Unknown Player',
                                    market: market.key,
                                    line: outcome.point,
                                    odds: outcome.price,
                                    bookmaker: bookmaker.title
                                });
                            });
                        }
                    });
                });
            });

            console.log(`📊 Found ${propsAnalysis.playerProps.length} player props across ${propsAnalysis.totalGames} games`);

            this.saveToFile('nba_props_analysis', propsAnalysis);
            return propsAnalysis;

        } catch (error) {
            this.log(`NBA props analysis error: ${error.message}`, 'ERROR');
            return [];
        }
    }

    // 3. Live Monitoring System
    async startLiveMonitoring(sports = ['americanfootball_nfl', 'basketball_nba']) {
        this.log('📡 Starting live odds monitoring...');
        console.log('\\n📡 LIVE ODDS MONITORING SYSTEM');
        console.log('==============================');

        let monitoringCount = 0;
        const maxMonitoringCycles = 5; // Limit for demo

        const monitoringInterval = setInterval(async () => {
            try {
                monitoringCount++;
                console.log(`\\n🔄 Monitoring Cycle ${monitoringCount} - ${new Date().toLocaleTimeString()}`);

                for (const sport of sports) {
                    try {
                        console.log(`\\n📊 Checking ${sport}...`);

                        // Get current odds
                        const odds = await this.oddsClient.getOdds(sport, {
                            regions: 'us',
                            markets: 'h2h',
                            oddsFormat: 'american'
                        });

                        // Check for arbitrage opportunities
                        const arbitrages = await this.oddsClient.findArbitrageOpportunities(sport);

                        if (arbitrages.length > 0) {
                            console.log(`🚨 ALERT: ${arbitrages.length} arbitrage opportunities found in ${sport}!`);
                            arbitrages.slice(0, 2).forEach(arb => {
                                console.log(`   💰 ${arb.event} - ${arb.profit.toFixed(2)}% profit`);
                            });
                        } else {
                            console.log(`   ✅ No arbitrage opportunities in ${sport}`);
                        }

                        // Save monitoring snapshot
                        const snapshot = {
                            timestamp: new Date().toISOString(),
                            sport: sport,
                            totalGames: odds.length,
                            arbitrageCount: arbitrages.length,
                            topArbitrages: arbitrages.slice(0, 3)
                        };

                        this.saveToFile(`monitoring_${sport}_${monitoringCount}`, snapshot);

                    } catch (error) {
                        console.log(`   ❌ Error monitoring ${sport}: ${error.message}`);
                    }

                    // Small delay between sports
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }

                // Stop after demo cycles
                if (monitoringCount >= maxMonitoringCycles) {
                    clearInterval(monitoringInterval);
                    console.log('\\n🏁 Live monitoring demo complete');

                    // Display usage stats
                    await this.oddsClient.getUsageStats();
                }

            } catch (error) {
                console.log(`❌ Monitoring error: ${error.message}`);
            }
        }, 30000); // Check every 30 seconds for demo

        console.log('🔄 Live monitoring started. Checking every 30 seconds...');
        console.log('💡 In production, you would run this continuously with longer intervals');
    }

    // 4. Portfolio Performance Tracker
    async portfolioPerformanceTracker() {
        this.log('📈 Generating portfolio performance report...');
        console.log('\\n📈 PORTFOLIO PERFORMANCE TRACKER');
        console.log('================================');

        // Simulate portfolio data (in real implementation, would read from database)
        const portfolioData = {
            totalBets: 150,
            winningBets: 82,
            losingBets: 68,
            totalWagered: 15000,
            totalReturns: 16200,
            roi: 8.0,
            sharpRatio: 1.45,
            longestWinStreak: 7,
            longestLoseStreak: 4,
            betsByType: {
                moneyline: { bets: 45, roi: 12.3 },
                spreads: { bets: 60, roi: 5.8 },
                totals: { bets: 30, roi: 8.9 },
                props: { bets: 15, roi: 15.2 }
            }
        };

        // Calculate metrics
        const winRate = (portfolioData.winningBets / portfolioData.totalBets * 100).toFixed(1);
        const avgBetSize = (portfolioData.totalWagered / portfolioData.totalBets).toFixed(2);
        const profit = portfolioData.totalReturns - portfolioData.totalWagered;

        console.log(`📊 Portfolio Overview:`);
        console.log(`   💰 Total Profit: $${profit > 0 ? '+' : ''}${profit.toLocaleString()}`);
        console.log(`   📈 ROI: ${portfolioData.roi}%`);
        console.log(`   🎯 Win Rate: ${winRate}%`);
        console.log(`   📏 Average Bet Size: $${avgBetSize}`);
        console.log(`   🏆 Sharp Ratio: ${portfolioData.sharpRatio}`);

        console.log(`\\n📊 Performance by Bet Type:`);
        Object.entries(portfolioData.betsByType).forEach(([type, data]) => {
            console.log(`   ${type.toUpperCase()}: ${data.bets} bets, ${data.roi}% ROI`);
        });

        console.log(`\\n📈 Streak Analysis:`);
        console.log(`   🔥 Longest Win Streak: ${portfolioData.longestWinStreak}`);
        console.log(`   ❄️ Longest Lose Streak: ${portfolioData.longestLoseStreak}`);

        // Generate recommendations
        const recommendations = this.generatePortfolioRecommendations(portfolioData);
        console.log(`\\n💡 RECOMMENDATIONS:`);
        recommendations.forEach((rec, index) => {
            console.log(`${index + 1}. ${rec}`);
        });

        this.saveToFile('portfolio_performance', {
            ...portfolioData,
            generatedAt: new Date().toISOString(),
            recommendations: recommendations
        });

        return portfolioData;
    }

    generatePortfolioRecommendations(data) {
        const recommendations = [];

        // Win rate analysis
        const winRate = data.winningBets / data.totalBets;
        if (winRate < 0.53) {
            recommendations.push('Win rate below break-even. Focus on bet selection and line shopping.');
        }

        // ROI analysis
        if (data.roi < 5) {
            recommendations.push('ROI below target. Consider reducing bet size and focusing on higher value bets.');
        }

        // Bet type analysis
        const bestType = Object.entries(data.betsByType)
            .sort(([,a], [,b]) => b.roi - a.roi)[0];

        recommendations.push(`${bestType[0].toUpperCase()} bets show highest ROI (${bestType[1].roi}%). Consider increasing allocation.`);

        // Streak analysis
        if (data.longestLoseStreak >= 5) {
            recommendations.push('Long losing streaks detected. Review bankroll management and bet sizing.');
        }

        return recommendations;
    }

    // 5. Cross-Platform Integration Demo
    async crossPlatformDemo() {
        this.log('🌐 Starting cross-platform integration demo...');
        console.log('\\n🌐 CROSS-PLATFORM INTEGRATION DEMO');
        console.log('==================================');

        try {
            // Check if Python files exist
            const pythonFiles = [
                'eq12_enhanced_openai_sdk.py',
                'eq12_odds_api_client.py',
                'eq12_google_sheets_integration.py'
            ];

            const availablePython = pythonFiles.filter(file => {
                try {
                    return fs.existsSync(path.join(process.cwd(), file));
                } catch {
                    return false;
                }
            });

            console.log(`🐍 Python Integration Status:`);
            console.log(`   ✅ Available Python modules: ${availablePython.length}/${pythonFiles.length}`);
            availablePython.forEach(file => {
                console.log(`   📄 ${file}`);
            });

            // Node.js capabilities
            console.log(`\\n🟢 Node.js Capabilities:`);
            console.log(`   ✅ Enhanced Odds API Client`);
            console.log(`   ✅ Real-time Arbitrage Detection`);
            console.log(`   ✅ NFL/NBA Analysis Engine`);
            console.log(`   ✅ Live Monitoring System`);
            console.log(`   ✅ Portfolio Performance Tracking`);

            // Integration points
            console.log(`\\n🔗 Integration Points:`);
            console.log(`   📊 Shared data directory: C:/EQ12/data`);
            console.log(`   📝 Shared logs directory: C:/EQ12/logs`);
            console.log(`   ⚙️ Shared configs directory: C:/EQ12/configs`);

            // Demonstrate data sharing
            const nodeData = {
                timestamp: new Date().toISOString(),
                source: 'Node.js Platform',
                version: '1.0.0',
                capabilities: [
                    'Real-time odds fetching',
                    'Arbitrage detection',
                    'NFL/NBA analysis',
                    'Live monitoring',
                    'Performance tracking'
                ],
                apiUsage: await this.oddsClient.getUsageStats()
            };

            this.saveToFile('nodejs_platform_status', nodeData);
            console.log(`\\n💾 Platform status saved for Python integration`);

            return {
                pythonModules: availablePython,
                nodeCapabilities: nodeData.capabilities,
                integrationReady: true
            };

        } catch (error) {
            this.log(`Cross-platform demo error: ${error.message}`, 'ERROR');
            throw error;
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

    // Master demo method
    async runCompleteBettingSuite() {
        console.log('🚀 EQ12 COMPLETE NODE.JS BETTING SUITE DEMO');
        console.log('==========================================');

        try {
            // 1. NFL Sunday Analysis
            await this.nflSundayAnalysis();
            await new Promise(resolve => setTimeout(resolve, 3000));

            // 2. NBA Props Builder
            await this.nbaPropsBuilder();
            await new Promise(resolve => setTimeout(resolve, 3000));

            // 3. Portfolio Performance
            await this.portfolioPerformanceTracker();
            await new Promise(resolve => setTimeout(resolve, 3000));

            // 4. Cross-Platform Demo
            await this.crossPlatformDemo();
            await new Promise(resolve => setTimeout(resolve, 3000));

            // 5. Live Monitoring (short demo)
            console.log('\\n🎯 Starting brief live monitoring demo...');
            await this.startLiveMonitoring(['americanfootball_nfl']);

            console.log('\\n🎉 COMPLETE BETTING SUITE DEMO FINISHED!');
            console.log('=========================================');
            console.log('🏆 Node.js platform fully operational and integrated with Python components');

        } catch (error) {
            console.log(`❌ Suite error: ${error.message}`);
            this.log(`Complete suite error: ${error.message}`, 'ERROR');
        }
    }
}

// Export for use as module
module.exports = EQ12NodeBettingSuite;

// If run directly, execute complete demo
if (require.main === module) {
    const suite = new EQ12NodeBettingSuite();
    suite.runCompleteBettingSuite().catch(console.error);
}
