// Background Service Worker - Sports Betting Assistant
// Handles WebSocket connection to Python backend and cross-browser compatibility

importScripts("polyfill/browser-polyfill.min.js");

class SportsBettingBackground {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.pythonServerUrl = "ws://localhost:8765";

        this.init();
    }

    async init() {
        console.log("🚀 Sports Betting Assistant Background Starting...");

        // Connect to Python WebSocket server
        this.connectWebSocket();

        // Set up periodic connection check
        setInterval(() => this.checkConnection(), 30000);

        // Listen for extension events
        this.setupEventListeners();
    }

    connectWebSocket() {
        try {
            this.ws = new WebSocket(this.pythonServerUrl);

            this.ws.onopen = () => {
                console.log("✅ Connected to Python betting optimizer backend");
                this.reconnectAttempts = 0;
                this.sendMessage({ type: "extension_connected", timestamp: new Date().toISOString() });
            };

            this.ws.onmessage = async (event) => {
                try {
                    const data = JSON.parse(event.data);
                    await this.handlePythonMessage(data);
                } catch (error) {
                    console.error("❌ Error parsing WebSocket message:", error);
                }
            };

            this.ws.onclose = () => {
                console.log("🔌 WebSocket connection closed");
                this.scheduleReconnect();
            };

            this.ws.onerror = (error) => {
                console.error("❌ WebSocket error:", error);
            };

        } catch (error) {
            console.error("❌ Failed to create WebSocket:", error);
            this.scheduleReconnect();
        }
    }

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

            setTimeout(() => {
                this.connectWebSocket();
            }, this.reconnectDelay * this.reconnectAttempts);
        } else {
            console.log("❌ Max reconnection attempts reached. Python backend may be offline.");
        }
    }

    async handlePythonMessage(data) {
        console.log("📨 Received from Python backend:", data);

        switch (data.type) {
            case "new_parlay":
                await this.handleNewParlay(data.parlay);
                break;
            case "odds_update":
                await this.handleOddsUpdate(data.odds);
                break;
            case "promo_alert":
                await this.handlePromoAlert(data.promo);
                break;
            case "status":
                await browser.storage.local.set({ pythonStatus: data.status });
                break;
            default:
                console.log("🤷 Unknown message type:", data.type);
        }
    }

    async handleNewParlay(parlay) {
        // Store parlay in extension storage
        await browser.storage.local.set({
            latestParlay: parlay,
            lastParlayUpdate: new Date().toISOString()
        });

        // Show notification
        await browser.notifications.create({
            type: "basic",
            iconUrl: "icons/icon48.png",
            title: `🎯 New ${parlay.sport.toUpperCase()} Parlay`,
            message: `${parlay.legs.length} legs | EV: ${parlay.ev} | Boost: ${parlay.promo_type}`
        });

        // Badge update
        await browser.action.setBadgeText({ text: "NEW" });
        await browser.action.setBadgeBackgroundColor({ color: "#10b981" });
    }

    async handleOddsUpdate(odds) {
        await browser.storage.local.set({ latestOdds: odds });
    }

    async handlePromoAlert(promo) {
        await browser.notifications.create({
            type: "basic",
            iconUrl: "icons/icon48.png",
            title: `🚨 ${promo.type} Alert`,
            message: promo.message
        });
    }

    setupEventListeners() {
        // Listen for popup requests
        browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
            this.handleExtensionMessage(request, sender, sendResponse);
            return true; // Will respond asynchronously
        });

        // Handle extension icon click
        browser.action.onClicked.addListener(() => {
            browser.action.setBadgeText({ text: "" });
        });
    }

    async handleExtensionMessage(request, sender, sendResponse) {
        switch (request.action) {
            case "getParlayData":
                const { latestParlay } = await browser.storage.local.get("latestParlay");
                sendResponse({ parlay: latestParlay });
                break;

            case "requestNewParlay":
                this.sendMessage({
                    type: "request_parlay",
                    sport: request.sport,
                    promo: request.promo,
                    stake: request.stake
                });
                sendResponse({ status: "requested" });
                break;

            case "fillBetSlip":
                await this.fillBetSlip(request.tabId, request.parlay);
                sendResponse({ status: "filled" });
                break;

            default:
                sendResponse({ error: "Unknown action" });
        }
    }

    async fillBetSlip(tabId, parlay) {
        try {
            await browser.scripting.executeScript({
                target: { tabId },
                func: this.injectParlayScript,
                args: [parlay]
            });
        } catch (error) {
            console.error("❌ Failed to fill bet slip:", error);
        }
    }

    // This function gets injected into the sportsbook page
    injectParlayScript(parlay) {
        console.log("🎯 Filling bet slip with parlay:", parlay);

        // Clear existing selections
        const clearButton = document.querySelector('[data-testid="betslip-clear-all"]');
        if (clearButton) clearButton.click();

        // Add each leg
        parlay.legs.forEach((leg, index) => {
            setTimeout(() => {
                const selector = `[data-outcome-label*="${leg.label}"], [data-sb-id*="${leg.market}"]`;
                const outcomeElement = document.querySelector(selector);

                if (outcomeElement) {
                    outcomeElement.click();
                    console.log(`✅ Added leg ${index + 1}: ${leg.label}`);
                } else {
                    console.warn(`❌ Could not find leg: ${leg.label}`);
                }
            }, index * 500); // Stagger clicks
        });

        // Set stake after all legs are added
        setTimeout(() => {
            const stakeInput = document.querySelector('input[data-testid="betslip-stake-input"]');
            if (stakeInput) {
                stakeInput.value = parlay.stake;
                stakeInput.dispatchEvent(new Event('input', { bubbles: true }));
                console.log(`💰 Set stake: $${parlay.stake}`);
            }
        }, parlay.legs.length * 500 + 1000);
    }

    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn("⚠️ WebSocket not connected. Message queued.");
        }
    }

    checkConnection() {
        if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
            console.log("🔄 Connection check: Reconnecting to Python backend...");
            this.connectWebSocket();
        }
    }
}

// Initialize background service
new SportsBettingBackground();
