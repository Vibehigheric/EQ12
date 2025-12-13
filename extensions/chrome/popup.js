/**
 * EQ12 Developer Suite - Popup Script
 * Handles UI interactions and revenue tracking
 */

class EQ12PopupManager {
    constructor() {
        this.settings = null;
        this.revenueStats = null;

        this.initializePopup();
        this.setupEventListeners();
        this.loadUserData();
    }

    async initializePopup() {
        // Load user settings
        const stored = await chrome.storage.sync.get('eq12Settings');
        this.settings = stored.eq12Settings || {};

        // Get revenue stats from background
        chrome.runtime.sendMessage({ action: 'getRevenueStats' }, (response) => {
            if (response.success) {
                this.revenueStats = response.stats;
                this.updateUI();
            }
        });

        // Update subscription badge
        this.updateSubscriptionBadge();

        // Update feature availability
        this.updateFeatureAvailability();
    }

    setupEventListeners() {
        // API Key validation
        document.getElementById('validateBtn').addEventListener('click', this.validateAPIKey.bind(this));
        document.getElementById('apiKeyInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.validateAPIKey();
        });

        // Feature buttons
        document.getElementById('aiReviewBtn').addEventListener('click', this.handleAIReview.bind(this));
        document.getElementById('costAnalyzeBtn').addEventListener('click', this.handleCostAnalysis.bind(this));
        document.getElementById('suggestionsBtn').addEventListener('click', this.handleSmartSuggestions.bind(this));

        // Upgrade button
        document.getElementById('upgradeBtn').addEventListener('click', this.handleUpgrade.bind(this));

        // Footer links
        document.getElementById('docsLink').addEventListener('click', () => {
            chrome.tabs.create({ url: 'https://docs.eq12.com' });
        });
        document.getElementById('supportLink').addEventListener('click', () => {
            chrome.tabs.create({ url: 'https://eq12.com/support' });
        });
        document.getElementById('settingsLink').addEventListener('click', () => {
            chrome.runtime.openOptionsPage();
        });
    }

    async loadUserData() {
        const stored = await chrome.storage.sync.get('eq12Settings');
        if (stored.eq12Settings) {
            this.settings = stored.eq12Settings;

            // Populate API key if exists
            if (this.settings.apiKey) {
                document.getElementById('apiKeyInput').value = '••••••••••••••••';
            }

            // Update stats
            this.updateQuickStats();
        }
    }

    updateSubscriptionBadge() {
        const badge = document.getElementById('subscriptionBadge');
        const subscription = this.settings?.subscription || 'free';

        badge.textContent = subscription.toUpperCase();
        badge.className = `subscription-badge ${subscription}`;
    }

    updateFeatureAvailability() {
        const subscription = this.settings?.subscription || 'free';
        const features = this.settings?.features || {};

        // AI Code Review
        const aiReviewBtn = document.getElementById('aiReviewBtn');
        if (!features.aiCodeReview) {
            aiReviewBtn.textContent = 'Pro Only';
            aiReviewBtn.disabled = true;
            aiReviewBtn.classList.add('pro-only');
        } else {
            aiReviewBtn.textContent = 'Review';
            aiReviewBtn.disabled = false;
            aiReviewBtn.classList.remove('pro-only');
        }

        // Smart Suggestions
        const suggestionsBtn = document.getElementById('suggestionsBtn');
        if (!features.smartSuggestions) {
            suggestionsBtn.textContent = 'Pro Only';
            suggestionsBtn.disabled = true;
            suggestionsBtn.classList.add('pro-only');
        } else {
            suggestionsBtn.textContent = 'Get Tips';
            suggestionsBtn.disabled = false;
            suggestionsBtn.classList.remove('pro-only');
        }

        // Show/hide upgrade prompt
        const upgradePrompt = document.getElementById('upgradePrompt');
        if (subscription === 'free') {
            upgradePrompt.style.display = 'block';
        } else {
            upgradePrompt.style.display = 'none';
        }
    }

    updateQuickStats() {
        const usage = this.settings?.usage || {};

        document.getElementById('totalRequests').textContent = usage.totalRequests || 0;
        document.getElementById('aiRequests').textContent = usage.aiRequests || 0;

        // Calculate estimated cost savings
        const estimatedSavings = (usage.totalRequests || 0) * 0.15; // $0.15 per optimization
        document.getElementById('costsSaved').textContent = `$${estimatedSavings.toFixed(0)}`;
    }

    updateUI() {
        if (this.revenueStats) {
            // Update revenue indicator
            const revenueAmount = document.getElementById('revenueAmount');
            const dailyRevenue = this.calculateDailyRevenue();
            revenueAmount.textContent = dailyRevenue.toFixed(2);

            // Show conversion triggers
            this.showConversionTriggers();
        }
    }

    calculateDailyRevenue() {
        const subscription = this.settings?.subscription || 'free';
        const pricing = { free: 0, pro: 29.99, enterprise: 99.99 };
        return pricing[subscription] / 30; // Daily revenue
    }

    showConversionTriggers() {
        if (this.revenueStats?.conversionTriggers?.length > 0) {
            const trigger = this.revenueStats.conversionTriggers[0];
            this.showMessage(trigger.message, trigger.urgency === 'high' ? 'success' : 'info');
        }
    }

    async validateAPIKey() {
        const apiKeyInput = document.getElementById('apiKeyInput');
        const validateBtn = document.getElementById('validateBtn');
        const apiKey = apiKeyInput.value.trim();

        if (!apiKey || apiKey === '••••••••••••••••') {
            this.showMessage('Please enter a valid API key', 'error');
            return;
        }

        validateBtn.textContent = '⏳';
        validateBtn.disabled = true;

        try {
            // Validate with background service
            chrome.runtime.sendMessage({
                action: 'validateLicense',
                data: { apiKey: apiKey }
            }, async (response) => {
                if (response.success) {
                    const validation = response.validation;

                    // Update settings
                    this.settings.apiKey = apiKey;
                    this.settings.subscription = validation.plan;
                    this.settings.features = validation.features || {};

                    await chrome.storage.sync.set({ eq12Settings: this.settings });

                    // Update UI
                    this.updateSubscriptionBadge();
                    this.updateFeatureAvailability();

                    // Mask API key
                    apiKeyInput.value = '••••••••••••••••';

                    this.showMessage(`License validated! ${validation.plan.toUpperCase()} plan activated.`, 'success');

                    // Track conversion
                    if (validation.plan !== 'free') {
                        this.trackConversion(validation.plan);
                    }
                } else {
                    this.showMessage('Invalid API key. Please try again.', 'error');
                }

                validateBtn.textContent = '✓';
                validateBtn.disabled = false;
            });

        } catch (error) {
            console.error('License validation failed:', error);
            this.showMessage('Validation failed. Please try again.', 'error');
            validateBtn.textContent = '✓';
            validateBtn.disabled = false;
        }
    }

    async handleAIReview() {
        const subscription = this.settings?.subscription || 'free';

        if (subscription === 'free') {
            this.showUpgradeModal('AI Code Review', 'Get instant AI-powered code reviews with detailed suggestions and security analysis.');
            return;
        }

        // Get current tab to analyze
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url.includes('github.com')) {
            this.showMessage('Navigate to a GitHub repository to use AI Review', 'info');
            return;
        }

        this.showMessage('Analyzing code... This may take a moment.', 'info');

        // Inject content script to get code
        try {
            const results = await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: this.extractCodeFromPage
            });

            if (results[0]?.result?.code) {
                const { code, language } = results[0].result;

                chrome.runtime.sendMessage({
                    action: 'getAICodeReview',
                    data: { code, language, repository: this.extractRepoFromURL(tab.url) }
                }, (response) => {
                    if (response.success && response.review) {
                        this.displayAIReview(response.review);
                    } else {
                        this.showMessage('AI review failed. Please try again.', 'error');
                    }
                });
            } else {
                this.showMessage('No code found on this page', 'error');
            }
        } catch (error) {
            this.showMessage('Failed to analyze code. Please refresh and try again.', 'error');
        }
    }

    async handleCostAnalysis() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab.url.includes('github.com')) {
            this.showMessage('Navigate to a GitHub repository to analyze costs', 'info');
            return;
        }

        const repo = this.extractRepoFromURL(tab.url);
        if (!repo) {
            this.showMessage('Invalid GitHub repository URL', 'error');
            return;
        }

        this.showMessage('Analyzing repository costs...', 'info');

        chrome.runtime.sendMessage({
            action: 'analyzeRepositoryCosts',
            data: {
                owner: repo.split('/')[0],
                repo: repo.split('/')[1],
                githubToken: null // Would need GitHub token for full analysis
            }
        }, (response) => {
            if (response.success) {
                this.displayCostAnalysis(response.costAnalysis);
            } else {
                this.showMessage('Cost analysis failed. Try connecting GitHub token in settings.', 'error');
            }
        });
    }

    async handleSmartSuggestions() {
        const subscription = this.settings?.subscription || 'free';

        if (subscription === 'free') {
            this.showUpgradeModal('Smart Suggestions', 'Get personalized workflow optimization suggestions based on your development patterns.');
            return;
        }

        // Implementation for smart suggestions
        this.showMessage('Generating smart suggestions...', 'info');

        // Would integrate with AI service for personalized suggestions
        setTimeout(() => {
            this.showMessage('Smart suggestions coming soon!', 'success');
        }, 2000);
    }

    handleUpgrade() {
        // Track upgrade intent
        this.trackEvent('upgrade_intent', { source: 'popup_button' });

        chrome.tabs.create({
            url: 'https://eq12.com/pricing?source=chrome-extension&plan=pro'
        });
    }

    showUpgradeModal(feature, description) {
        const modal = `
            <div style="position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:10000;display:flex;align-items:center;justify-content:center;">
                <div style="background:white;padding:20px;border-radius:8px;max-width:400px;text-align:center;">
                    <h3>🚀 Upgrade to EQ12 Pro</h3>
                    <p><strong>${feature}</strong></p>
                    <p>${description}</p>
                    <div style="margin:20px 0;">
                        <span style="font-size:24px;font-weight:bold;">$29.99/month</span>
                    </div>
                    <button onclick="chrome.tabs.create({url:'https://eq12.com/pricing'});window.close();" style="background:#007cba;color:white;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;">
                        Upgrade Now
                    </button>
                    <button onclick="this.parentElement.parentElement.remove();" style="margin-left:10px;background:#ccc;border:none;padding:10px 20px;border-radius:4px;cursor:pointer;">
                        Maybe Later
                    </button>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modal);
    }

    displayAIReview(review) {
        // Would display AI review results in a dedicated UI
        console.log('AI Review:', review);
        this.showMessage('AI review completed! Check console for details.', 'success');
    }

    displayCostAnalysis(analysis) {
        const message = `Cost Analysis: $${analysis.totalCost} total, ${analysis.runsAnalyzed} runs analyzed. ${analysis.recommendations.length} recommendations available.`;
        this.showMessage(message, 'success');
    }

    extractCodeFromPage() {
        // Function to run in content script context
        const codeElements = document.querySelectorAll('.blob-code-inner, .highlight pre, code');
        if (codeElements.length > 0) {
            const code = Array.from(codeElements).map(el => el.textContent).join('\n');
            const language = this.detectLanguage() || 'javascript';
            return { code: code.slice(0, 2000), language }; // Limit code size
        }
        return null;
    }

    detectLanguage() {
        const url = window.location.href;
        if (url.includes('.js')) return 'javascript';
        if (url.includes('.py')) return 'python';
        if (url.includes('.ts')) return 'typescript';
        if (url.includes('.java')) return 'java';
        return 'text';
    }

    extractRepoFromURL(url) {
        const match = url.match(/github\.com\/([^/]+\/[^/]+)/);
        return match ? match[1] : null;
    }

    showMessage(message, type = 'info') {
        const statusElement = document.getElementById('statusMessage');
        statusElement.textContent = message;
        statusElement.className = `status-message ${type}`;
        statusElement.style.display = 'block';

        setTimeout(() => {
            statusElement.style.display = 'none';
        }, 5000);
    }

    async trackConversion(plan) {
        chrome.runtime.sendMessage({
            action: 'trackUsage',
            data: {
                feature: 'subscription_conversion',
                metadata: { plan: plan, source: 'popup' }
            }
        });
    }

    async trackEvent(event, data = {}) {
        chrome.runtime.sendMessage({
            action: 'trackUsage',
            data: {
                feature: event,
                metadata: data
            }
        });
    }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EQ12PopupManager();
});
