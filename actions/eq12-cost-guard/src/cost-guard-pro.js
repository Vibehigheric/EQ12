const core = require('@actions/core');
const github = require('@actions/github');
const { EQ12OpenAISecurityManager } = require('./eq12-openai-security');

/**
 * EQ12 Cost Guard Pro - AI-powered GitHub Actions cost optimization
 * Revenue model: $29.99/month for AI features, $99.99/month for enterprise
 */
class EQ12CostGuardPro {
    constructor() {
        // Basic inputs
        this.token = core.getInput('token');
        this.costThreshold = parseFloat(core.getInput('cost-threshold') || '10.00');
        this.analysisLevel = core.getInput('analysis-level') || 'standard';

        // EQ12 License validation
        this.eq12ApiKey = core.getInput('eq12-api-key');
        this.eq12LicenseServer = core.getInput('eq12-license-server') || 'https://api.eq12.com';

        // OpenAI integration (premium feature)
        this.openaiEnabled = core.getInput('openai-enabled') === 'true';
        this.openaiModel = core.getInput('openai-model') || 'gpt-4o-mini';

        // Revenue tracking
        this.subscriptionTier = 'free'; // Will be validated via license server

        this.octokit = github.getOctokit(this.token);
        this.context = github.context;

        // Initialize OpenAI security manager
        this.openaiManager = null;
        if (this.openaiEnabled) {
            this.openaiManager = new EQ12OpenAISecurityManager('ci');
        }
    }

    async analyze() {
        try {
            core.info('🚀 Starting EQ12 Cost Guard Pro analysis...');

            // Step 1: Validate EQ12 license and subscription tier
            const licenseValidation = await this.validateEQ12License();
            if (!licenseValidation.valid) {
                await this.generateFreeTierReport();
                return;
            }

            this.subscriptionTier = licenseValidation.tier;
            core.info(`✅ License validated: ${this.subscriptionTier} tier`);

            // Step 2: Collect workflow cost data
            const costData = await this.collectCostData();

            // Step 3: Generate AI-powered analysis (premium feature)
            let aiAnalysis = null;
            if (this.subscriptionTier !== 'free' && this.openaiEnabled && this.openaiManager) {
                aiAnalysis = await this.generateAIAnalysis(costData);

                // Bill the usage
                await this.recordUsage('ai_cost_analysis', costData);
            }

            // Step 4: Generate comprehensive report
            const report = await this.generateComprehensiveReport(costData, aiAnalysis);

            // Step 5: Set outputs and create summary
            await this.setOutputsAndSummary(report);

            core.info('✅ EQ12 Cost Guard Pro analysis completed');

        } catch (error) {
            core.setFailed(`EQ12 Cost Guard Pro failed: ${error.message}`);
        }
    }

    async validateEQ12License() {
        if (!this.eq12ApiKey) {
            return { valid: false, tier: 'free', message: 'No EQ12 API key provided' };
        }

        try {
            const response = await fetch(`${this.eq12LicenseServer}/license/validate`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.eq12ApiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    github_username: this.context.repo.owner,
                    repo: this.context.repo.repo,
                    action: 'cost_guard_pro',
                    metadata: {
                        analysis_level: this.analysisLevel,
                        openai_enabled: this.openaiEnabled
                    }
                })
            });

            const data = await response.json();

            if (data.valid) {
                return {
                    valid: true,
                    tier: data.plan,
                    credits: data.credits_remaining,
                    message: 'License valid'
                };
            } else {
                return {
                    valid: false,
                    tier: 'free',
                    message: data.message || 'License validation failed'
                };
            }

        } catch (error) {
            core.warning(`License validation failed: ${error.message}`);
            return { valid: false, tier: 'free', message: 'Validation error' };
        }
    }

    async collectCostData() {
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

        try {
            const { data: runs } = await this.octokit.rest.actions.listWorkflowRunsForRepo({
                owner: this.context.repo.owner,
                repo: this.context.repo.repo,
                per_page: 100,
                created: `>=${thirtyDaysAgo.toISOString()}`
            });

            let totalCost = 0;
            let totalMinutes = 0;
            const costByWorkflow = {};
            const costByRunner = {};
            const inefficiencies = [];

            // Runner cost rates (GitHub's pricing)
            const costRates = {
                'ubuntu-latest': 0.008,
                'ubuntu-20.04': 0.008,
                'ubuntu-18.04': 0.008,
                'windows-latest': 0.016,
                'windows-2019': 0.016,
                'windows-2022': 0.016,
                'macos-latest': 0.08,
                'macos-11': 0.08,
                'macos-12': 0.08,
                'macos-13': 0.08
            };

            for (const run of runs.workflow_runs) {
                try {
                    const { data: jobs } = await this.octokit.rest.actions.listJobsForWorkflowRun({
                        owner: this.context.repo.owner,
                        repo: this.context.repo.repo,
                        run_id: run.id
                    });

                    for (const job of jobs.jobs) {
                        if (job.started_at && job.completed_at) {
                            const duration = (new Date(job.completed_at) - new Date(job.started_at)) / (1000 * 60);
                            const runnerType = this.extractRunnerType(job.runner_name || 'ubuntu-latest');
                            const costPerMinute = costRates[runnerType] || costRates['ubuntu-latest'];
                            const jobCost = duration * costPerMinute;

                            totalCost += jobCost;
                            totalMinutes += duration;

                            // Track by workflow
                            const workflowName = run.name || 'Unknown';
                            costByWorkflow[workflowName] = (costByWorkflow[workflowName] || 0) + jobCost;

                            // Track by runner
                            costByRunner[runnerType] = (costByRunner[runnerType] || 0) + jobCost;

                            // Detect inefficiencies
                            if (duration > 60 && runnerType.includes('macos')) {
                                inefficiencies.push({
                                    type: 'expensive_runner_long_job',
                                    job: job.name,
                                    workflow: workflowName,
                                    duration: duration,
                                    runner: runnerType,
                                    cost: jobCost,
                                    suggestion: 'Consider using ubuntu-latest or optimizing job duration'
                                });
                            }

                            if (duration < 2 && costPerMinute > 0.01) {
                                inefficiencies.push({
                                    type: 'expensive_runner_short_job',
                                    job: job.name,
                                    workflow: workflowName,
                                    duration: duration,
                                    runner: runnerType,
                                    cost: jobCost,
                                    suggestion: 'Short jobs on expensive runners waste money due to minimum billing'
                                });
                            }
                        }
                    }
                } catch (error) {
                    core.debug(`Failed to analyze run ${run.id}: ${error.message}`);
                }
            }

            return {
                totalCost,
                totalMinutes,
                totalRuns: runs.workflow_runs.length,
                avgDailyCost: totalCost / 30,
                monthlyProjected: totalCost,
                costByWorkflow: Object.entries(costByWorkflow)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10),
                costByRunner,
                inefficiencies,
                period: '30 days'
            };

        } catch (error) {
            throw new Error(`Cost data collection failed: ${error.message}`);
        }
    }

    async generateAIAnalysis(costData) {
        if (!this.openaiManager || this.subscriptionTier === 'free') {
            return null;
        }

        try {
            core.info('🧠 Generating AI-powered cost optimization analysis...');

            const prompt = this.createOptimizationPrompt(costData);

            const response = await this.openaiManager.secure_openai_request(
                this.openaiModel,
                [
                    {
                        role: 'system',
                        content: 'You are an expert GitHub Actions cost optimization consultant. Analyze the provided workflow cost data and generate specific, actionable recommendations to reduce costs while maintaining efficiency.'
                    },
                    {
                        role: 'user',
                        content: prompt
                    }
                ],
                {
                    max_tokens: 1500,
                    temperature: 0.3
                }
            );

            const aiRecommendations = this.parseAIRecommendations(response.response.choices[0].message.content);

            return {
                model: this.openaiModel,
                recommendations: aiRecommendations,
                cost_estimate: response.cost_check?.estimated_cost || 0,
                confidence: this.calculateConfidenceScore(aiRecommendations, costData)
            };

        } catch (error) {
            core.warning(`AI analysis failed: ${error.message}`);
            return null;
        }
    }

    createOptimizationPrompt(costData) {
        return `# GitHub Actions Cost Optimization Analysis

## Current Usage Data (${costData.period})
- Total Cost: $${costData.totalCost.toFixed(2)}
- Total Runtime: ${costData.totalMinutes.toFixed(0)} minutes
- Number of Runs: ${costData.totalRuns}
- Average Daily Cost: $${costData.avgDailyCost.toFixed(2)}
- Monthly Projected: $${costData.monthlyProjected.toFixed(2)}

## Cost by Workflow
${costData.costByWorkflow.map(([name, cost]) => `- ${name}: $${cost.toFixed(2)}`).join('\n')}

## Cost by Runner Type
${Object.entries(costData.costByRunner).map(([runner, cost]) => `- ${runner}: $${cost.toFixed(2)}`).join('\n')}

## Detected Inefficiencies
${costData.inefficiencies.map(ineff => `- ${ineff.type}: ${ineff.suggestion} (${ineff.workflow}/${ineff.job})`).join('\n')}

Please provide:
1. Top 5 specific cost optimization recommendations
2. Estimated monthly savings for each recommendation
3. Implementation difficulty (Easy/Medium/Hard)
4. Risk assessment for each change
5. Priority ranking (1-5, 5 being highest)

Format as structured recommendations with clear action items.`;
    }

    parseAIRecommendations(aiResponse) {
        // Parse AI response into structured recommendations
        const lines = aiResponse.split('\n');
        const recommendations = [];
        let currentRec = null;

        for (const line of lines) {
            const trimmed = line.trim();

            // Look for numbered recommendations
            if (/^\d+\./.test(trimmed)) {
                if (currentRec) recommendations.push(currentRec);

                currentRec = {
                    title: trimmed.replace(/^\d+\.\s*/, ''),
                    description: '',
                    savings: 0,
                    difficulty: 'Medium',
                    priority: 3,
                    implementation: []
                };
            } else if (currentRec && trimmed) {
                // Extract specific details
                if (trimmed.toLowerCase().includes('saving')) {
                    const match = trimmed.match(/\$(\d+(?:\.\d+)?)/);
                    if (match) currentRec.savings = parseFloat(match[1]);
                }

                if (trimmed.toLowerCase().includes('difficulty')) {
                    if (trimmed.includes('Easy')) currentRec.difficulty = 'Easy';
                    if (trimmed.includes('Hard')) currentRec.difficulty = 'Hard';
                }

                if (trimmed.toLowerCase().includes('priority')) {
                    const match = trimmed.match(/(\d+)/);
                    if (match) currentRec.priority = parseInt(match[1]);
                }

                if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
                    currentRec.implementation.push(trimmed.substring(2));
                } else {
                    currentRec.description += ' ' + trimmed;
                }
            }
        }

        if (currentRec) recommendations.push(currentRec);

        return recommendations;
    }

    calculateConfidenceScore(recommendations, costData) {
        // Calculate confidence based on data quality and recommendation relevance
        let score = 0.7; // Base confidence

        // More data = higher confidence
        if (costData.totalRuns > 50) score += 0.1;
        if (costData.totalCost > 10) score += 0.1;

        // Quality recommendations increase confidence
        if (recommendations.length >= 3) score += 0.05;
        if (recommendations.some(r => r.savings > 5)) score += 0.05;

        return Math.min(score, 0.95); // Cap at 95%
    }

    async generateFreeTierReport() {
        const basicReport = {
            tier: 'free',
            message: 'Upgrade to EQ12 Pro for AI-powered cost optimization',
            basic_recommendations: [
                'Use ubuntu-latest runners instead of macOS/Windows when possible',
                'Implement caching for dependencies',
                'Use path filtering to avoid unnecessary workflow runs',
                'Optimize matrix builds to reduce combinations'
            ],
            upgrade_benefits: [
                'AI-powered cost analysis and recommendations',
                'Detailed inefficiency detection',
                'Custom optimization strategies',
                'Real-time budget alerts',
                'Advanced reporting and analytics'
            ],
            upgrade_url: 'https://eq12.com/pricing'
        };

        core.setOutput('analysis-result', JSON.stringify(basicReport));

        await this.generateBasicSummary(basicReport);
    }

    async generateComprehensiveReport(costData, aiAnalysis) {
        const report = {
            tier: this.subscriptionTier,
            timestamp: new Date().toISOString(),
            cost_analysis: {
                current_period: costData,
                threshold_status: costData.monthlyProjected <= this.costThreshold ? 'OK' : 'EXCEEDED',
                efficiency_score: this.calculateEfficiencyScore(costData)
            },
            ai_analysis: aiAnalysis,
            recommendations: this.combineRecommendations(costData, aiAnalysis),
            projected_savings: this.calculateTotalSavings(aiAnalysis?.recommendations || []),
            next_steps: this.generateNextSteps(costData, aiAnalysis)
        };

        return report;
    }

    calculateEfficiencyScore(costData) {
        // Score based on cost per run, runner selection, and inefficiencies
        let score = 100;

        const avgCostPerRun = costData.totalCost / costData.totalRuns;
        if (avgCostPerRun > 1.0) score -= 20;
        if (avgCostPerRun > 2.0) score -= 20;

        // Penalize expensive runners
        const macosUsage = costData.costByRunner['macos-latest'] || 0;
        const windowsUsage = costData.costByRunner['windows-latest'] || 0;
        const expensiveUsage = (macosUsage + windowsUsage) / costData.totalCost;

        if (expensiveUsage > 0.5) score -= 15;
        if (expensiveUsage > 0.8) score -= 15;

        // Penalize inefficiencies
        score -= Math.min(costData.inefficiencies.length * 5, 30);

        return Math.max(score, 0);
    }

    combineRecommendations(costData, aiAnalysis) {
        const recommendations = [];

        // Basic recommendations
        if (costData.costByRunner['macos-latest'] > costData.totalCost * 0.3) {
            recommendations.push({
                type: 'runner_optimization',
                title: 'Reduce macOS runner usage',
                description: 'macOS runners cost 10x more than Ubuntu runners',
                priority: 5,
                estimated_savings: costData.costByRunner['macos-latest'] * 0.8,
                difficulty: 'Easy'
            });
        }

        // Add AI recommendations if available
        if (aiAnalysis?.recommendations) {
            recommendations.push(...aiAnalysis.recommendations.map(rec => ({
                ...rec,
                type: 'ai_recommendation'
            })));
        }

        return recommendations.sort((a, b) => (b.priority || 0) - (a.priority || 0));
    }

    calculateTotalSavings(recommendations) {
        return recommendations.reduce((total, rec) => total + (rec.savings || 0), 0);
    }

    generateNextSteps(costData, aiAnalysis) {
        const steps = [];

        if (costData.monthlyProjected > this.costThreshold) {
            steps.push('🚨 Implement high-priority cost optimizations immediately');
        }

        if (aiAnalysis) {
            steps.push('🧠 Review and implement AI-generated recommendations');
        } else {
            steps.push('⭐ Upgrade to EQ12 Pro for AI-powered optimization');
        }

        steps.push('📊 Monitor cost trends and set up budget alerts');
        steps.push('🔄 Schedule regular cost optimization reviews');

        return steps;
    }

    async recordUsage(action, metadata = {}) {
        if (!this.eq12ApiKey) return;

        try {
            await fetch(`${this.eq12LicenseServer}/license/consume`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.eq12ApiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    github_username: this.context.repo.owner,
                    repo: this.context.repo.repo,
                    action: action,
                    metadata: {
                        ...metadata,
                        analysis_level: this.analysisLevel,
                        openai_enabled: this.openaiEnabled,
                        subscription_tier: this.subscriptionTier
                    }
                })
            });
        } catch (error) {
            core.debug(`Usage recording failed: ${error.message}`);
        }
    }

    async setOutputsAndSummary(report) {
        core.setOutput('analysis-result', JSON.stringify(report));
        core.setOutput('cost-summary', JSON.stringify(report.cost_analysis));
        core.setOutput('recommendations', JSON.stringify(report.recommendations));
        core.setOutput('projected-savings', report.projected_savings.toString());

        await this.generatePremiumSummary(report);
    }

    async generatePremiumSummary(report) {
        const summary = `## 💰 EQ12 Cost Guard Pro Analysis (${report.tier.toUpperCase()})

### 📊 Cost Analysis
- **Current Monthly Cost:** $${report.cost_analysis.current_period.monthlyProjected.toFixed(2)}
- **Threshold Status:** ${report.cost_analysis.threshold_status}
- **Efficiency Score:** ${report.cost_analysis.efficiency_score}/100
- **Total Runs:** ${report.cost_analysis.current_period.totalRuns}

### 🎯 Top Recommendations
${report.recommendations.slice(0, 5).map((rec, i) => `
**${i + 1}. ${rec.title}** (Priority: ${rec.priority}/5)
- ${rec.description}
- Estimated Savings: $${(rec.savings || 0).toFixed(2)}/month
- Difficulty: ${rec.difficulty}
`).join('')}

### 💡 AI-Powered Insights
${report.ai_analysis ? `
- **Model Used:** ${report.ai_analysis.model}
- **Confidence:** ${(report.ai_analysis.confidence * 100).toFixed(1)}%
- **Total Projected Savings:** $${report.projected_savings.toFixed(2)}/month
` : `
*Upgrade to EQ12 Pro for AI-powered cost optimization insights*
[Get EQ12 Pro](https://eq12.com/pricing)
`}

### 📋 Next Steps
${report.next_steps.map(step => `- ${step}`).join('\n')}

---
*Powered by EQ12 Cost Guard Pro v2.0.0 | [Learn More](https://docs.eq12.com/cost-guard-pro)*`;

        core.summary.addRaw(summary);
        await core.summary.write();
    }

    async generateBasicSummary(basicReport) {
        const summary = `## 💰 EQ12 Cost Guard (Free Tier)

### 🚀 Upgrade to Pro for Advanced Features

**What you're missing:**
- 🧠 AI-powered cost analysis
- 📊 Advanced inefficiency detection
- 💡 Custom optimization strategies
- 🚨 Real-time budget alerts
- 📈 Detailed cost forecasting

### 🎯 Basic Recommendations
${basicReport.basic_recommendations.map(rec => `- ${rec}`).join('\n')}

### ⭐ Pro Benefits
${basicReport.upgrade_benefits.map(benefit => `- ✅ ${benefit}`).join('\n')}

**[Upgrade to EQ12 Pro - Only $29.99/month](${basicReport.upgrade_url})**

---
*EQ12 Cost Guard Free Tier | [Upgrade Now](${basicReport.upgrade_url})*`;

        core.summary.addRaw(summary);
        await core.summary.write();
    }

    extractRunnerType(runnerName) {
        const lower = (runnerName || '').toLowerCase();
        if (lower.includes('macos')) return 'macos-latest';
        if (lower.includes('windows')) return 'windows-latest';
        return 'ubuntu-latest';
    }
}

// Main execution
async function run() {
    const costGuard = new EQ12CostGuardPro();
    await costGuard.analyze();
}

run().catch(error => {
    core.setFailed(error.message);
});

module.exports = { EQ12CostGuardPro };
