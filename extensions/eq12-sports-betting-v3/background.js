// background.js - Service Worker for WebExtension v3
class EQ12BackgroundService {
    constructor() {
        this.apiUrl = 'https://localhost:3001/api'
        this.wsUrl = 'ws://localhost:3001'
        this.setupListeners()
        this.startOddsMonitoring()
    }

    setupListeners() {
        // Extension installation/startup
        chrome.runtime.onInstalled.addListener((details) => {
            this.handleInstall(details)
        })

        // Tab updates for sportsbook detection
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab)
        })

        // Message passing between content scripts and background
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse)
            return true // Keep message channel open for async responses
        })

        // Alarm for periodic odds updates
        chrome.alarms.onAlarm.addListener((alarm) => {
            this.handleAlarm(alarm)
        })
    }

    async handleInstall(details) {
        console.log('EQ12 Extension installed:', details.reason)

        // Set default configuration
        await chrome.storage.sync.set({
            enabled: true,
            autoDetectParlays: true,
            oddsUpdateInterval: 30, // seconds
            minExpectedValue: 8.0,
            maxRiskLevel: 0.7,
            notifications: true,
            sportsbooks: {
                draftkings: true,
                fanduel: true,
                bet365: true,
                caesars: true,
                mgm: true
            }
        })

        // Create periodic alarm for odds updates
        chrome.alarms.create('updateOdds', {
            delayInMinutes: 0.5,
            periodInMinutes: 0.5
        })

        // Show welcome notification
        this.showNotification('EQ12 Ready', 'Sports betting analysis extension is now active!')
    }

    async handleTabUpdate(tabId, changeInfo, tab) {
        if (changeInfo.status === 'complete' && tab.url) {
            const isSportsbook = this.isSportsbookSite(tab.url)

            if (isSportsbook) {
                console.log('Sportsbook detected:', tab.url)

                // Inject enhanced scripts
                await this.injectEnhancedScripts(tabId)

                // Start monitoring this tab
                this.startTabMonitoring(tabId, tab.url)
            }
        }
    }

    isSportsbookSite(url) {
        const sportsbooks = [
            'draftkings.com',
            'fanduel.com',
            'bet365.com',
            'caesars.com',
            'mgm.com'
        ]

        return sportsbooks.some(book => url.includes(book))
    }

    async injectEnhancedScripts(tabId) {
        try {
            // Inject main content script if not already present
            await chrome.scripting.executeScript({
                target: { tabId },
                files: ['content.js']
            })

            // Inject advanced betting analysis
            await chrome.scripting.executeScript({
                target: { tabId },
                files: ['eq12-api.js']
            })

            console.log('Scripts injected successfully for tab:', tabId)
        } catch (error) {
            console.error('Failed to inject scripts:', error)
        }
    }

    async startTabMonitoring(tabId, url) {
        // Send configuration to content script
        const config = await chrome.storage.sync.get()

        chrome.tabs.sendMessage(tabId, {
            type: 'INIT_MONITORING',
            config: config,
            sportsbook: this.detectSportsbook(url)
        })
    }

    detectSportsbook(url) {
        if (url.includes('draftkings')) return 'draftkings'
        if (url.includes('fanduel')) return 'fanduel'
        if (url.includes('bet365')) return 'bet365'
        if (url.includes('caesars')) return 'caesars'
        if (url.includes('mgm')) return 'mgm'
        return 'unknown'
    }

    async handleMessage(message, sender, sendResponse) {
        try {
            switch (message.type) {
                case 'GET_LIVE_ODDS':
                    const odds = await this.fetchLiveOdds(message.sport)
                    sendResponse({ success: true, data: odds })
                    break

                case 'ANALYZE_PARLAY':
                    const analysis = await this.analyzeParlayWithAI(message.legs)
                    sendResponse({ success: true, data: analysis })
                    break

                case 'DETECTED_PARLAY':
                    await this.handleParlayDetection(message.parlay, sender.tab)
                    sendResponse({ success: true })
                    break

                case 'UPDATE_PREFERENCES':
                    await chrome.storage.sync.set(message.preferences)
                    sendResponse({ success: true })
                    break

                case 'GET_EQ12_RECOMMENDATION':
                    const recommendation = await this.getEQ12Recommendation(message.game)
                    sendResponse({ success: true, data: recommendation })
                    break

                default:
                    sendResponse({ success: false, error: 'Unknown message type' })
            }
        } catch (error) {
            console.error('Message handling error:', error)
            sendResponse({ success: false, error: error.message })
        }
    }

    async handleAlarm(alarm) {
        if (alarm.name === 'updateOdds') {
            await this.updateAllTabsWithLatestOdds()
        }
    }

    async fetchLiveOdds(sport = 'baseball_mlb') {
        try {
            const response = await fetch(`${this.apiUrl}/odds/${sport}`)
            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            return await response.json()
        } catch (error) {
            console.error('Failed to fetch odds:', error)
            return null
        }
    }

    async analyzeParlayWithAI(legs) {
        try {
            const response = await fetch(`${this.apiUrl}/analyze-parlay`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ legs })
            })

            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            return await response.json()
        } catch (error) {
            console.error('Failed to analyze parlay:', error)
            return {
                error: 'Analysis failed',
                recommendation: 'Unable to analyze - check connection to EQ12 backend'
            }
        }
    }

    async handleParlayDetection(parlay, tab) {
        console.log('Parlay detected on', tab.url, ':', parlay)

        // Analyze the detected parlay
        const analysis = await this.analyzeParlayWithAI(parlay.legs)

        // Send analysis back to content script
        chrome.tabs.sendMessage(tab.id, {
            type: 'PARLAY_ANALYSIS',
            parlay: parlay,
            analysis: analysis
        })

        // Show notification if high value
        if (analysis.expectedValue && analysis.expectedValue > 15) {
            this.showNotification(
                '🔥 High Value Parlay Detected!',
                `Expected Value: ${analysis.expectedValue.toFixed(1)}%`
            )
        }
    }

    async getEQ12Recommendation(game) {
        try {
            const response = await fetch(`${this.apiUrl}/recommendation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(game)
            })

            if (!response.ok) throw new Error(`HTTP ${response.status}`)
            return await response.json()
        } catch (error) {
            console.error('Failed to get recommendation:', error)
            return null
        }
    }

    async updateAllTabsWithLatestOdds() {
        try {
            const tabs = await chrome.tabs.query({
                url: [
                    'https://www.draftkings.com/*',
                    'https://www.fanduel.com/*',
                    'https://www.bet365.com/*',
                    'https://www.caesars.com/*',
                    'https://www.mgm.com/*'
                ]
            })

            const odds = await this.fetchLiveOdds()

            if (odds) {
                tabs.forEach(tab => {
                    chrome.tabs.sendMessage(tab.id, {
                        type: 'ODDS_UPDATE',
                        odds: odds
                    }).catch(err => {
                        // Tab might be closed or unresponsive
                        console.log('Failed to send odds update to tab', tab.id)
                    })
                })
            }
        } catch (error) {
            console.error('Failed to update tabs with odds:', error)
        }
    }

    showNotification(title, message) {
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: title,
            message: message,
            priority: 2
        })
    }
}

// Initialize the background service
const eq12Service = new EQ12BackgroundService()

// Export for testing
globalThis.EQ12BackgroundService = EQ12BackgroundService
