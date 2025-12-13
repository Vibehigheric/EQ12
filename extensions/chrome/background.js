/**
 * EQ12 Developer Productivity Suite - Background Service Worker
 * Handles license validation, OpenAI integration, and revenue tracking
 */

import { EQ12LicenseValidator } from './eq12-license-validator.js';
import { EQ12OpenAIClient } from './eq12-openai-client.js';

class EQ12BackgroundService {
    constructor() {
        this.licenseValidator = new EQ12LicenseValidator();
        this.openaiClient = new EQ12OpenAIClient();
        this.revenueTracking = {
            installs: 0,
            activeUsers: 0,
            premiumUsers: 0,
            dailyUsage: {}
        };

        this.setupEventListeners();
        this.initializeRevenue();
    }

    setupEventListeners() {
        // Extension installation
        chrome.runtime.onInstalled.addListener(this.handleInstall.bind(this));

        // Messages from content scripts and popup
        chrome.runtime.onMessage.addListener(this.handleMessage.bind(this));

        // Tab updates for GitHub integration
        chrome.tabs.onUpdated.addListener(this.handleTabUpdate.bind(this));

        // Periodic license validation
        chrome.alarms.onAlarm.addListener(this.handleAlarm.bind(this));

        // User activity tracking
        chrome.idle.onStateChanged.addListener(this.handleIdleStateChange.bind(this));
    }

    async handleInstall(details) {
        console.log('🚀 EQ12 Developer Suite installed');

        // Track installation
        this.revenueTracking.installs += 1;
        await this.saveRevenueData();

        // Set up periodic validation
        chrome.alarms.create('validateLicense', {
            delayInMinutes: 1,
            periodInMinutes: 60
        });

        // Show welcome page
        if (details.reason === 'install') {
            chrome.tabs.create({
                url: 'https://eq12.com/welcome?source=chrome-extension'
            });
        }

        // Initialize default settings
        await chrome.storage.sync.set({
            eq12Settings: {
                apiKey: null,
                subscription: 'free',
                features: {
                    aiCodeReview: false,
                    costOptimization: true,
                    smartSuggestions: false,
                    advancedAnalytics: false
                },
                usage: {
                    totalRequests: 0,
                    aiRequests: 0,
                    lastUsed: new Date().toISOString()
                }
            }
        });
    }

    async handleMessage(request, sender, sendResponse) {
        const { action, data } = request;

        try {
            switch (action) {
                case 'validateLicense':
                    const validation = await this.validateUserLicense(data.apiKey);
                    sendResponse({ success: true, validation });
                    break;

                case 'getAICodeReview':
                    const review = await this.getAICodeReview(data);
                    sendResponse({ success: true, review });
                    break;

                case 'analyzeRepositoryCosts':
                    const costAnalysis = await this.analyzeRepositoryCosts(data);
                    sendResponse({ success: true, costAnalysis });
                    break;

                case 'trackUsage':
                    await this.trackFeatureUsage(data.feature, data.metadata);
                    sendResponse({ success: true });
                    break;

                case 'getRevenueStats':
                    const stats = await this.getRevenueStats();
                    sendResponse({ success: true, stats });
                    break;

                default:
                    sendResponse({ success: false, error: 'Unknown action' });
            }
        } catch (error) {
            console.error('Background service error:', error);
            sendResponse({ success: false, error: error.message });
        }

        return true; // Keep message channel open for async response
    }

    async handleTabUpdate(tabId, changeInfo, tab) {
        if (changeInfo.status === 'complete' && tab.url?.includes('github.com')) {
            // Inject GitHub enhancements
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tabId },
                    files: ['content-github.js']
                });

                // Track GitHub usage
                await this.trackFeatureUsage('github_page_view', {
                    url: tab.url,
                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                console.debug('Script injection failed:', error);
            }
        }
    }

    async handleAlarm(alarm) {
        if (alarm.name === 'validateLicense') {
            const settings = await chrome.storage.sync.get('eq12Settings');
            if (settings.eq12Settings?.apiKey) {
                const validation = await this.validateUserLicense(settings.eq12Settings.apiKey);

                // Update local settings with validation result
                settings.eq12Settings.subscription = validation.plan;
                settings.eq12Settings.features = this.getAvailableFeatures(validation.plan);
                await chrome.storage.sync.set({ eq12Settings: settings.eq12Settings });
            }
        }
    }

    async handleIdleStateChange(state) {
        if (state === 'active') {
            await this.trackFeatureUsage('user_active', {
                timestamp: new Date().toISOString()
            });
        }
    }

    async validateUserLicense(apiKey) {
        return await this.licenseValidator.validate(apiKey, {
            github_username: 'chrome_extension_user',
            repo: 'browser_extension',
            action: 'chrome_extension_validation'
        });
    }

    async getAICodeReview(data) {
        const { code, language, repository } = data;

        // Check subscription level
        const settings = await chrome.storage.sync.get('eq12Settings');
        const subscription = settings.eq12Settings?.subscription || 'free';

        if (subscription === 'free') {
            return {
                available: false,
                message: 'AI Code Review requires EQ12 Pro subscription',
                upgradeUrl: 'https://eq12.com/pricing?feature=ai-code-review'
            };
        }

        // Perform AI code review using secure OpenAI integration
        const review = await this.openaiClient.getCodeReview(code, language, {
            repository: repository,
            subscription: subscription
        });

        // Track usage
        await this.trackFeatureUsage('ai_code_review', {
            language: language,
            codeLength: code.length,
            repository: repository
        });

        return review;
    }

    async analyzeRepositoryCosts(data) {
        const { owner, repo, githubToken } = data;

        try {
            // Fetch repository workflow data
            const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/actions/runs`, {
                headers: {
                    'Authorization': `token ${githubToken}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch repository data');
            }

            const workflowData = await response.json();

            // Analyze costs (similar to GitHub Action logic)
            const costAnalysis = this.calculateWorkflowCosts(workflowData.workflow_runs);

            // Track usage
            await this.trackFeatureUsage('cost_analysis', {
                repository: `${owner}/${repo}`,
                runsAnalyzed: workflowData.workflow_runs.length
            });

            return costAnalysis;

        } catch (error) {
            throw new Error(`Cost analysis failed: ${error.message}`);
        }
    }

    calculateWorkflowCosts(runs) {
        let totalCost = 0;
        let totalMinutes = 0;
        const costByRunner = {};

        // GitHub runner cost rates
        const rates = {
            'ubuntu': 0.008,
            'windows': 0.016,
            'macos': 0.08
        };

        runs.forEach(run => {
            // Estimate costs based on runner and duration
            // In real implementation, would fetch job details
            const estimatedDuration = 10; // minutes
            const runnerType = 'ubuntu'; // default assumption
            const runCost = estimatedDuration * rates[runnerType];

            totalCost += runCost;
            totalMinutes += estimatedDuration;
            costByRunner[runnerType] = (costByRunner[runnerType] || 0) + runCost;
        });

        return {
            totalCost: totalCost.toFixed(2),
            totalMinutes: Math.round(totalMinutes),
            avgCostPerRun: (totalCost / runs.length).toFixed(2),
            costByRunner: costByRunner,
            runsAnalyzed: runs.length,
            recommendations: this.generateCostRecommendations(totalCost, costByRunner)
        };
    }

    generateCostRecommendations(totalCost, costByRunner) {
        const recommendations = [];

        if (costByRunner.macos > totalCost * 0.3) {
            recommendations.push({
                type: 'runner_optimization',
                title: 'Reduce macOS runner usage',
                impact: 'high',
                savings: (costByRunner.macos * 0.8).toFixed(2)
            });
        }

        if (totalCost > 50) {
            recommendations.push({
                type: 'caching',
                title: 'Implement dependency caching',
                impact: 'medium',
                savings: (totalCost * 0.3).toFixed(2)
            });
        }

        return recommendations;
    }

    async trackFeatureUsage(feature, metadata = {}) {
        const today = new Date().toDateString();

        // Update daily usage
        if (!this.revenueTracking.dailyUsage[today]) {
            this.revenueTracking.dailyUsage[today] = {};
        }

        this.revenueTracking.dailyUsage[today][feature] =
            (this.revenueTracking.dailyUsage[today][feature] || 0) + 1;

        // Update user settings
        const settings = await chrome.storage.sync.get('eq12Settings');
        if (settings.eq12Settings) {
            settings.eq12Settings.usage.totalRequests += 1;
            settings.eq12Settings.usage.lastUsed = new Date().toISOString();

            if (feature.includes('ai')) {
                settings.eq12Settings.usage.aiRequests += 1;
            }

            await chrome.storage.sync.set({ eq12Settings: settings.eq12Settings });
        }

        await this.saveRevenueData();

        // Report to license server
        try {
            const apiKey = settings.eq12Settings?.apiKey;
            if (apiKey) {
                await fetch('https://api.eq12.com/license/consume', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${apiKey}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        github_username: 'chrome_extension_user',
                        action: feature,
                        metadata: {
                            ...metadata,
                            source: 'chrome_extension',
                            version: chrome.runtime.getManifest().version
                        }
                    })
                });
            }
        } catch (error) {
            console.debug('Usage reporting failed:', error);
        }
    }

    getAvailableFeatures(subscription) {
        const features = {
            free: {
                aiCodeReview: false,
                costOptimization: true,
                smartSuggestions: false,
                advancedAnalytics: false
            },
            pro: {
                aiCodeReview: true,
                costOptimization: true,
                smartSuggestions: true,
                advancedAnalytics: true
            },
            enterprise: {
                aiCodeReview: true,
                costOptimization: true,
                smartSuggestions: true,
                advancedAnalytics: true,
                teamFeatures: true,
                customIntegrations: true
            }
        };

        return features[subscription] || features.free;
    }

    async initializeRevenue() {
        const stored = await chrome.storage.local.get('revenueTracking');
        if (stored.revenueTracking) {
            this.revenueTracking = { ...this.revenueTracking, ...stored.revenueTracking };
        }
    }

    async saveRevenueData() {
        await chrome.storage.local.set({ revenueTracking: this.revenueTracking });
    }

    async getRevenueStats() {
        const settings = await chrome.storage.sync.get('eq12Settings');
        const subscription = settings.eq12Settings?.subscription || 'free';

        return {
            subscription: subscription,
            usage: settings.eq12Settings?.usage || {},
            dailyUsage: this.revenueTracking.dailyUsage,
            monetizationOpportunities: this.getMonetizationOpportunities(subscription),
            conversionTriggers: this.getConversionTriggers(settings.eq12Settings?.usage || {})
        };
    }

    getMonetizationOpportunities(subscription) {
        if (subscription === 'free') {
            return [
                {
                    feature: 'AI Code Review',
                    description: 'Get instant AI-powered code reviews',
                    value: '$29.99/month',
                    cta: 'Upgrade to Pro'
                },
                {
                    feature: 'Advanced Analytics',
                    description: 'Deep insights into your development patterns',
                    value: '$29.99/month',
                    cta: 'Upgrade to Pro'
                }
            ];
        } else if (subscription === 'pro') {
            return [
                {
                    feature: 'Team Collaboration',
                    description: 'Share insights with your development team',
                    value: '$99.99/month',
                    cta: 'Upgrade to Enterprise'
                }
            ];
        }

        return [];
    }

    getConversionTriggers(usage) {
        const triggers = [];

        // High usage trigger
        if (usage.totalRequests > 50) {
            triggers.push({
                type: 'high_usage',
                message: 'You\'re a power user! Upgrade for unlimited features.',
                urgency: 'medium'
            });
        }

        // AI interest trigger
        if (usage.aiRequests > 5 && usage.aiRequests < 10) {
            triggers.push({
                type: 'ai_interest',
                message: 'Loving AI features? Get unlimited AI with Pro!',
                urgency: 'high'
            });
        }

        return triggers;
    }
}

// Initialize background service
new EQ12BackgroundService();
