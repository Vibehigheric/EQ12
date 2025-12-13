// EQ12 Advanced Tab Manager - Enhanced with MDN Tabs API Best Practices
// Implements sophisticated multi-sportsbook coordination and tab monitoring

class EQ12TabManager {
    constructor() {
        this.activeTabs = new Map();
        this.tabGroups = new Map();
        this.sportsbookSessions = new Map();
        this.tabUpdateQueue = [];
        this.processingQueue = false;

        this.init();
    }

    async init() {
        console.log('🎯 EQ12 Tab Manager initializing...');

        try {
            await this.setupTabListeners();
            await this.discoverExistingTabs();
            await this.setupTabGroups();

            console.log('✅ Tab Manager ready');
        } catch (error) {
            console.error('Tab Manager initialization error:', error);
        }
    }

    async setupTabListeners() {
        // Tab activation listener
        chrome.tabs.onActivated.addListener(async (activeInfo) => {
            await this.handleTabActivated(activeInfo);
        });

        // Tab update listener (URL changes, loading states)
        chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
            await this.handleTabUpdated(tabId, changeInfo, tab);
        });

        // Tab creation listener
        chrome.tabs.onCreated.addListener(async (tab) => {
            await this.handleTabCreated(tab);
        });

        // Tab removal listener
        chrome.tabs.onRemoved.addListener(async (tabId, removeInfo) => {
            await this.handleTabRemoved(tabId, removeInfo);
        });

        // Tab movement listener
        chrome.tabs.onMoved.addListener(async (tabId, moveInfo) => {
            await this.handleTabMoved(tabId, moveInfo);
        });

        // Window focus change listener
        chrome.windows.onFocusChanged.addListener(async (windowId) => {
            await this.handleWindowFocusChanged(windowId);
        });
    }

    async discoverExistingTabs() {
        const tabs = await chrome.tabs.query({});

        for (const tab of tabs) {
            if (this.isSportsbookTab(tab)) {
                await this.registerSportsbookTab(tab);
            }
        }

        console.log(`Discovered ${this.activeTabs.size} existing sportsbook tabs`);
    }

    async setupTabGroups() {
        // Group tabs by sportsbook for better organization
        const sportsbookGroups = {
            'DraftKings': [],
            'FanDuel': [],
            'BetMGM': [],
            'Other': []
        };

        for (const [tabId, tabInfo] of this.activeTabs) {
            const group = this.getSportsbookGroup(tabInfo.sportsbook);
            sportsbookGroups[group].push(tabId);
        }

        // Store group information
        for (const [groupName, tabIds] of Object.entries(sportsbookGroups)) {
            if (tabIds.length > 0) {
                this.tabGroups.set(groupName, {
                    tabIds: tabIds,
                    lastActive: Date.now(),
                    totalTabs: tabIds.length
                });
            }
        }
    }

    async handleTabActivated(activeInfo) {
        try {
            const tab = await chrome.tabs.get(activeInfo.tabId);

            if (this.isSportsbookTab(tab)) {
                await this.activateSportsbookTab(tab);
                await this.updateTabGroups(tab);
            }

            // Update active tab tracking
            this.updateActiveTabStats(tab);

        } catch (error) {
            console.error('Tab activation error:', error);
        }
    }

    async handleTabUpdated(tabId, changeInfo, tab) {
        // Queue updates to prevent overwhelming the system
        this.tabUpdateQueue.push({ tabId, changeInfo, tab });

        if (!this.processingQueue) {
            await this.processUpdateQueue();
        }
    }

    async processUpdateQueue() {
        this.processingQueue = true;

        while (this.tabUpdateQueue.length > 0) {
            const update = this.tabUpdateQueue.shift();
            await this.processTabUpdate(update);
        }

        this.processingQueue = false;
    }

    async processTabUpdate(update) {
        const { tabId, changeInfo, tab } = update;

        try {
            // Handle URL changes
            if (changeInfo.url) {
                await this.handleUrlChange(tabId, changeInfo.url, tab);
            }

            // Handle loading state changes
            if (changeInfo.status === 'complete') {
                await this.handleTabLoadComplete(tabId, tab);
            }

            // Handle title changes
            if (changeInfo.title && this.isSportsbookTab(tab)) {
                await this.updateTabTitle(tabId, changeInfo.title);
            }

            // Handle favicon changes
            if (changeInfo.favIconUrl && this.isSportsbookTab(tab)) {
                await this.updateTabFavicon(tabId, changeInfo.favIconUrl);
            }

        } catch (error) {
            console.error('Tab update processing error:', error);
        }
    }

    async handleUrlChange(tabId, newUrl, tab) {
        const wasSportsbook = this.activeTabs.has(tabId);
        const isSportsbook = this.isSportsbookTab(tab);

        if (wasSportsbook && !isSportsbook) {
            // Tab navigated away from sportsbook
            await this.unregisterSportsbookTab(tabId);
        } else if (!wasSportsbook && isSportsbook) {
            // Tab navigated to sportsbook
            await this.registerSportsbookTab(tab);
        } else if (isSportsbook) {
            // Sportsbook URL changed (different page on same site)
            await this.updateSportsbookTab(tab);
        }
    }

    async handleTabLoadComplete(tabId, tab) {
        if (this.isSportsbookTab(tab)) {
            // Inject or update content script
            await this.injectContentScript(tabId);

            // Start monitoring this tab
            await this.startTabMonitoring(tabId, tab);

            // Update tab badge
            await this.updateTabBadge(tabId, tab);
        }
    }

    async handleTabCreated(tab) {
        console.log(`New tab created: ${tab.id}`);

        if (this.isSportsbookTab(tab)) {
            await this.registerSportsbookTab(tab);
        }
    }

    async handleTabRemoved(tabId, removeInfo) {
        console.log(`Tab removed: ${tabId}`);

        if (this.activeTabs.has(tabId)) {
            await this.unregisterSportsbookTab(tabId);
        }

        // Clean up any monitoring for this tab
        await this.stopTabMonitoring(tabId);
    }

    async handleTabMoved(tabId, moveInfo) {
        console.log(`Tab moved: ${tabId} from ${moveInfo.fromIndex} to ${moveInfo.toIndex}`);

        // Update group information if this is a sportsbook tab
        if (this.activeTabs.has(tabId)) {
            await this.updateTabPosition(tabId, moveInfo);
        }
    }

    async handleWindowFocusChanged(windowId) {
        if (windowId === chrome.windows.WINDOW_ID_NONE) {
            // No window focused
            return;
        }

        try {
            // Get active tab in focused window
            const tabs = await chrome.tabs.query({ active: true, windowId });
            if (tabs.length > 0 && this.isSportsbookTab(tabs[0])) {
                await this.handleWindowSportsbookFocus(tabs[0]);
            }
        } catch (error) {
            console.error('Window focus change error:', error);
        }
    }

    async registerSportsbookTab(tab) {
        const sportsbook = this.detectSportsbook(tab.url);

        const tabInfo = {
            id: tab.id,
            url: tab.url,
            title: tab.title,
            sportsbook: sportsbook,
            windowId: tab.windowId,
            registeredAt: Date.now(),
            lastActive: Date.now(),
            lastScrape: null,
            monitoringActive: false,
            contentScriptInjected: false
        };

        this.activeTabs.set(tab.id, tabInfo);

        // Start session tracking
        await this.startSportsbookSession(tab.id, tabInfo);

        console.log(`Registered ${sportsbook} tab: ${tab.id}`);

        // Notify other components
        await this.broadcastTabRegistration(tabInfo);
    }

    async unregisterSportsbookTab(tabId) {
        const tabInfo = this.activeTabs.get(tabId);

        if (tabInfo) {
            // End session tracking
            await this.endSportsbookSession(tabId);

            // Clean up monitoring
            await this.stopTabMonitoring(tabId);

            // Remove from active tabs
            this.activeTabs.delete(tabId);

            console.log(`Unregistered ${tabInfo.sportsbook} tab: ${tabId}`);

            // Notify other components
            await this.broadcastTabUnregistration(tabInfo);
        }
    }

    async updateSportsbookTab(tab) {
        const tabInfo = this.activeTabs.get(tab.id);

        if (tabInfo) {
            tabInfo.url = tab.url;
            tabInfo.title = tab.title;
            tabInfo.lastActive = Date.now();

            // Check if we've moved to a different section of the sportsbook
            const newPage = this.detectSportsbookPage(tab.url);
            if (newPage !== tabInfo.currentPage) {
                tabInfo.currentPage = newPage;
                await this.handlePageChange(tab.id, newPage);
            }
        }
    }

    async activateSportsbookTab(tab) {
        const tabInfo = this.activeTabs.get(tab.id);

        if (tabInfo) {
            tabInfo.lastActive = Date.now();

            // Update extension badge
            await this.updateExtensionBadge(tab.id);

            // Refresh content script if needed
            await this.ensureContentScriptActive(tab.id);

            // Log activation
            await this.logTabActivity(tab.id, 'activated');
        }
    }

    async injectContentScript(tabId) {
        try {
            const tabInfo = this.activeTabs.get(tabId);
            if (!tabInfo || tabInfo.contentScriptInjected) {
                return;
            }

            // Check if content script is already running
            const results = await chrome.scripting.executeScript({
                target: { tabId },
                func: () => window.EQ12_INJECTED || false
            });

            if (!results[0]?.result) {
                // Inject content script
                await chrome.scripting.executeScript({
                    target: { tabId },
                    files: ['sportsbook_scraper.js']
                });

                tabInfo.contentScriptInjected = true;
                console.log(`Content script injected into tab ${tabId}`);
            }
        } catch (error) {
            console.error(`Content script injection error for tab ${tabId}:`, error);
        }
    }

    async startTabMonitoring(tabId, tab) {
        const tabInfo = this.activeTabs.get(tabId);
        if (!tabInfo || tabInfo.monitoringActive) {
            return;
        }

        tabInfo.monitoringActive = true;

        // Start periodic checks for this tab
        const monitoringInterval = setInterval(async () => {
            await this.performTabHealthCheck(tabId);
        }, 30000); // 30 seconds

        tabInfo.monitoringInterval = monitoringInterval;

        console.log(`Started monitoring for tab ${tabId}`);
    }

    async stopTabMonitoring(tabId) {
        const tabInfo = this.activeTabs.get(tabId);
        if (tabInfo && tabInfo.monitoringInterval) {
            clearInterval(tabInfo.monitoringInterval);
            tabInfo.monitoringActive = false;
            console.log(`Stopped monitoring for tab ${tabId}`);
        }
    }

    async performTabHealthCheck(tabId) {
        try {
            const tab = await chrome.tabs.get(tabId);
            const tabInfo = this.activeTabs.get(tabId);

            if (!tabInfo) return;

            // Check if content script is still responsive
            const response = await chrome.tabs.sendMessage(tabId, {
                action: 'healthCheck'
            });

            if (!response || !response.success) {
                console.warn(`Content script unresponsive in tab ${tabId}, re-injecting...`);
                await this.injectContentScript(tabId);
            }

            // Update last check time
            tabInfo.lastHealthCheck = Date.now();

        } catch (error) {
            console.warn(`Health check failed for tab ${tabId}:`, error);
            // Tab might be closed or navigated away
            await this.unregisterSportsbookTab(tabId);
        }
    }

    async updateExtensionBadge(tabId) {
        const tabInfo = this.activeTabs.get(tabId);
        if (!tabInfo) return;

        try {
            // Get VPN status
            const vpnStatus = await this.getVPNStatus();

            // Update badge text and color
            await chrome.action.setBadgeText({
                text: '●',
                tabId: tabId
            });

            await chrome.action.setBadgeBackgroundColor({
                color: vpnStatus.connected ? '#00ff88' : '#ff4757',
                tabId: tabId
            });

            // Update title
            await chrome.action.setTitle({
                title: `EQ12: ${tabInfo.sportsbook} - ${vpnStatus.connected ? 'Protected' : 'Unprotected'}`,
                tabId: tabId
            });

        } catch (error) {
            console.error(`Badge update error for tab ${tabId}:`, error);
        }
    }

    // Advanced Tab Operations
    async openSportsbookInNewTab(sportsbook, url) {
        try {
            const tab = await chrome.tabs.create({
                url: url,
                active: true
            });

            console.log(`Opened ${sportsbook} in new tab: ${tab.id}`);
            return tab;
        } catch (error) {
            console.error(`Failed to open ${sportsbook} tab:`, error);
            throw error;
        }
    }

    async duplicateActiveTab() {
        try {
            const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tabs.length === 0) return null;

            const activeTab = tabs[0];
            if (!this.isSportsbookTab(activeTab)) {
                throw new Error('Active tab is not a sportsbook');
            }

            const duplicatedTab = await chrome.tabs.duplicate(activeTab.id);
            console.log(`Duplicated tab ${activeTab.id} to ${duplicatedTab.id}`);

            return duplicatedTab;
        } catch (error) {
            console.error('Tab duplication error:', error);
            throw error;
        }
    }

    async closeSportsbookTabs(sportsbook) {
        const tabsToClose = [];

        for (const [tabId, tabInfo] of this.activeTabs) {
            if (tabInfo.sportsbook === sportsbook) {
                tabsToClose.push(tabId);
            }
        }

        if (tabsToClose.length === 0) {
            console.log(`No ${sportsbook} tabs to close`);
            return;
        }

        try {
            await chrome.tabs.remove(tabsToClose);
            console.log(`Closed ${tabsToClose.length} ${sportsbook} tabs`);
        } catch (error) {
            console.error(`Error closing ${sportsbook} tabs:`, error);
        }
    }

    async reloadAllSportsbookTabs() {
        const reloadPromises = [];

        for (const tabId of this.activeTabs.keys()) {
            reloadPromises.push(chrome.tabs.reload(tabId));
        }

        try {
            await Promise.all(reloadPromises);
            console.log(`Reloaded ${reloadPromises.length} sportsbook tabs`);
        } catch (error) {
            console.error('Error reloading sportsbook tabs:', error);
        }
    }

    async captureAllSportsbookScreenshots() {
        const screenshots = new Map();

        for (const [tabId, tabInfo] of this.activeTabs) {
            try {
                const screenshot = await chrome.tabs.captureVisibleTab(
                    tabInfo.windowId,
                    { format: 'png', quality: 90 }
                );

                screenshots.set(tabId, {
                    sportsbook: tabInfo.sportsbook,
                    url: tabInfo.url,
                    timestamp: Date.now(),
                    screenshot: screenshot
                });
            } catch (error) {
                console.warn(`Failed to capture screenshot for tab ${tabId}:`, error);
            }
        }

        return screenshots;
    }

    // Utility Methods
    isSportsbookTab(tab) {
        if (!tab?.url) return false;

        const sportsbookDomains = [
            'draftkings.com',
            'fanduel.com',
            'betmgm.com',
            'caesars.com',
            'pointsbet.com'
        ];

        return sportsbookDomains.some(domain => tab.url.includes(domain));
    }

    detectSportsbook(url) {
        if (url.includes('draftkings.com')) return 'DraftKings';
        if (url.includes('fanduel.com')) return 'FanDuel';
        if (url.includes('betmgm.com')) return 'BetMGM';
        if (url.includes('caesars.com')) return 'Caesars';
        if (url.includes('pointsbet.com')) return 'PointsBet';
        return 'Unknown';
    }

    detectSportsbookPage(url) {
        if (url.includes('/sports/')) return 'sports';
        if (url.includes('/casino/')) return 'casino';
        if (url.includes('/live/')) return 'live-betting';
        if (url.includes('/promo/')) return 'promotions';
        if (url.includes('/account/')) return 'account';
        return 'home';
    }

    getSportsbookGroup(sportsbook) {
        const knownSportsbooks = ['DraftKings', 'FanDuel', 'BetMGM'];
        return knownSportsbooks.includes(sportsbook) ? sportsbook : 'Other';
    }

    async getVPNStatus() {
        try {
            const response = await chrome.runtime.sendMessage({ action: 'getVpnStatus' });
            return response.success ? response.data : { connected: false };
        } catch (error) {
            return { connected: false, error: error.message };
        }
    }

    // Session and Analytics
    async startSportsbookSession(tabId, tabInfo) {
        const sessionId = `${tabInfo.sportsbook}_${tabId}_${Date.now()}`;

        this.sportsbookSessions.set(tabId, {
            sessionId: sessionId,
            sportsbook: tabInfo.sportsbook,
            startTime: Date.now(),
            pageViews: 1,
            interactions: 0,
            scrapeCount: 0
        });

        console.log(`Started session ${sessionId} for ${tabInfo.sportsbook}`);
    }

    async endSportsbookSession(tabId) {
        const session = this.sportsbookSessions.get(tabId);

        if (session) {
            session.endTime = Date.now();
            session.duration = session.endTime - session.startTime;

            // Log session data
            await this.logSessionData(session);

            this.sportsbookSessions.delete(tabId);
            console.log(`Ended session ${session.sessionId}`);
        }
    }

    async logTabActivity(tabId, activity) {
        const tabInfo = this.activeTabs.get(tabId);
        const session = this.sportsbookSessions.get(tabId);

        if (tabInfo && session) {
            const logEntry = {
                timestamp: Date.now(),
                sessionId: session.sessionId,
                tabId: tabId,
                sportsbook: tabInfo.sportsbook,
                activity: activity,
                url: tabInfo.url
            };

            // Send to background for logging
            chrome.runtime.sendMessage({
                action: 'logBettingOperation',
                data: logEntry
            });
        }
    }

    async logSessionData(session) {
        chrome.runtime.sendMessage({
            action: 'logBettingOperation',
            data: {
                type: 'session_end',
                ...session
            }
        });
    }

    // Broadcast Methods
    async broadcastTabRegistration(tabInfo) {
        chrome.runtime.sendMessage({
            action: 'sportsbookTabRegistered',
            data: tabInfo
        });
    }

    async broadcastTabUnregistration(tabInfo) {
        chrome.runtime.sendMessage({
            action: 'sportsbookTabUnregistered',
            data: tabInfo
        });
    }

    // Public API
    getActiveTabs() {
        return Array.from(this.activeTabs.values());
    }

    getTabCount() {
        return this.activeTabs.size;
    }

    getTabsByGroup() {
        const grouped = {};
        for (const [tabId, tabInfo] of this.activeTabs) {
            const group = tabInfo.sportsbook;
            if (!grouped[group]) grouped[group] = [];
            grouped[group].push(tabInfo);
        }
        return grouped;
    }

    async handlePageChange(tabId, newPage) {
        await this.logTabActivity(tabId, `page_change_${newPage}`);

        const session = this.sportsbookSessions.get(tabId);
        if (session) {
            session.pageViews++;
        }
    }

    async handleWindowSportsbookFocus(tab) {
        await this.logTabActivity(tab.id, 'window_focus');
    }

    updateActiveTabStats(tab) {
        // Update internal statistics
        if (this.activeTabs.has(tab.id)) {
            const tabInfo = this.activeTabs.get(tab.id);
            tabInfo.lastActive = Date.now();
        }
    }

    updateTabGroups(tab) {
        // Update group last active time
        const group = this.getSportsbookGroup(this.detectSportsbook(tab.url));
        const groupInfo = this.tabGroups.get(group);
        if (groupInfo) {
            groupInfo.lastActive = Date.now();
        }
    }

    updateTabTitle(tabId, title) {
        const tabInfo = this.activeTabs.get(tabId);
        if (tabInfo) {
            tabInfo.title = title;
        }
    }

    updateTabFavicon(tabId, favIconUrl) {
        const tabInfo = this.activeTabs.get(tabId);
        if (tabInfo) {
            tabInfo.favIconUrl = favIconUrl;
        }
    }

    updateTabPosition(tabId, moveInfo) {
        const tabInfo = this.activeTabs.get(tabId);
        if (tabInfo) {
            tabInfo.position = moveInfo.toIndex;
        }
    }

    async ensureContentScriptActive(tabId) {
        const tabInfo = this.activeTabs.get(tabId);
        if (tabInfo && !tabInfo.contentScriptInjected) {
            await this.injectContentScript(tabId);
        }
    }

    async updateTabBadge(tabId, tab) {
        await this.updateExtensionBadge(tabId);
    }
}

// Export for use in background script
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EQ12TabManager;
} else if (typeof self !== 'undefined') {
    self.EQ12TabManager = EQ12TabManager;
}
