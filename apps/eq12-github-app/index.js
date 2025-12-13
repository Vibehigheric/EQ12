/**
 * EQ12 GitHub App - CI-as-a-Service Platform
 * Monetizes every commit with license validation and premium analysis
 */

module.exports = (app) => {
  app.log.info('EQ12 GitHub App initialized');

  // Handle push and pull request events for commit monetization
  app.on(['push', 'pull_request'], async (ctx) => {
    const { owner, repo } = ctx.repo();
    const sha = ctx.payload.after || ctx.payload.pull_request?.head?.sha;

    app.log.info(`Processing commit ${sha} for ${owner}/${repo}`);

    // Skip if commit message contains skip flags
    const commitMessage = ctx.payload.head_commit?.message || ctx.payload.pull_request?.title || '';
    if (commitMessage.includes('[skip-eq12]') || commitMessage.includes('[skip ci]')) {
      app.log.info('Skipping due to skip flag in commit message');
      return;
    }

    // Validate license with EQ12 license server
    const licenseUrl = `${process.env.EQ12_LICENSE}/consume?repo=${owner}/${repo}&sha=${sha}`;

    try {
      const licenseResponse = await fetch(licenseUrl, {
        headers: {
          'Authorization': `Bearer ${process.env.EQ12_TOKEN}`,
          'Content-Type': 'application/json'
        }
      });

      const license = await licenseResponse.json();

      if (!license.allowed) {
        app.log.warn(`License validation failed for ${owner}/${repo}: ${license.reason}`);

        return ctx.octokit.checks.create({
          owner,
          repo,
          name: 'EQ12 Analysis',
          head_sha: sha,
          status: 'completed',
          conclusion: 'cancelled',
          output: {
            title: 'EQ12 License Required',
            summary: license.reason || 'Upgrade to EQ12 Pro to enable commit analysis. Visit https://eq12.com/pricing',
            text: `Current plan: ${license.plan || 'Free'}\nRemaining credits: ${license.remaining || 0}\n\n[Upgrade Now](https://eq12.com/upgrade)`
          }
        });
      }

      app.log.info(`License validated for ${owner}/${repo}. Plan: ${license.plan}, Remaining: ${license.remaining}`);

      // Call EQ12 analysis API for premium insights
      const analysisBody = {
        owner,
        repo,
        commitSha: sha,
        event: ctx.name,
        timestamp: new Date().toISOString()
      };

      const analysisResponse = await fetch(`${process.env.EQ12_API}/ci/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.EQ12_API_KEY}`
        },
        body: JSON.stringify(analysisBody)
      });

      const report = await analysisResponse.json();

      // Create successful check with premium insights
      return ctx.octokit.checks.create({
        owner,
        repo,
        name: 'EQ12 Analysis',
        head_sha: sha,
        status: 'completed',
        conclusion: 'success',
        output: {
          title: '🎯 EQ12 Premium Analysis Complete',
          summary: report.summary || 'Commit analyzed successfully with EQ12 intelligence',
          text: `${report.details || ''}\n\n**Arbitrage Opportunities:** ${report.arbitrage_count || 0}\n**Line Movement Alerts:** ${report.line_movements || 0}\n**Correlation Updates:** ${report.correlations || 0}\n\n[View Full Report](${process.env.EQ12_DASHBOARD}/reports/${sha})`
        },
        actions: [{
          label: 'View EQ12 Dashboard',
          description: 'Open premium sports betting intelligence dashboard',
          identifier: 'view_dashboard'
        }]
      });

    } catch (error) {
      app.log.error(`Error processing ${owner}/${repo}:`, error);

      return ctx.octokit.checks.create({
        owner,
        repo,
        name: 'EQ12 Analysis',
        head_sha: sha,
        status: 'completed',
        conclusion: 'failure',
        output: {
          title: 'EQ12 Analysis Failed',
          summary: 'Unable to complete premium analysis. Please try again or contact support.',
          text: `Error: ${error.message}\n\nIf this persists, reach out to support@eq12.com`
        }
      });
    }
  });

  // Handle check suite events for additional monetization opportunities
  app.on('check_suite', async (ctx) => {
    if (ctx.payload.action === 'completed') {
      const { owner, repo } = ctx.repo();
      app.log.info(`Check suite completed for ${owner}/${repo}`);

      // Opportunity to upsell premium features
      // Track usage metrics for billing
    }
  });

  // Handle installation events for onboarding
  app.on(['installation.created', 'installation_repositories.added'], async (ctx) => {
    const installation = ctx.payload.installation;
    app.log.info(`EQ12 App installed for account: ${installation.account.login}`);

    // Send welcome message and setup instructions
    // Initialize free trial credits
  });
};
