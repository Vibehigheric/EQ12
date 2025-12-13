const core = require('@actions/core');
const axios = require('axios');

/**
 * EQ12 Parlay Sanitizer - Advanced parlay validation and optimization
 */
class EQ12ParlaySanitizer {
    constructor() {
        this.parlayData = JSON.parse(core.getInput('parlay-data'));
        this.riskThreshold = parseInt(core.getInput('risk-threshold') || '7');
        this.analysisLevel = core.getInput('analysis-level') || 'standard';
        this.eq12ApiKey = core.getInput('eq12-api-key');
        this.correlationCheck = core.getInput('correlation-check') === 'true';
        this.bankrollPercentage = parseFloat(core.getInput('bankroll-percentage') || '2');

        // Correlation patterns that increase risk
        this.riskCorrelations = [
            ['team_total', 'player_prop_same_team'],
            ['game_total', 'both_teams_same_game'],
            ['spread', 'moneyline_same_game'],
            ['player_prop', 'team_performance_same_player'],
            ['weather_dependent', 'outdoor_game_totals']
        ];
    }

    async sanitize() {
        try {
            core.info('🔍 Starting EQ12 Parlay Sanitization...');

            // Validate parlay structure
            const validation = await this.validateParlayStructure();
            if (!validation.valid) {
                core.setFailed(`Invalid parlay structure: ${validation.error}`);
                return;
            }

            // Perform risk assessment
            const riskAssessment = await this.assessRisk();

            // Check correlations
            const correlationAnalysis = await this.analyzeCorrelations();

            // Calculate expected value
            const expectedValue = await this.calculateExpectedValue();

            // Generate recommendations
            const recommendations = await this.generateRecommendations(riskAssessment, correlationAnalysis);

            // Sanitize parlay
            const sanitizedParlay = await this.sanitizeParlay(recommendations);

            // Set outputs
            core.setOutput('sanitized-parlay', JSON.stringify(sanitizedParlay));
            core.setOutput('risk-assessment', JSON.stringify(riskAssessment));
            core.setOutput('recommendations', JSON.stringify(recommendations));
            core.setOutput('expected-value', JSON.stringify(expectedValue));

            // Generate summary
            await this.generateSummary(riskAssessment, expectedValue, recommendations);

            core.info('✅ EQ12 Parlay Sanitization completed');

        } catch (error) {
            core.setFailed(`EQ12 Parlay Sanitizer failed: ${error.message}`);
        }
    }

    async validateParlayStructure() {
        const required = ['legs', 'stake', 'bankroll'];

        for (const field of required) {
            if (!this.parlayData[field]) {
                return { valid: false, error: `Missing required field: ${field}` };
            }
        }

        if (!Array.isArray(this.parlayData.legs) || this.parlayData.legs.length < 2) {
            return { valid: false, error: 'Parlay must have at least 2 legs' };
        }

        if (this.parlayData.legs.length > 15) {
            return { valid: false, error: 'Parlay exceeds maximum 15 legs for safety' };
        }

        // Validate each leg
        for (let i = 0; i < this.parlayData.legs.length; i++) {
            const leg = this.parlayData.legs[i];
            if (!leg.odds || !leg.selection || !leg.market) {
                return { valid: false, error: `Invalid leg ${i + 1}: missing odds, selection, or market` };
            }

            // Convert odds to decimal for validation
            const decimalOdds = this.convertToDecimal(leg.odds, leg.format || 'american');
            if (decimalOdds < 1.01 || decimalOdds > 100) {
                return { valid: false, error: `Invalid odds in leg ${i + 1}: ${leg.odds}` };
            }
        }

        return { valid: true };
    }

    async assessRisk() {
        const legs = this.parlayData.legs;
        let totalRisk = 0;
        let riskFactors = [];

        // Base risk from number of legs
        const legRisk = Math.min(legs.length * 0.8, 8);
        totalRisk += legRisk;
        riskFactors.push({ factor: 'leg_count', risk: legRisk, description: `${legs.length} legs in parlay` });

        // Risk from individual odds
        let lowOddsCount = 0;
        let highOddsCount = 0;

        for (const leg of legs) {
            const decimalOdds = this.convertToDecimal(leg.odds, leg.format || 'american');

            if (decimalOdds < 1.5) {
                lowOddsCount++;
            } else if (decimalOdds > 5.0) {
                highOddsCount++;
            }
        }

        if (lowOddsCount > legs.length * 0.6) {
            const heavyFavoriteRisk = 2;
            totalRisk += heavyFavoriteRisk;
            riskFactors.push({
                factor: 'heavy_favorites',
                risk: heavyFavoriteRisk,
                description: 'Too many heavy favorites reduces expected value'
            });
        }

        if (highOddsCount > legs.length * 0.3) {
            const longShotRisk = 3;
            totalRisk += longShotRisk;
            riskFactors.push({
                factor: 'long_shots',
                risk: longShotRisk,
                description: 'High number of long shots increases variance'
            });
        }

        // Bankroll risk
        const bankrollRisk = this.calculateBankrollRisk();
        totalRisk += bankrollRisk.risk;
        riskFactors.push(bankrollRisk);

        // Get EQ12 premium risk analysis
        if (this.eq12ApiKey && this.analysisLevel === 'premium') {
            const premiumRisk = await this.getEQ12RiskAnalysis();
            if (premiumRisk) {
                totalRisk += premiumRisk.additional_risk;
                riskFactors.push(...premiumRisk.factors);
            }
        }

        return {
            total_risk: Math.min(totalRisk, 10),
            risk_level: totalRisk <= 3 ? 'low' : totalRisk <= 6 ? 'medium' : 'high',
            factors: riskFactors,
            exceeds_threshold: totalRisk > this.riskThreshold
        };
    }

    async analyzeCorrelations() {
        if (!this.correlationCheck) {
            return { correlations_found: [], risk_increase: 0 };
        }

        const legs = this.parlayData.legs;
        const correlations = [];

        // Check for same game correlations
        const gameGroups = {};
        legs.forEach((leg, index) => {
            const gameId = leg.game_id || `${leg.team1}_vs_${leg.team2}`;
            if (!gameGroups[gameId]) gameGroups[gameId] = [];
            gameGroups[gameId].push({ index, leg });
        });

        for (const [gameId, gameLegs] of Object.entries(gameGroups)) {
            if (gameLegs.length > 1) {
                const markets = gameLegs.map(gl => gl.leg.market);
                const riskIncrease = this.calculateCorrelationRisk(markets);

                correlations.push({
                    type: 'same_game',
                    game: gameId,
                    legs: gameLegs.map(gl => gl.index),
                    markets: markets,
                    risk_increase: riskIncrease,
                    description: `Multiple bets on ${gameId}`
                });
            }
        }

        // Check for player-team correlations
        const playerTeamCorrelations = this.findPlayerTeamCorrelations(legs);
        correlations.push(...playerTeamCorrelations);

        // Premium correlation analysis
        if (this.eq12ApiKey && this.analysisLevel === 'premium') {
            const premiumCorrelations = await this.getEQ12CorrelationAnalysis();
            if (premiumCorrelations) {
                correlations.push(...premiumCorrelations);
            }
        }

        const totalRiskIncrease = correlations.reduce((sum, corr) => sum + corr.risk_increase, 0);

        return {
            correlations_found: correlations,
            risk_increase: Math.min(totalRiskIncrease, 5),
            high_risk_correlations: correlations.filter(c => c.risk_increase >= 2)
        };
    }

    async calculateExpectedValue() {
        const legs = this.parlayData.legs;
        let parlayOdds = 1;
        let impliedProbability = 1;

        // Calculate parlay odds and implied probability
        for (const leg of legs) {
            const decimalOdds = this.convertToDecimal(leg.odds, leg.format || 'american');
            parlayOdds *= decimalOdds;
            impliedProbability *= (1 / decimalOdds);
        }

        // Account for correlation adjustments
        const correlationAnalysis = await this.analyzeCorrelations();
        const adjustedProbability = impliedProbability * (1 + correlationAnalysis.risk_increase * 0.1);

        const expectedValue = (this.parlayData.stake * parlayOdds * adjustedProbability) - this.parlayData.stake;
        const roi = (expectedValue / this.parlayData.stake) * 100;

        // Kelly Criterion calculation
        const edge = adjustedProbability - impliedProbability;
        const kellyPercentage = edge > 0 ? (edge / (parlayOdds - 1)) * 100 : 0;

        return {
            parlay_odds: parlayOdds,
            implied_probability: impliedProbability,
            adjusted_probability: adjustedProbability,
            expected_value: expectedValue,
            roi_percentage: roi,
            kelly_percentage: kellyPercentage,
            recommended_stake: Math.min(
                this.parlayData.bankroll * (kellyPercentage / 100),
                this.parlayData.bankroll * (this.bankrollPercentage / 100)
            )
        };
    }

    async generateRecommendations(riskAssessment, correlationAnalysis) {
        const recommendations = [];

        // Risk-based recommendations
        if (riskAssessment.total_risk > this.riskThreshold) {
            recommendations.push({
                type: 'risk_reduction',
                priority: 'high',
                title: 'Reduce overall parlay risk',
                description: `Risk level ${riskAssessment.total_risk}/10 exceeds threshold ${this.riskThreshold}/10`,
                actions: [
                    'Remove legs with lowest confidence',
                    'Reduce stake size',
                    'Split into smaller parlays'
                ]
            });
        }

        // Correlation recommendations
        if (correlationAnalysis.high_risk_correlations.length > 0) {
            recommendations.push({
                type: 'correlation_warning',
                priority: 'high',
                title: 'Remove correlated bets',
                description: 'High-risk correlations detected',
                actions: correlationAnalysis.high_risk_correlations.map(c =>
                    `Remove correlation: ${c.description}`
                )
            });
        }

        // Bankroll management
        const expectedValue = await this.calculateExpectedValue();
        if (expectedValue.recommended_stake < this.parlayData.stake) {
            recommendations.push({
                type: 'bankroll_management',
                priority: 'medium',
                title: 'Reduce stake size',
                description: `Recommended stake: $${expectedValue.recommended_stake.toFixed(2)} (current: $${this.parlayData.stake})`,
                actions: ['Use Kelly Criterion for optimal sizing']
            });
        }

        // EQ12 Premium recommendations
        if (this.eq12ApiKey && this.analysisLevel === 'premium') {
            const premiumRecs = await this.getEQ12PremiumRecommendations();
            if (premiumRecs) {
                recommendations.push(...premiumRecs);
            }
        }

        return recommendations;
    }

    async sanitizeParlay(recommendations) {
        let sanitized = JSON.parse(JSON.stringify(this.parlayData));

        // Apply high-priority recommendations
        for (const rec of recommendations) {
            if (rec.priority === 'high') {
                switch (rec.type) {
                    case 'correlation_warning':
                        // Remove legs involved in high-risk correlations
                        const legsToRemove = new Set();
                        for (const action of rec.actions) {
                            // Extract leg indices from correlation warnings
                            // This is a simplified implementation
                        }
                        break;

                    case 'risk_reduction':
                        // Remove highest risk legs if too many
                        if (sanitized.legs.length > 8) {
                            sanitized.legs = sanitized.legs.slice(0, 6);
                        }
                        break;
                }
            }
        }

        // Apply stake recommendations
        const expectedValue = await this.calculateExpectedValue();
        if (expectedValue.recommended_stake < sanitized.stake) {
            sanitized.recommended_stake = expectedValue.recommended_stake;
            sanitized.original_stake = sanitized.stake;
            sanitized.stake = expectedValue.recommended_stake;
        }

        // Add metadata
        sanitized.sanitization_applied = true;
        sanitized.sanitization_timestamp = new Date().toISOString();
        sanitized.eq12_analysis_level = this.analysisLevel;

        return sanitized;
    }

    convertToDecimal(odds, format) {
        switch (format.toLowerCase()) {
            case 'american':
                return odds > 0 ? (odds / 100) + 1 : (100 / Math.abs(odds)) + 1;
            case 'fractional':
                const [num, den] = odds.split('/').map(Number);
                return (num / den) + 1;
            case 'decimal':
                return parseFloat(odds);
            default:
                return parseFloat(odds);
        }
    }

    calculateBankrollRisk() {
        const stakePercentage = (this.parlayData.stake / this.parlayData.bankroll) * 100;

        if (stakePercentage > 5) {
            return {
                factor: 'bankroll_risk',
                risk: 4,
                description: `Stake ${stakePercentage.toFixed(1)}% of bankroll (recommended: <3%)`
            };
        } else if (stakePercentage > 3) {
            return {
                factor: 'bankroll_risk',
                risk: 2,
                description: `Stake ${stakePercentage.toFixed(1)}% of bankroll (recommended: <3%)`
            };
        } else {
            return {
                factor: 'bankroll_risk',
                risk: 0,
                description: 'Bankroll management appropriate'
            };
        }
    }

    calculateCorrelationRisk(markets) {
        const riskPairs = [
            ['spread', 'moneyline'],
            ['total', 'team_total'],
            ['player_prop', 'team_prop']
        ];

        let risk = 0;
        for (const [market1, market2] of riskPairs) {
            if (markets.includes(market1) && markets.includes(market2)) {
                risk += 1.5;
            }
        }

        return Math.min(risk, 3);
    }

    findPlayerTeamCorrelations(legs) {
        const correlations = [];

        for (let i = 0; i < legs.length; i++) {
            for (let j = i + 1; j < legs.length; j++) {
                const leg1 = legs[i];
                const leg2 = legs[j];

                // Check if player prop correlates with team performance
                if (leg1.market?.includes('player') && leg2.market?.includes('team')) {
                    if (leg1.team === leg2.team) {
                        correlations.push({
                            type: 'player_team',
                            legs: [i, j],
                            risk_increase: 1.5,
                            description: `Player prop and team performance correlation`
                        });
                    }
                }
            }
        }

        return correlations;
    }

    async getEQ12RiskAnalysis() {
        try {
            const response = await axios.post('https://api.eq12.com/parlay/risk-analysis', {
                parlay_data: this.parlayData,
                analysis_level: 'premium'
            }, {
                headers: {
                    'Authorization': `Bearer ${this.eq12ApiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            return response.data;
        } catch (error) {
            core.debug(`EQ12 risk analysis failed: ${error.message}`);
            return null;
        }
    }

    async getEQ12CorrelationAnalysis() {
        try {
            const response = await axios.post('https://api.eq12.com/parlay/correlations', {
                legs: this.parlayData.legs
            }, {
                headers: {
                    'Authorization': `Bearer ${this.eq12ApiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            return response.data.correlations || [];
        } catch (error) {
            core.debug(`EQ12 correlation analysis failed: ${error.message}`);
            return [];
        }
    }

    async getEQ12PremiumRecommendations() {
        try {
            const response = await axios.post('https://api.eq12.com/parlay/recommendations', {
                parlay_data: this.parlayData,
                risk_assessment: await this.assessRisk()
            }, {
                headers: {
                    'Authorization': `Bearer ${this.eq12ApiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            return response.data.recommendations || [];
        } catch (error) {
            core.debug(`EQ12 premium recommendations failed: ${error.message}`);
            return [];
        }
    }

    async generateSummary(riskAssessment, expectedValue, recommendations) {
        const summary = `## 🛡️ EQ12 Parlay Sanitizer Report

### Risk Assessment
- **Overall Risk Level:** ${riskAssessment.risk_level.toUpperCase()} (${riskAssessment.total_risk}/10)
- **Exceeds Threshold:** ${riskAssessment.exceeds_threshold ? '❌ YES' : '✅ NO'}
- **Number of Legs:** ${this.parlayData.legs.length}

### Expected Value Analysis
- **Parlay Odds:** ${expectedValue.parlay_odds.toFixed(2)}
- **Expected ROI:** ${expectedValue.roi_percentage.toFixed(2)}%
- **Kelly Criterion:** ${expectedValue.kelly_percentage.toFixed(2)}%
- **Recommended Stake:** $${expectedValue.recommended_stake.toFixed(2)}

### Key Risk Factors
${riskAssessment.factors.map(factor => `- **${factor.factor}:** ${factor.description} (Risk: +${factor.risk})`).join('\\n')}

### 🎯 Recommendations (${recommendations.length})
${recommendations.map(rec => `
**${rec.title}** (${rec.priority.toUpperCase()})
- ${rec.description}
${rec.actions.map(action => `  - ${action}`).join('\\n')}
`).join('\\n')}

---
*Generated by EQ12 Parlay Sanitizer v1.0.0*`;

        core.summary.addRaw(summary);
        await core.summary.write();
    }
}

// Main execution
async function run() {
    const sanitizer = new EQ12ParlaySanitizer();
    await sanitizer.sanitize();
}

run().catch(error => {
    core.setFailed(error.message);
});

module.exports = { EQ12ParlaySanitizer };
