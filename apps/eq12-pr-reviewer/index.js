const { Probot } = require('probot');
const axios = require('axios');

/**
 * EQ12 PR Auto-Reviewer
 * Automated pull request analysis with cost optimization and EQ12 intelligence
 */
module.exports = (app) => {
    app.log.info('EQ12 PR Auto-Reviewer loaded');

    // Handle new pull requests
    app.on('pull_request.opened', async (context) => {
        await reviewPullRequest(context, 'opened');
    });

    // Handle pull request updates
    app.on('pull_request.synchronize', async (context) => {
        await reviewPullRequest(context, 'updated');
    });

    async function reviewPullRequest(context, action) {
        const { payload } = context;
        const pr = payload.pull_request;
        const repo = payload.repository;

        try {
            app.log.info(`Reviewing PR #${pr.number} in ${repo.full_name} (${action})`);

            // Validate EQ12 license
            const licenseValid = await validateEQ12License(context);
            if (!licenseValid) {
                await postComment(context, generateBasicReview());
                return;
            }

            // Analyze pull request
            const analysis = await analyzePullRequest(context);

            // Generate comprehensive review
            const review = await generateComprehensiveReview(context, analysis);

            // Post review comment
            await postComment(context, review);

            // Create or update check run
            await createCheckRun(context, analysis);

        } catch (error) {
            app.log.error(`Error reviewing PR #${pr.number}:`, error);
            await postComment(context, generateErrorReview(error));
        }
    }

    async function validateEQ12License(context) {
        const { payload } = context;
        const repo = payload.repository;

        try {
            const response = await axios.post('http://localhost:8000/license/validate', {
                github_username: repo.owner.login,
                repo: repo.full_name,
                action: 'pr_review',
                metadata: {
                    pr_number: payload.pull_request.number
                }
            }, {
                headers: {
                    'Authorization': `Bearer ${process.env.EQ12_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            return response.data.valid;
        } catch (error) {
            app.log.warn('EQ12 license validation failed, using basic review');
            return false;
        }
    }

    async function analyzePullRequest(context) {
        const { payload } = context;
        const pr = payload.pull_request;

        // Get pull request files
        const files = await context.octokit.rest.pulls.listFiles({
            owner: payload.repository.owner.login,
            repo: payload.repository.name,
            pull_request_number: pr.number
        });

        // Analyze workflow changes
        const workflowAnalysis = await analyzeWorkflowChanges(files.data);

        // Analyze cost impact
        const costAnalysis = await analyzeCostImpact(files.data, context);

        // Get EQ12 premium analysis if available
        const eq12Analysis = await getEQ12Analysis(context, files.data);

        return {
            workflow_changes: workflowAnalysis,
            cost_impact: costAnalysis,
            eq12_intelligence: eq12Analysis,
            files_changed: files.data.length,
            lines_added: files.data.reduce((sum, f) => sum + f.additions, 0),
            lines_removed: files.data.reduce((sum, f) => sum + f.deletions, 0)
        };
    }

    async function analyzeWorkflowChanges(files) {
        const workflowFiles = files.filter(f => f.filename.startsWith('.github/workflows/'));
        const changes = {
            workflow_files_modified: workflowFiles.length,
            new_workflows: [],
            modified_workflows: [],
            runner_changes: [],
            matrix_changes: [],
            dependency_changes: []
        };

        for (const file of workflowFiles) {
            if (file.status === 'added') {
                changes.new_workflows.push(file.filename);
            } else if (file.status === 'modified') {
                changes.modified_workflows.push(file.filename);

                // Analyze patch for specific changes
                if (file.patch) {
                    // Check for runner changes
                    const runnerMatches = file.patch.match(/runs-on:\s*(.+)/g);
                    if (runnerMatches) {
                        changes.runner_changes.push({
                            file: file.filename,
                            runners: runnerMatches
                        });
                    }

                    // Check for matrix changes
                    if (file.patch.includes('matrix:')) {
                        changes.matrix_changes.push(file.filename);
                    }

                    // Check for new dependencies
                    if (file.patch.includes('uses:') || file.patch.includes('npm install') || file.patch.includes('pip install')) {
                        changes.dependency_changes.push(file.filename);
                    }
                }
            }
        }

        return changes;
    }

    async function analyzeCostImpact(files, context) {
        const impact = {
            estimated_cost_change: 0,
            risk_level: 'low',
            recommendations: []
        };

        // Analyze workflow files for cost implications
        const workflowFiles = files.filter(f => f.filename.startsWith('.github/workflows/'));

        for (const file of workflowFiles) {
            if (file.patch) {
                // Check for expensive runner additions
                const macosAdditions = (file.patch.match(/\+.*macos/gi) || []).length;
                const windowsAdditions = (file.patch.match(/\+.*windows/gi) || []).length;

                impact.estimated_cost_change += macosAdditions * 2.0; // $2/hour estimate
                impact.estimated_cost_change += windowsAdditions * 1.0; // $1/hour estimate

                // Check for matrix expansions
                const matrixMatches = file.patch.match(/\+.*matrix:/g);
                if (matrixMatches && matrixMatches.length > 0) {
                    impact.risk_level = 'medium';
                    impact.recommendations.push('Matrix expansion detected - consider cost implications');
                }

                // Check for new actions/dependencies
                const newActions = (file.patch.match(/\+.*uses:/g) || []).length;
                if (newActions > 5) {
                    impact.risk_level = 'medium';
                    impact.recommendations.push('Multiple new actions added - review necessity');
                }
            }
        }

        // Set risk level based on estimated cost
        if (impact.estimated_cost_change > 10) {
            impact.risk_level = 'high';
        } else if (impact.estimated_cost_change > 5) {
            impact.risk_level = 'medium';
        }

        return impact;
    }

    async function getEQ12Analysis(context, files) {
        try {
            const response = await axios.post('http://localhost:8000/analysis/premium', {
                repo: context.payload.repository.full_name,
                commit_sha: context.payload.pull_request.head.sha,
                analysis_type: 'pr_review',
                include_predictions: true,
                include_correlations: true
            }, {
                headers: {
                    'Authorization': `Bearer ${process.env.EQ12_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            return response.data.report;
        } catch (error) {
            return null;
        }
    }

    async function generateComprehensiveReview(context, analysis) {
        let review = `## 🤖 EQ12 PR Auto-Review

### 📊 Analysis Summary
- **Files Changed:** ${analysis.files_changed}
- **Lines Added:** ${analysis.lines_added}
- **Lines Removed:** ${analysis.lines_removed}
- **Cost Risk Level:** ${analysis.cost_impact.risk_level.toUpperCase()}

`;

        // Workflow changes analysis
        if (analysis.workflow_changes.workflow_files_modified > 0) {
            review += `### 🔄 Workflow Changes
`;
            if (analysis.workflow_changes.new_workflows.length > 0) {
                review += `- **New Workflows:** ${analysis.workflow_changes.new_workflows.join(', ')}
`;
            }
            if (analysis.workflow_changes.modified_workflows.length > 0) {
                review += `- **Modified Workflows:** ${analysis.workflow_changes.modified_workflows.join(', ')}
`;
            }
            if (analysis.workflow_changes.runner_changes.length > 0) {
                review += `- **Runner Changes Detected** ⚠️
`;
            }
        }

        // Cost impact analysis
        if (analysis.cost_impact.estimated_cost_change > 0) {
            review += `### 💰 Cost Impact Analysis
- **Estimated Monthly Cost Change:** +$${analysis.cost_impact.estimated_cost_change.toFixed(2)}
- **Risk Level:** ${analysis.cost_impact.risk_level.toUpperCase()}

#### Recommendations:
${analysis.cost_impact.recommendations.map(rec => `- ${rec}`).join('\\n')}
`;
        }

        // EQ12 Intelligence (if available)
        if (analysis.eq12_intelligence) {
            review += `### 🧠 EQ12 Intelligence Analysis
`;
            if (analysis.eq12_intelligence.performance_metrics) {
                review += `#### Performance Prediction
- **Backtested ROI:** ${analysis.eq12_intelligence.performance_metrics.backtested_roi}%
- **Sharpe Ratio:** ${analysis.eq12_intelligence.performance_metrics.sharpe_ratio}
- **Max Drawdown:** ${analysis.eq12_intelligence.performance_metrics.max_drawdown}%
`;
            }

            if (analysis.eq12_intelligence.risk_assessment) {
                review += `#### Risk Assessment
- **Overall Risk:** ${analysis.eq12_intelligence.risk_assessment.overall_risk}
- **Volatility Score:** ${analysis.eq12_intelligence.risk_assessment.volatility_score}
- **Recommendation:** ${analysis.eq12_intelligence.risk_assessment.recommendation}
`;
            }
        }

        // Security recommendations
        review += `### 🔒 Security Recommendations
- Ensure all secrets are properly stored in repository secrets
- Review new dependencies for security vulnerabilities
- Consider using dependabot for automated security updates
`;

        // Performance recommendations
        review += `### ⚡ Performance Recommendations
- Use caching for dependencies where possible
- Consider using \`ubuntu-latest\` runners for cost efficiency
- Implement path filtering to avoid unnecessary workflow runs
`;

        review += `
---
*Generated by EQ12 PR Auto-Reviewer v1.0.0 | [Learn More](https://docs.eq12.com/pr-reviewer)*`;

        return review;
    }

    function generateBasicReview() {
        return `## 🤖 EQ12 PR Auto-Review (Basic)

Thank you for your contribution!

### Basic Analysis
- This pull request has been automatically analyzed
- For advanced cost optimization and EQ12 intelligence features, upgrade to EQ12 Premium

### General Recommendations
- ✅ Ensure all tests pass before merging
- ✅ Review code for security best practices
- ✅ Consider impact on GitHub Actions costs
- ✅ Update documentation if needed

---
*Upgrade to EQ12 Premium for advanced analysis | [Learn More](https://eq12.com/premium)*`;
    }

    function generateErrorReview(error) {
        return `## ❌ EQ12 PR Auto-Review Error

An error occurred while analyzing this pull request:
\`\`\`
${error.message}
\`\`\`

Please check:
- Repository permissions
- EQ12 API availability
- Network connectivity

---
*Contact support if this issue persists | [Support](mailto:support@eq12.com)*`;
    }

    async function postComment(context, review) {
        return context.octokit.rest.issues.createComment({
            owner: context.payload.repository.owner.login,
            repo: context.payload.repository.name,
            issue_number: context.payload.pull_request.number,
            body: review
        });
    }

    async function createCheckRun(context, analysis) {
        const conclusion = analysis.cost_impact.risk_level === 'high' ? 'failure' : 'success';
        const summary = `Cost Risk: ${analysis.cost_impact.risk_level} | Files: ${analysis.files_changed} | Est. Cost Change: +$${analysis.cost_impact.estimated_cost_change.toFixed(2)}`;

        return context.octokit.rest.checks.create({
            owner: context.payload.repository.owner.login,
            repo: context.payload.repository.name,
            name: 'EQ12 Cost Analysis',
            head_sha: context.payload.pull_request.head.sha,
            status: 'completed',
            conclusion,
            output: {
                title: 'EQ12 Cost Analysis Results',
                summary,
                text: `Detailed analysis available in PR comments.`
            }
        });
    }
};
