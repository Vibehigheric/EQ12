/**
 * EQ12 Discord Integration - Browser Extension Compatible
 * Cross-browser Discord webhook integration for automated bet notifications
 */

// Configuration constants
const EQ12_DISCORD_CONFIG = {
    WEBHOOK_STORAGE_KEY: 'eq12_discord_webhook_url',
    NOTIFICATION_SETTINGS_KEY: 'eq12_discord_settings',
    DEFAULT_USERNAME: 'EQ12 Browser Bot',
    DEFAULT_AVATAR: 'https://cdn.discordapp.com/emojis/1234567890.png',

    // Notification types
    NOTIFICATION_TYPES: {
        BET_ALERT: 'bet_alert',
        BET_PLACED: 'bet_placed',
        BET_SETTLED: 'bet_settled',
        ERROR: 'error',
        DAILY_SUMMARY: 'daily_summary'
    },

    // Colors for different alert types
    EMBED_COLORS: {
        VALUE: 0x00FF00,    // Green for +EV
        ARBITRAGE: 0xFF6600, // Orange for arbitrage
        BOOST: 0x9966FF,    // Purple for boosts
        ERROR: 0xFF0000,    // Red for errors
        WIN: 0x00FF00,      // Green for wins
        LOSS: 0xFF0000,     // Red for losses
        PUSH: 0xFFFF00,     // Yellow for pushes
        INFO: 0x0099FF      // Blue for info
    },

    // Sport emojis
    SPORT_EMOJIS: {
        'NFL': '🏈', 'NBA': '🏀', 'MLB': '⚾', 'NHL': '🏒',
        'CFB': '🏈', 'NCAAB': '🏀', 'UFC': '🥊', 'SOCCER': '⚽',
        'TENNIS': '🎾', 'UNKNOWN': '🎯'
    }
};

/**
 * Discord Webhook Manager - handles secure webhook operations
 */
class EQ12DiscordWebhook {
    constructor() {
        this.webhookUrl = null;
        this.settings = {};
        this.initialized = false;
    }

    /**
     * Initialize Discord integration with stored settings
     */
    async initialize() {
        try {
            // Load webhook URL from storage
            if (typeof browser !== 'undefined' && browser.storage) {
                // Firefox WebExtensions API
                const result = await browser.storage.local.get([
                    EQ12_DISCORD_CONFIG.WEBHOOK_STORAGE_KEY,
                    EQ12_DISCORD_CONFIG.NOTIFICATION_SETTINGS_KEY
                ]);
                this.webhookUrl = result[EQ12_DISCORD_CONFIG.WEBHOOK_STORAGE_KEY];
                this.settings = result[EQ12_DISCORD_CONFIG.NOTIFICATION_SETTINGS_KEY] || {};
            } else if (typeof chrome !== 'undefined' && chrome.storage) {
                // Chrome Extension API
                const result = await new Promise((resolve) => {
                    chrome.storage.local.get([
                        EQ12_DISCORD_CONFIG.WEBHOOK_STORAGE_KEY,
                        EQ12_DISCORD_CONFIG.NOTIFICATION_SETTINGS_KEY
                    ], resolve);
                });
                this.webhookUrl = result[EQ12_DISCORD_CONFIG.WEBHOOK_STORAGE_KEY];
                this.settings = result[EQ12_DISCORD_CONFIG.NOTIFICATION_SETTINGS_KEY] || {};
            }

            this.initialized = true;
            console.log('🔗 EQ12 Discord integration initialized');

        } catch (error) {
            console.error('❌ Failed to initialize Discord integration:', error);
        }
    }

    /**
     * Store webhook URL securely in extension storage
     */
    async setWebhookUrl(url) {
        if (!this.validateWebhookUrl(url)) {
            throw new Error('Invalid Discord webhook URL');
        }

        this.webhookUrl = url;

        try {
            if (typeof browser !== 'undefined' && browser.storage) {
                await browser.storage.local.set({
                    [EQ12_DISCORD_CONFIG.WEBHOOK_STORAGE_KEY]: url
                });
            } else if (typeof chrome !== 'undefined' && chrome.storage) {
                await new Promise((resolve) => {
                    chrome.storage.local.set({
                        [EQ12_DISCORD_CONFIG.WEBHOOK_STORAGE_KEY]: url
                    }, resolve);
                });
            }

            console.log('✅ Discord webhook URL saved');
        } catch (error) {
            console.error('❌ Failed to save webhook URL:', error);
            throw error;
        }
    }

    /**
     * Validate Discord webhook URL format
     */
    validateWebhookUrl(url) {
        if (!url || typeof url !== 'string') return false;

        try {
            const parsedUrl = new URL(url);
            return parsedUrl.hostname === 'discord.com' ||
                parsedUrl.hostname === 'discordapp.com';
        } catch {
            return false;
        }
    }

    /**
     * Send webhook notification with retry logic
     */
    async sendNotification(payload, retries = 3) {
        if (!this.webhookUrl) {
            console.warn('⚠️ No Discord webhook URL configured');
            return false;
        }

        const finalPayload = {
            username: EQ12_DISCORD_CONFIG.DEFAULT_USERNAME,
            ...payload
        };

        for (let attempt = 1; attempt <= retries; attempt++) {
            try {
                const response = await fetch(this.webhookUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(finalPayload)
                });

                if (response.status === 204) {
                    console.log('✅ Discord notification sent successfully');
                    return true;
                } else if (response.status === 429) {
                    // Rate limited - wait and retry
                    const retryAfter = response.headers.get('Retry-After') || 1;
                    await this.sleep(retryAfter * 1000);
                    continue;
                } else {
                    console.error(`❌ Discord webhook error: ${response.status}`);
                    return false;
                }

            } catch (error) {
                console.error(`❌ Discord notification attempt ${attempt} failed:`, error);

                if (attempt < retries) {
                    await this.sleep(1000 * attempt); // Exponential backoff
                }
            }
        }

        return false;
    }

    /**
     * Create bet alert embed for Discord
     */
    createBetAlertEmbed(betData) {
        const sport = (betData.sport || 'UNKNOWN').toUpperCase();
        const emoji = EQ12_DISCORD_CONFIG.SPORT_EMOJIS[sport] || '🎯';
        const color = EQ12_DISCORD_CONFIG.EMBED_COLORS[betData.alertType] ||
            EQ12_DISCORD_CONFIG.EMBED_COLORS.VALUE;

        return {
            title: `${emoji} ${betData.alertType || 'VALUE'} ALERT`,
            color: color,
            timestamp: new Date().toISOString(),
            fields: [
                {
                    name: '📊 Expected Value',
                    value: `**${(betData.ev || 0).toFixed(2)}%**`,
                    inline: true
                },
                {
                    name: '💰 Recommended Stake',
                    value: `**$${(betData.stake || 0).toFixed(2)}**`,
                    inline: true
                },
                {
                    name: '🎲 Odds',
                    value: `**${(betData.odds || 0).toFixed(2)}**`,
                    inline: true
                },
                {
                    name: '🏪 Sportsbook',
                    value: betData.book || 'Unknown',
                    inline: true
                },
                {
                    name: '🆔 Bet ID',
                    value: `\`${betData.id || 'unknown'}\``,
                    inline: true
                },
                {
                    name: '⏰ Generated',
                    value: `<t:${Math.floor(Date.now() / 1000)}:R>`,
                    inline: true
                }
            ],
            footer: {
                text: 'EQ12 Automated Sports Betting System'
            }
        };
    }

    /**
     * Create bet settlement embed for Discord
     */
    createBetSettlementEmbed(settlementData) {
        const resultConfig = {
            'win': { emoji: '✅', color: EQ12_DISCORD_CONFIG.EMBED_COLORS.WIN, title: 'BET WON' },
            'loss': { emoji: '❌', color: EQ12_DISCORD_CONFIG.EMBED_COLORS.LOSS, title: 'BET LOST' },
            'push': { emoji: '🔄', color: EQ12_DISCORD_CONFIG.EMBED_COLORS.PUSH, title: 'BET PUSHED' },
            'void': { emoji: '⚪', color: 0x888888, title: 'BET VOIDED' }
        };

        const config = resultConfig[settlementData.result] || resultConfig.loss;

        return {
            title: `${config.emoji} ${config.title}`,
            color: config.color,
            timestamp: new Date().toISOString(),
            fields: [
                {
                    name: '📈 Profit/Loss',
                    value: `**$${(settlementData.profitLoss || 0).toFixed(2)}**`,
                    inline: true
                },
                {
                    name: '💳 Payout',
                    value: `**$${(settlementData.payout || 0).toFixed(2)}**`,
                    inline: true
                },
                {
                    name: '🏦 New Balance',
                    value: `**$${(settlementData.newBalance || 0).toFixed(2)}**`,
                    inline: true
                },
                {
                    name: '💰 Original Stake',
                    value: `$${(settlementData.stake || 0).toFixed(2)}`,
                    inline: true
                },
                {
                    name: '🆔 Bet ID',
                    value: `\`${settlementData.id || 'unknown'}\``,
                    inline: true
                },
                {
                    name: '🏈 Sport',
                    value: (settlementData.sport || 'UNKNOWN').toUpperCase(),
                    inline: true
                }
            ],
            footer: {
                text: 'EQ12 Automated Sports Betting System'
            }
        };
    }

    /**
     * Send bet alert notification
     */
    async sendBetAlert(betData) {
        const embed = this.createBetAlertEmbed(betData);

        const payload = {
            content: '🚨 **New Betting Opportunity Detected**',
            embeds: [embed]
        };

        return await this.sendNotification(payload);
    }

    /**
     * Send bet settlement notification
     */
    async sendBetSettlement(settlementData) {
        const embed = this.createBetSettlementEmbed(settlementData);

        const payload = {
            content: `🎯 **Bet Settlement Update**`,
            embeds: [embed]
        };

        return await this.sendNotification(payload);
    }

    /**
     * Send simple text notification
     */
    async sendMessage(message, type = 'info') {
        const typeEmojis = {
            info: '💡',
            success: '✅',
            warning: '⚠️',
            error: '❌'
        };

        const payload = {
            content: `${typeEmojis[type] || '💡'} **EQ12 Extension**\n${message}`
        };

        return await this.sendNotification(payload);
    }

    /**
     * Utility sleep function
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global Discord webhook instance
const eq12Discord = new EQ12DiscordWebhook();

/**
 * Content script integration - for use in sportsbook pages
 */
if (typeof window !== 'undefined' && window.location) {
    // Auto-initialize when script loads
    eq12Discord.initialize();

    // Example usage in content script:
    window.EQ12Discord = {
        // Send bet alert from page content
        alertBetOpportunity: async (betData) => {
            return await eq12Discord.sendBetAlert(betData);
        },

        // Send settlement update
        reportBetSettlement: async (settlementData) => {
            return await eq12Discord.sendBetSettlement(settlementData);
        },

        // Send general message
        notify: async (message, type = 'info') => {
            return await eq12Discord.sendMessage(message, type);
        },

        // Configure webhook URL
        setWebhook: async (url) => {
            return await eq12Discord.setWebhookUrl(url);
        }
    };

    console.log('🎯 EQ12 Discord integration loaded');
}

/**
 * Background script integration - for persistent operations
 */
if (typeof chrome !== 'undefined' && chrome.runtime) {
    // Initialize Discord integration
    eq12Discord.initialize();

    // Listen for messages from content scripts
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === 'discord_notification') {
            const { notificationType, data } = request;

            switch (notificationType) {
                case EQ12_DISCORD_CONFIG.NOTIFICATION_TYPES.BET_ALERT:
                    eq12Discord.sendBetAlert(data).then(sendResponse);
                    break;

                case EQ12_DISCORD_CONFIG.NOTIFICATION_TYPES.BET_SETTLED:
                    eq12Discord.sendBetSettlement(data).then(sendResponse);
                    break;

                default:
                    eq12Discord.sendMessage(data.message, data.type).then(sendResponse);
            }

            return true; // Keep message channel open for async response
        }
    });
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        EQ12DiscordWebhook,
        EQ12_DISCORD_CONFIG,
        eq12Discord
    };
}
