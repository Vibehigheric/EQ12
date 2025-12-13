/**
 * EQ12 Data Pusher - Enhanced Background Script
 * Handles extension lifecycle, EQ12 backend API communication, and automated data capture
 */

class EQ12BackgroundScript {
    constructor() {
        this.apiEndpoint = 'http://localhost:8000/api';
        this.captureStats = {
            odds: 0,
            deals: 0,
            tickets: 0,
            finance: 0,
            total: 0
        };

        this.setupListeners();
        this.startPeriodicTasks();
        this.checkApiStatus(); // Initial status check
    }

    setupListeners() {
        // Handle messages from content scripts and popup
        browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep channel open for async response
        });

        // Handle tab updates for auto-capture
        browser.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            if (changeInfo.status === 'complete' && tab.url) {
                this.handleTabUpdate(tabId, tab);
            }
        });

        // Add context menu items
        this.setupContextMenus();

        // Handle extension install/startup
        browser.runtime.onInstalled.addListener((details) => {
            this.handleInstall(details);
        });
    }

    handleInstall(details) {
        console.log('📦 EQ12 Extension installed/updated:', details);

        // Set default settings
        browser.storage.local.set({
            auto_capture: false,
            affiliate_injection: true,
            ai_analysis: true,
            eq12_stats: this.captureStats,
            affiliate_config: {
                stubhub: { id: 'EQ12STUBHUB', param: 'ref' },
                expedia: { id: 'EQ12EXPEDIA', param: 'SEMCID' },
                booking: { id: 'EQ12BOOKING', param: 'aid' },
                kayak: { id: 'EQ12KAYAK', param: 'a' },
                draftkings: { id: 'EQ12DK', param: 'wpcid' },
                fanduel: { id: 'EQ12FD', param: 'pfm' }
            }
        });

        // Show welcome notification for new installs
        if (details.reason === 'install') {
            browser.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon-48.png',
                title: 'EQ12 Data Pusher Installed!',
                message: 'Connected to EQ12 automation hub. Click toolbar icon to start capturing data.'
            });
        }
    }

    setupContextMenus() {
        browser.contextMenus.create({
            id: 'eq12-capture-odds',
            title: 'Capture Odds Data for EQ12',
            contexts: ['page'],
            documentUrlPatterns: [
                '*://*.draftkings.com/*',
                '*://*.fanduel.com/*',
                '*://*.betmgm.com/*',
                '*://*.caesars.com/*',
                '*://*.barstoolsportsbook.com/*'
            ]
        });

        browser.contextMenus.create({
            id: 'eq12-capture-deals',
            title: 'Capture Travel Deals for EQ12',
            contexts: ['page'],
            documentUrlPatterns: [
                '*://*.expedia.com/*',
                '*://*.booking.com/*',
                '*://*.kayak.com/*',
                '*://*.priceline.com/*',
                '*://*.hotels.com/*'
            ]
        });

        browser.contextMenus.create({
            id: 'eq12-capture-tickets',
            title: 'Capture Ticket Data for EQ12',
            contexts: ['page'],
            documentUrlPatterns: [
                '*://*.stubhub.com/*',
                '*://*.ticketmaster.com/*',
                '*://*.seatgeek.com/*',
                '*://*.vividseats.com/*'
            ]
        });

        browser.contextMenus.onClicked.addListener((info, tab) => {
            this.handleContextMenu(info, tab);
        });
    }

    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.type) {
                case 'CAPTURE_DATA':
                    const result = await this.captureData(message.data, sender.tab);
                    sendResponse({ success: true, result });
                    break;

                case 'GET_STATS':
                    const stats = await this.getUpdatedStats();
                    sendResponse({ success: true, stats });
                    break;

                case 'CHECK_API_STATUS':
                    const status = await this.checkApiStatus();
                    sendResponse({ success: true, status });
                    break;

                case 'AUTO_CAPTURE':
                    if (message.enabled) {
                        this.enableAutoCapture(sender.tab);
                    } else {
                        this.disableAutoCapture(sender.tab.id);
                    }
                    sendResponse({ success: true });
                    break;

                case 'INJECT_AFFILIATES':
                    await this.injectAffiliateLinks(sender.tab);
                    sendResponse({ success: true });
                    break;

                default:
                    sendResponse({ success: false, error: 'Unknown message type' });
            }
        } catch (error) {
            console.error('Background script error:', error);
            sendResponse({ success: false, error: error.message });
        }
    }

    async handleTabUpdate(tabId, tab) {
        // Check if auto-capture is enabled for this tab
        const settings = await browser.storage.local.get(['auto_capture', 'captureSettings']);

        if (settings.auto_capture && this.isSupportedSite(tab.url)) {
            // Update badge to show site is supported
            browser.browserAction.setBadgeText({
                text: '●',
                tabId: tabId
            });
            browser.browserAction.setBadgeBackgroundColor({
                color: '#00ff88'
            });

            // Inject content script if not already present
            try {
                await browser.tabs.executeScript(tabId, {
                    file: '/content.js',
                    runAt: 'document_end'
                });

                // Trigger auto-capture after a delay
                setTimeout(() => {
                    browser.tabs.sendMessage(tabId, {
                        type: 'AUTO_CAPTURE_REQUEST',
                        settings: settings.captureSettings || {}
                    });
                }, 3000); // Allow page to fully load

            } catch (error) {
                console.log('Content script injection skipped:', error.message);
            }
        } else {
            // Clear badge for unsupported sites
            browser.browserAction.setBadgeText({
                text: '',
                tabId: tabId
            });
        }
    }

    isSupportedSite(url) {
        const supportedDomains = [
            'draftkings.com', 'fanduel.com', 'betmgm.com', 'caesars.com', 'barstoolsportsbook.com',
            'expedia.com', 'booking.com', 'kayak.com', 'priceline.com', 'hotels.com',
            'stubhub.com', 'ticketmaster.com', 'seatgeek.com', 'vividseats.com',
            'yahoo.com', 'finance.yahoo.com', 'marketwatch.com', 'bloomberg.com'
        ];

        return supportedDomains.some(domain => url.includes(domain));
    }

    async handleContextMenu(info, tab) {
        try {
            switch (info.menuItemId) {
                case 'eq12-capture-odds':
                    await browser.tabs.sendMessage(tab.id, { type: 'MANUAL_ODDS_CAPTURE' });
                    break;

                case 'eq12-capture-deals':
                    await browser.tabs.sendMessage(tab.id, { type: 'MANUAL_DEALS_CAPTURE' });
                    break;

                case 'eq12-capture-tickets':
                    await browser.tabs.sendMessage(tab.id, { type: 'MANUAL_TICKETS_CAPTURE' });
                    break;
            }
        } catch (error) {
            console.error('Context menu action failed:', error);
            this.showErrorNotification('Action Failed', error.message);
        }
    }

    async captureData(data, tab) {
        try {
            // Determine endpoint based on data type using new EQ12 backend structure
            let endpoint = '/firefox/capture/generic';

            if (data.type === 'odds') {
                endpoint = '/firefox/capture/odds';
            } else if (data.type === 'travel_deal') {
                endpoint = '/firefox/capture/travel';
            } else if (data.type === 'financial') {
                endpoint = '/firefox/capture/financial';
            } else if (data.type === 'tickets') {
                endpoint = '/firefox/capture/tickets';
            }

            // Prepare data payload matching EQ12 backend models
            const payload = this.formatDataForBackend(data, tab);

            const response = await fetch(this.apiEndpoint + endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'eq12-extension-key'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            // Update local stats
            this.updateCaptureStats(data.type);

            // Show notification on successful capture with AI insights
            this.showCaptureNotification(data.type, result);

            // Store capture history for analytics
            this.storeCaptureHistory(data, result, tab);

            return result;

        } catch (error) {
            console.error('EQ12 data capture failed:', error);
            this.showErrorNotification('EQ12 Capture Failed', error.message);
            throw error;
        }
    }

    formatDataForBackend(data, tab) {
        const baseData = {
            url: tab.url,
            domain: new URL(tab.url).hostname,
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
            viewport_size: {
                width: window.screen?.width || 1920,
                height: window.screen?.height || 1080
            }
        };

        // Format specific data types for EQ12 backend models
        if (data.type === 'odds') {
            return {
                ...baseData,
                event_name: data.event_name || `${data.home_team} vs ${data.away_team}`,
                sport: data.sport,
                league: data.league,
                home_team: data.home_team,
                away_team: data.away_team,
                moneyline_home: data.moneyline_home,
                moneyline_away: data.moneyline_away,
                spread_line: data.spread_line,
                spread_home_odds: data.spread_home_odds,
                spread_away_odds: data.spread_away_odds,
                total_line: data.total_line,
                over_odds: data.over_odds,
                under_odds: data.under_odds,
                sportsbook: data.sportsbook || this.detectSportsbook(tab.url),
                market_type: data.market_type || 'pre_game',
                event_date: data.event_date,
                player_props: data.player_props,
                ai_analysis: data.ai_analysis,
                confidence_score: data.confidence_score
            };
        } else if (data.type === 'travel_deal') {
            return {
                ...baseData,
                deal_type: data.deal_type,
                provider: data.provider || this.detectTravelProvider(tab.url),
                destination: data.destination,
                origin: data.origin,
                departure_date: data.departure_date,
                return_date: data.return_date,
                original_price: data.original_price,
                sale_price: data.sale_price,
                discount_percentage: data.discount_percentage,
                currency: data.currency || 'USD',
                availability: data.availability,
                deal_expires: data.deal_expires,
                promo_code: data.promo_code,
                value_score: data.value_score,
                recommendation: data.recommendation
            };
        } else if (data.type === 'financial') {
            return {
                ...baseData,
                data_type: data.data_type,
                symbol: data.symbol,
                name: data.name,
                exchange: data.exchange,
                current_price: data.current_price,
                change_amount: data.change_amount,
                change_percentage: data.change_percentage,
                volume: data.volume,
                market_cap: data.market_cap,
                pe_ratio: data.pe_ratio,
                trend_analysis: data.trend_analysis,
                risk_assessment: data.risk_assessment
            };
        } else if (data.type === 'tickets') {
            return {
                ...baseData,
                event_name: data.event_name,
                event_type: data.event_type,
                venue: data.venue,
                event_date: data.event_date,
                section: data.section,
                row: data.row,
                seat_numbers: data.seat_numbers,
                quantity: data.quantity,
                face_value: data.face_value,
                listed_price: data.listed_price,
                fees: data.fees,
                total_price: data.total_price,
                seller_platform: data.seller_platform || this.detectTicketPlatform(tab.url),
                seller_rating: data.seller_rating,
                market_value: data.market_value,
                value_rating: data.value_rating
            };
        }

        // Generic data fallback
        return {
            ...baseData,
            page_title: tab.title,
            meta_description: data.meta_description,
            structured_data: data.structured_data,
            key_metrics: data.key_metrics,
            text_content: data.text_content,
            content_category: data.content_category,
            relevance_score: data.relevance_score
        };
    }

    detectSportsbook(url) {
        const domain = new URL(url).hostname.toLowerCase();
        if (domain.includes('draftkings')) return 'DraftKings';
        if (domain.includes('fanduel')) return 'FanDuel';
        if (domain.includes('betmgm')) return 'BetMGM';
        if (domain.includes('caesars')) return 'Caesars';
        if (domain.includes('barstool')) return 'Barstool Sportsbook';
        return 'Unknown';
    }

    detectTravelProvider(url) {
        const domain = new URL(url).hostname.toLowerCase();
        if (domain.includes('expedia')) return 'Expedia';
        if (domain.includes('booking')) return 'Booking.com';
        if (domain.includes('kayak')) return 'Kayak';
        if (domain.includes('priceline')) return 'Priceline';
        if (domain.includes('hotels')) return 'Hotels.com';
        return 'Unknown';
    }

    detectTicketPlatform(url) {
        const domain = new URL(url).hostname.toLowerCase();
        if (domain.includes('stubhub')) return 'StubHub';
        if (domain.includes('ticketmaster')) return 'Ticketmaster';
        if (domain.includes('seatgeek')) return 'SeatGeek';
        if (domain.includes('vivid')) return 'Vivid Seats';
        return 'Unknown';
    }

    async storeCaptureHistory(data, result, tab) {
        try {
            const { captureHistory = [] } = await browser.storage.local.get('captureHistory');

            captureHistory.push({
                timestamp: new Date().toISOString(),
                type: data.type,
                url: tab.url,
                domain: new URL(tab.url).hostname,
                success: result.success,
                record_id: result.record_id,
                ai_insights: result.ai_insights,
                processing_time: result.processing_time
            });

            // Keep only last 100 captures in memory
            if (captureHistory.length > 100) {
                captureHistory.splice(0, captureHistory.length - 100);
            }

            await browser.storage.local.set({ captureHistory });
        } catch (error) {
            console.error('Failed to store capture history:', error);
        }
    }

    updateCaptureStats(type) {
        if (type === 'odds') this.captureStats.odds++;
        else if (type === 'travel_deal') this.captureStats.deals++;
        else if (type === 'tickets') this.captureStats.tickets++;
        else if (type === 'financial') this.captureStats.finance++;

        this.captureStats.total++;

        // Save to storage
        browser.storage.local.set({ eq12_stats: this.captureStats });
    }

    async getUpdatedStats() {
        // Try to sync with backend first
        try {
            const status = await this.checkApiStatus();
            if (status.connected && status.firefox_integration && status.capture_stats) {
                this.captureStats = {
                    odds: status.capture_stats.odds || 0,
                    deals: status.capture_stats.travel || 0,
                    tickets: status.capture_stats.tickets || 0,
                    finance: status.capture_stats.financial || 0,
                    total: Object.values(status.capture_stats).reduce((sum, val) => sum + (val || 0), 0)
                };
            }
        } catch (error) {
            console.log('Could not sync stats with backend, using local stats');
        }

        return this.captureStats;
    }

    async checkApiStatus() {
        try {
            // First check main EQ12 backend health
            const healthResponse = await fetch(this.apiEndpoint + '/health', {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });

            let backendStatus = { connected: false };

            if (healthResponse.ok) {
                const healthData = await healthResponse.json();
                backendStatus = {
                    connected: true,
                    status: healthData.status,
                    uptime: healthData.uptime,
                    database: healthData.database_status,
                    version: healthData.version || '2.0.0-gpt5'
                };
            }

            // Check Firefox extension specific endpoints
            try {
                const firefoxResponse = await fetch(this.apiEndpoint + '/firefox/status', {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' }
                });

                if (firefoxResponse.ok) {
                    const firefoxData = await firefoxResponse.json();
                    return {
                        ...backendStatus,
                        firefox_integration: true,
                        capture_stats: firefoxData.capture_stats,
                        last_capture: firefoxData.last_capture,
                        recommendations: firefoxData.recommendations
                    };
                }
            } catch (firefoxError) {
                console.warn('Firefox extension endpoints not available:', firefoxError.message);
            }

            return {
                ...backendStatus,
                firefox_integration: false
            };

        } catch (error) {
            console.error('EQ12 Backend connection failed:', error);
            return {
                connected: false,
                error: error.message,
                firefox_integration: false
            };
        }
    }

    showCaptureNotification(type, result) {
        const typeNames = {
            odds: '⚡ Odds Data',
            travel_deal: '✈️ Travel Deal',
            financial: '📈 Financial Data',
            tickets: '🎫 Ticket Deal'
        };

        let message = `${typeNames[type] || 'Data'} sent to EQ12 Hub`;

        // Add AI insights to notification if available
        if (result.ai_insights) {
            if (result.ai_insights.edge_detected) {
                message += ' - Betting edge detected!';
            } else if (result.ai_insights.deal_quality === 'excellent') {
                message += ' - Excellent deal found!';
            } else if (result.ai_insights.volatility === 'high') {
                message += ' - High volatility detected';
            } else if (result.ai_insights.value_rating === 'excellent') {
                message += ' - Great value detected!';
            }
        }

        browser.notifications.create({
            type: 'basic',
            iconUrl: '/icons/icon-48.png',
            title: 'EQ12 Data Capture',
            message: message
        });
    }

    showErrorNotification(title, message) {
        browser.notifications.create({
            type: 'basic',
            iconUrl: '/icons/icon-48.png',
            title: title,
            message: message
        });
    }

    async injectAffiliateLinks(tab) {
        try {
            // Get affiliate configuration
            const { affiliate_config } = await browser.storage.local.get('affiliate_config');

            if (affiliate_config && tab.url) {
                const domain = new URL(tab.url).hostname.toLowerCase();

                // Check if we have affiliate configuration for this domain
                let affiliateId = null;
                let paramName = null;

                for (const [key, config] of Object.entries(affiliate_config)) {
                    if (domain.includes(key)) {
                        affiliateId = config.id;
                        paramName = config.param;
                        break;
                    }
                }

                if (affiliateId && paramName) {
                    // Inject affiliate link modification script
                    await browser.tabs.executeScript(tab.id, {
                        code: `
                            // EQ12 Affiliate Link Injection
                            (function() {
                                const links = document.querySelectorAll('a[href]');
                                let modified = 0;

                                links.forEach(link => {
                                    const href = link.href;
                                    if (href && !href.includes('${paramName}=')) {
                                        const separator = href.includes('?') ? '&' : '?';
                                        link.href = href + separator + '${paramName}=${affiliateId}';
                                        modified++;
                                    }
                                });

                                console.log('EQ12: Modified', modified, 'affiliate links');
                                return modified;
                            })();
                        `
                    });
                }
            }
        } catch (error) {
            console.error('Failed to inject affiliate links:', error);
        }
    }

    startPeriodicTasks() {
        console.log('🔄 Starting EQ12 periodic tasks...');

        // Check EQ12 backend status every 5 minutes
        setInterval(async () => {
            const status = await this.checkApiStatus();
            console.log('EQ12 Backend Status Check:', status);

            // Update extension badge based on connection status
            if (status.connected && status.firefox_integration) {
                browser.browserAction.setTitle({
                    title: 'EQ12 Data Pusher - Connected to EQ12 Hub'
                });
            } else if (status.connected) {
                browser.browserAction.setTitle({
                    title: 'EQ12 Data Pusher - Backend Connected (Limited Features)'
                });
            } else {
                browser.browserAction.setTitle({
                    title: 'EQ12 Data Pusher - Disconnected from EQ12 Hub'
                });
            }
        }, 5 * 60 * 1000);

        // Cleanup old data periodically
        setInterval(() => {
            this.cleanupOldData();
        }, 60 * 60 * 1000); // Every hour

        // Sync capture stats with backend periodically
        setInterval(() => {
            this.syncStatsWithBackend();
        }, 15 * 60 * 1000); // Every 15 minutes

        console.log('✅ EQ12 periodic tasks initialized');
    }

    async syncStatsWithBackend() {
        try {
            const status = await this.checkApiStatus();
            if (status.connected && status.firefox_integration && status.capture_stats) {
                // Update local stats with backend stats
                this.captureStats = {
                    odds: status.capture_stats.odds || 0,
                    deals: status.capture_stats.travel || 0,
                    tickets: status.capture_stats.tickets || 0,
                    finance: status.capture_stats.financial || 0,
                    total: Object.values(status.capture_stats).reduce((sum, val) => sum + (val || 0), 0)
                };

                await browser.storage.local.set({ eq12_stats: this.captureStats });
                console.log('📊 Stats synced with EQ12 backend:', this.captureStats);
            }
        } catch (error) {
            console.error('Failed to sync stats with EQ12 backend:', error);
        }
    }

    async cleanupOldData() {
        try {
            // Remove old capture data older than 7 days
            const cutoff = Date.now() - (7 * 24 * 60 * 60 * 1000);

            const { captureHistory } = await browser.storage.local.get('captureHistory');
            if (captureHistory) {
                const cleaned = captureHistory.filter(item =>
                    new Date(item.timestamp).getTime() > cutoff
                );

                await browser.storage.local.set({ captureHistory: cleaned });
                console.log(`🧹 Cleaned up ${captureHistory.length - cleaned.length} old capture records`);
            }
        } catch (error) {
            console.error('Cleanup failed:', error);
        }
    }
}

// Initialize EQ12 background script
console.log('🚀 Loading EQ12 Data Pusher background script...');
const eq12Background = new EQ12BackgroundScript();
