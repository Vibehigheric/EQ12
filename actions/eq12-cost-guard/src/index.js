const core = require('@actions/core');
const github = require('@actions/github');
const axios = require('axios');
const _ = require('lodash');

/**
 * EQ12 Cost Guard - GitHub Actions cost monitoring and optimization
 */
class EQ12CostGuard {
    constructor() {
        this.token = core.getInput('token');
        this.costThreshold = parseFloat(core.getInput('cost-threshold') || '10.00');
        this.analysisLevel = core.getInput('analysis-level') || 'standard';
        this.eq12ApiKey = core.getInput('eq12-api-key');
        this.notificationWebhook = core.getInput('notification-webhook');

        this.octokit = github.getOctokit(this.token);
        this.context = github.context;

        // Cost calculation constants (GitHub's pricing)
        this.COST_PER_MINUTE = {
            'ubuntu-latest': 0.008,
            'windows-latest': 0.016,
            'macos-latest': 0.08,
            'ubuntu-20.04': 0.008,
            'ubuntu-18.04': 0.008,
            'windows-2019': 0.016,
            'windows-2022': 0.016,
            'macos-11': 0.08,
            'macos-12': 0.08
        };
    }

    async analyze() {
        try {
            core.info('🔍 Starting EQ12 Cost Guard analysis...');

            const workflowRuns = await this.getRecentWorkflowRuns();
            const costAnalysis = await this.analyzeCosts(workflowRuns);
            const recommendations = await this.generateRecommendations(costAnalysis);

            // Generate report
            const report = {
                timestamp: new Date().toISOString(),
                analysis_level: this.analysisLevel,
                cost_summary: costAnalysis.summary,
                detailed_analysis: costAnalysis.details,
                recommendations: recommendations,
                projected_savings: this.calculateProjectedSavings(recommendations)
            };

            // Output results
            core.setOutput('cost-analysis', JSON.stringify(report.cost_summary));
            core.setOutput('recommendations', JSON.stringify(report.recommendations));
            core.setOutput('projected-savings', JSON.stringify(report.projected_savings));

            // Check threshold
            if (costAnalysis.summary.monthly_projected > this.costThreshold) {
                await this.sendAlert(report);
                core.setFailed(`Monthly projected cost ($${costAnalysis.summary.monthly_projected.toFixed(2)}) exceeds threshold ($${this.costThreshold.toFixed(2)})`);
            }

            // Generate markdown summary
            await this.generateSummary(report);

            core.info('✅ EQ12 Cost Guard analysis completed');

        } catch (error) {
            core.setFailed(`EQ12 Cost Guard failed: ${error.message}`);
        }
    }

    async getRecentWorkflowRuns() {
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

        try {
            const { data: runs } = await this.octokit.rest.actions.listWorkflowRunsForRepo({
                owner: this.context.repo.owner,
                repo: this.context.repo.repo,
                per_page: 100,
                created: `>=${thirtyDaysAgo.toISOString()}`
            });

            return runs.workflow_runs;
        } catch (error) {
            core.warning(`Failed to fetch workflow runs: ${error.message}`);
            return [];
        }
    }

    async analyzeCosts(workflowRuns) {
        let totalCost = 0;
        let totalMinutes = 0;
        const costByWorkflow = {};
        const costByRunner = {};
        const dailyCosts = {};

        for (const run of workflowRuns) {
            try {
                const { data: jobs } = await this.octokit.rest.actions.listJobsForWorkflowRun({
                    owner: this.context.repo.owner,
                    repo: this.context.repo.repo,
                    run_id: run.id
                });

                for (const job of jobs.jobs) {
                    const runnerOs = this.extractRunnerOS(job.runner_name || job.labels?.join(',') || 'ubuntu-latest');
                    const costPerMinute = this.COST_PER_MINUTE[runnerOs] || this.COST_PER_MINUTE['ubuntu-latest'];

                    if (job.started_at && job.completed_at) {
                        const duration = (new Date(job.completed_at) - new Date(job.started_at)) / (1000 * 60); // minutes
                        const jobCost = duration * costPerMinute;

                        totalCost += jobCost;
                        totalMinutes += duration;

                        // Track by workflow
                        const workflowName = run.name || 'Unknown';
                        costByWorkflow[workflowName] = (costByWorkflow[workflowName] || 0) + jobCost;

                        // Track by runner
                        costByRunner[runnerOs] = (costByRunner[runnerOs] || 0) + jobCost;

                        // Track daily costs
                        const date = new Date(job.started_at).toISOString().split('T')[0];
                        dailyCosts[date] = (dailyCosts[date] || 0) + jobCost;
                    }
                }
            } catch (error) {
                core.warning(`Failed to analyze run ${run.id}: ${error.message}`);
            }
        }

        const avgDailyCost = totalCost / 30;
        const monthlyProjected = avgDailyCost * 30;

        return {
            summary: {
                total_cost_30_days: totalCost,
                total_minutes: totalMinutes,
                average_daily_cost: avgDailyCost,
                monthly_projected: monthlyProjected,
                total_runs: workflowRuns.length
            },
            details: {
                cost_by_workflow: Object.entries(costByWorkflow)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10)
                    .map(([name, cost]) => ({ workflow: name, cost: cost.toFixed(4) })),
                cost_by_runner: costByRunner,
                daily_costs: dailyCosts
            }
        };
    }

    extractRunnerOS(runnerInfo) {
        const lower = runnerInfo.toLowerCase();
        if (lower.includes('macos')) return 'macos-latest';
        if (lower.includes('windows')) return 'windows-latest';
        return 'ubuntu-latest';
    }

    async generateRecommendations(costAnalysis) {
        const recommendations = [];

        // Check for expensive runners
        const expensiveRunners = Object.entries(costAnalysis.details.cost_by_runner)
            .filter(([runner, cost]) => cost > costAnalysis.summary.total_cost_30_days * 0.3)
            .map(([runner, cost]) => ({ runner, cost, savings_potential: cost * 0.5 }));

        if (expensiveRunners.length > 0) {
            recommendations.push({
                type: 'runner_optimization',
                priority: 'high',
                title: 'Optimize expensive runners',
                description: `Consider using Ubuntu runners instead of ${expensiveRunners.map(r => r.runner).join(', ')}`,
                potential_savings: expensiveRunners.reduce((sum, r) => sum + r.savings_potential, 0),
                implementation: 'Change runner labels in workflow files to ubuntu-latest where possible'
            });
        }

        // Check for frequent workflows
        const frequentWorkflows = costAnalysis.details.cost_by_workflow
            .filter(w => parseFloat(w.cost) > costAnalysis.summary.total_cost_30_days * 0.2);

        if (frequentWorkflows.length > 0) {
            recommendations.push({
                type: 'workflow_optimization',
                priority: 'medium',
                title: 'Optimize high-cost workflows',
                description: `Workflows ${frequentWorkflows.map(w => w.workflow).join(', ')} consume significant resources`,
                potential_savings: frequentWorkflows.reduce((sum, w) => sum + parseFloat(w.cost), 0) * 0.3,
                implementation: 'Add path filters, reduce matrix size, or use caching'
            });
        }

        // EQ12 Premium Analysis
        if (this.eq12ApiKey && this.analysisLevel === 'premium') {
            try {
                const premiumRecommendations = await this.getEQ12PremiumRecommendations(costAnalysis);
                recommendations.push(...premiumRecommendations);
            } catch (error) {
                core.warning(`EQ12 Premium analysis failed: ${error.message}`);
            }
        }

        return recommendations;
    }

    async getEQ12PremiumRecommendations(costAnalysis) {
        try {
            const response = await axios.post('https://api.eq12.com/actions/analyze-costs', {
                cost_data: costAnalysis,
                analysis_type: 'github_actions_optimization'
            }, {
                headers: {
                    'Authorization': `Bearer ${this.eq12ApiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            return response.data.recommendations || [];
        } catch (error) {
            core.debug(`EQ12 API call failed: ${error.message}`);
            return [];
        }
    }

    calculateProjectedSavings(recommendations) {
        const totalSavings = recommendations.reduce((sum, rec) => sum + (rec.potential_savings || 0), 0);
        return {
            monthly_savings: totalSavings,
            annual_savings: totalSavings * 12,
            percentage_reduction: totalSavings / (this.costThreshold || 1) * 100
        };
    }

    async sendAlert(report) {
        if (!this.notificationWebhook) return;

        try {
            await axios.post(this.notificationWebhook, {
                text: `🚨 EQ12 Cost Guard Alert: GitHub Actions costs exceed threshold`,
                blocks: [
                    {
                        type: 'section',
                        text: {
                            type: 'mrkdwn',
                            text: `*Repository:* ${this.context.repo.owner}/${this.context.repo.repo}\\n*Monthly Projected Cost:* $${report.cost_summary.monthly_projected.toFixed(2)}\\n*Threshold:* $${this.costThreshold.toFixed(2)}`
                        }
                    },
                    {
                        type: 'section',
                        text: {
                            type: 'mrkdwn',
                            text: `*Top Recommendations:*\\n${report.recommendations.slice(0, 3).map(r => `• ${r.title}`).join('\\n')}`
                        }
                    }
                ]
            });
        } catch (error) {
            core.warning(`Failed to send alert: ${error.message}`);
        }
    }

    async generateSummary(report) {
        const summary = `## 💰 EQ12 Cost Guard Report

### Cost Summary (Last 30 Days)
- **Total Cost:** $${report.cost_summary.total_cost_30_days.toFixed(2)}
- **Monthly Projected:** $${report.cost_summary.monthly_projected.toFixed(2)}
- **Average Daily:** $${report.cost_summary.average_daily_cost.toFixed(2)}
- **Total Workflow Runs:** ${report.cost_summary.total_runs}

### 🎯 Optimization Recommendations
${report.recommendations.map(rec => `
**${rec.title}** (${rec.priority.toUpperCase()})
- ${rec.description}
- Potential Savings: $${(rec.potential_savings || 0).toFixed(2)}/month
- Implementation: ${rec.implementation}
`).join('\\n')}

### 💡 Projected Savings
- **Monthly:** $${report.projected_savings.monthly_savings.toFixed(2)}
- **Annual:** $${report.projected_savings.annual_savings.toFixed(2)}
- **Cost Reduction:** ${report.projected_savings.percentage_reduction.toFixed(1)}%

---
*Generated by EQ12 Cost Guard v1.0.0*`;

        core.summary.addRaw(summary);
        await core.summary.write();
    }
}

// Main execution
async function run() {
    const costGuard = new EQ12CostGuard();
    await costGuard.analyze();
}

run().catch(error => {
    core.setFailed(error.message);
});

module.exports = { EQ12CostGuard };
