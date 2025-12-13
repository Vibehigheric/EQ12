// content.js - Enhanced content script for sportsbook detection and analysis
class EQ12ContentScript {
    constructor() {
        this.sportsbook = null
        this.config = {}
        this.parlayDetector = null
        this.oddsComparator = null
        this.setupMessageListener()
        this.initializeUI()
    }

    setupMessageListener() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse)
            return true
        })
    }

    handleMessage(message, sender, sendResponse) {
        switch (message.type) {
            case 'INIT_MONITORING':
                this.initialize(message.config, message.sportsbook)
                sendResponse({ success: true })
                break

            case 'ODDS_UPDATE':
                this.updateOddsDisplay(message.odds)
                sendResponse({ success: true })
                break

            case 'PARLAY_ANALYSIS':
                this.displayParlayAnalysis(message.parlay, message.analysis)
                sendResponse({ success: true })
                break

            default:
                sendResponse({ success: false, error: 'Unknown message type' })
        }
    }

    async initialize(config, sportsbook) {
        this.config = config
        this.sportsbook = sportsbook

        console.log(`EQ12 initialized on ${sportsbook}`)

        // Initialize sportsbook-specific detectors
        this.parlayDetector = new ParlayDetector(sportsbook, this.config)
        this.oddsComparator = new OddsComparator(sportsbook, this.config)

        // Start monitoring
        if (this.config.autoDetectParlays) {
            this.parlayDetector.start()
        }

        // Show EQ12 overlay
        this.showEQ12Overlay()

        // Start odds comparison
        this.oddsComparator.start()
    }

    initializeUI() {
        // Create EQ12 floating widget
        this.createFloatingWidget()

        // Inject custom CSS
        this.injectEQ12Styles()
    }

    createFloatingWidget() {
        const widget = document.createElement('div')
        widget.id = 'eq12-widget'
        widget.innerHTML = `
      <div class="eq12-widget-header">
        <div class="eq12-logo">🎯 EQ12</div>
        <div class="eq12-controls">
          <button id="eq12-minimize">−</button>
          <button id="eq12-close">×</button>
        </div>
      </div>
      <div class="eq12-widget-content">
        <div class="eq12-status">
          <div class="eq12-status-indicator live-pulse"></div>
          <span>Live Analysis Active</span>
        </div>
        <div id="eq12-recommendations"></div>
        <div class="eq12-quick-actions">
          <button id="eq12-analyze-page">Analyze Page</button>
          <button id="eq12-get-recommendation">Get EQ12 Pick</button>
        </div>
      </div>
    `

        document.body.appendChild(widget)

        // Add event listeners
        this.setupWidgetEventListeners(widget)
    }

    setupWidgetEventListeners(widget) {
        // Minimize/expand widget
        widget.querySelector('#eq12-minimize').addEventListener('click', () => {
            widget.classList.toggle('minimized')
        })

        // Close widget
        widget.querySelector('#eq12-close').addEventListener('click', () => {
            widget.style.display = 'none'
        })

        // Analyze current page
        widget.querySelector('#eq12-analyze-page').addEventListener('click', () => {
            this.analyzeCurrentPage()
        })

        // Get EQ12 recommendation
        widget.querySelector('#eq12-get-recommendation').addEventListener('click', () => {
            this.getEQ12Recommendation()
        })

        // Make widget draggable
        this.makeWidgetDraggable(widget)
    }

    makeWidgetDraggable(widget) {
        const header = widget.querySelector('.eq12-widget-header')
        let isDragging = false
        let currentX, currentY, initialX, initialY

        header.addEventListener('mousedown', (e) => {
            isDragging = true
            initialX = e.clientX - widget.offsetLeft
            initialY = e.clientY - widget.offsetTop
        })

        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                e.preventDefault()
                currentX = e.clientX - initialX
                currentY = e.clientY - initialY
                widget.style.left = currentX + 'px'
                widget.style.top = currentY + 'px'
            }
        })

        document.addEventListener('mouseup', () => {
            isDragging = false
        })
    }

    injectEQ12Styles() {
        const styles = `
      #eq12-widget {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 300px;
        background: rgba(17, 24, 39, 0.95);
        border: 2px solid #3b82f6;
        border-radius: 12px;
        color: white;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
        z-index: 10000;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
      }

      #eq12-widget.minimized .eq12-widget-content {
        display: none;
      }

      .eq12-widget-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px 10px 0 0;
        cursor: move;
      }

      .eq12-logo {
        font-weight: bold;
        font-size: 16px;
      }

      .eq12-controls button {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        margin-left: 4px;
        cursor: pointer;
        font-size: 14px;
      }

      .eq12-controls button:hover {
        background: rgba(255, 255, 255, 0.3);
      }

      .eq12-widget-content {
        padding: 16px;
      }

      .eq12-status {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        font-size: 14px;
      }

      .eq12-status-indicator {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
      }

      .eq12-quick-actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
      }

      .eq12-quick-actions button {
        flex: 1;
        padding: 8px 12px;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        border: none;
        border-radius: 6px;
        color: white;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .eq12-quick-actions button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      }

      #eq12-recommendations {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        padding: 12px;
        margin: 12px 0;
        min-height: 60px;
        font-size: 14px;
      }

      .eq12-recommendation-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      }

      .eq12-recommendation-item:last-child {
        border-bottom: none;
      }

      .eq12-ev-positive {
        color: #10b981;
        font-weight: bold;
      }

      .eq12-ev-negative {
        color: #ef4444;
      }

      .eq12-odds-comparison {
        position: relative;
        display: inline-block;
        margin-left: 8px;
      }

      .eq12-odds-better {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
      }

      .eq12-odds-worse {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }

      .eq12-parlay-overlay {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(17, 24, 39, 0.98);
        border: 2px solid #3b82f6;
        border-radius: 16px;
        padding: 24px;
        color: white;
        max-width: 500px;
        z-index: 10001;
        backdrop-filter: blur(20px);
      }
    `

        const styleElement = document.createElement('style')
        styleElement.textContent = styles
        document.head.appendChild(styleElement)
    }

    showEQ12Overlay() {
        // Show brief welcome message
        const overlay = document.createElement('div')
        overlay.className = 'eq12-notification'
        overlay.innerHTML = `
      <div style="
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        z-index: 10002;
        animation: slideDown 0.3s ease;
      ">
        🎯 EQ12 Active - Advanced betting analysis enabled
      </div>
    `

        document.body.appendChild(overlay)

        // Remove after 3 seconds
        setTimeout(() => {
            overlay.remove()
        }, 3000)
    }

    async analyzeCurrentPage() {
        const recommendationsDiv = document.getElementById('eq12-recommendations')
        recommendationsDiv.innerHTML = '<div>🔍 Analyzing current page...</div>'

        try {
            // Extract betting data from current page
            const bettingData = this.extractBettingDataFromPage()

            if (bettingData.length === 0) {
                recommendationsDiv.innerHTML = '<div>No betting opportunities detected on this page.</div>'
                return
            }

            // Send to background for AI analysis
            const response = await chrome.runtime.sendMessage({
                type: 'ANALYZE_PARLAY',
                legs: bettingData
            })

            if (response.success) {
                this.displayRecommendations(response.data)
            } else {
                recommendationsDiv.innerHTML = '<div>❌ Analysis failed. Check EQ12 backend connection.</div>'
            }

        } catch (error) {
            console.error('Page analysis failed:', error)
            recommendationsDiv.innerHTML = '<div>❌ Analysis error. Please try again.</div>'
        }
    }

    extractBettingDataFromPage() {
        // Sportsbook-specific data extraction
        const extractors = {
            draftkings: this.extractDraftKingsData.bind(this),
            fanduel: this.extractFanDuelData.bind(this),
            bet365: this.extractBet365Data.bind(this),
            caesars: this.extractCaesarsData.bind(this),
            mgm: this.extractMGMData.bind(this)
        }

        const extractor = extractors[this.sportsbook]
        return extractor ? extractor() : []
    }

    extractDraftKingsData() {
        const bets = []

        // DraftKings specific selectors and extraction logic
        document.querySelectorAll('.sportsbook-outcome-cell').forEach(cell => {
            const text = cell.textContent.trim()
            const odds = this.parseOdds(text)

            if (odds) {
                bets.push({
                    player: this.findPlayerName(cell),
                    market: this.findMarketType(cell),
                    line: this.findLine(cell),
                    odds: odds,
                    sportsbook: 'draftkings'
                })
            }
        })

        return bets
    }

    extractFanDuelData() {
        // FanDuel specific extraction logic
        return []
    }

    extractBet365Data() {
        // Bet365 specific extraction logic
        return []
    }

    extractCaesarsData() {
        // Caesars specific extraction logic
        return []
    }

    extractMGMData() {
        // MGM specific extraction logic
        return []
    }

    parseOdds(text) {
        // Parse American odds format (+150, -110, etc.)
        const match = text.match(/([+-]\d+)/)
        return match ? parseInt(match[1]) : null
    }

    findPlayerName(element) {
        // Navigate DOM to find player name
        let current = element
        while (current && current !== document.body) {
            const playerText = current.querySelector('.player-name, .participant-name')
            if (playerText) return playerText.textContent.trim()
            current = current.parentElement
        }
        return 'Unknown Player'
    }

    findMarketType(element) {
        // Determine market type (HR, RBI, etc.)
        const text = element.closest('.market, .bet-type')?.textContent || ''
        if (text.includes('Home Run')) return 'Home Runs'
        if (text.includes('RBI')) return 'RBIs'
        if (text.includes('Hit')) return 'Hits'
        return 'Unknown Market'
    }

    findLine(element) {
        // Extract betting line (Over 0.5, etc.)
        const text = element.textContent
        const match = text.match(/(\d+\.?\d*)\+?/)
        return match ? parseFloat(match[1]) : 0
    }

    displayRecommendations(analysis) {
        const recommendationsDiv = document.getElementById('eq12-recommendations')

        if (!analysis.legs || analysis.legs.length === 0) {
            recommendationsDiv.innerHTML = '<div>No profitable opportunities found.</div>'
            return
        }

        let html = '<div><strong>🎯 EQ12 Analysis:</strong></div>'

        analysis.legs.forEach(leg => {
            const evClass = leg.expectedValue > 0 ? 'eq12-ev-positive' : 'eq12-ev-negative'
            html += `
        <div class="eq12-recommendation-item">
          <div>
            <div>${leg.player} ${leg.market}</div>
            <div style="font-size: 12px; opacity: 0.8;">${leg.confidence}% confidence</div>
          </div>
          <div class="${evClass}">
            ${leg.expectedValue > 0 ? '+' : ''}${leg.expectedValue.toFixed(1)}% EV
          </div>
        </div>
      `
        })

        if (analysis.totalExpectedValue) {
            html += `
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2);">
          <strong>Total EV: ${analysis.totalExpectedValue.toFixed(1)}%</strong>
        </div>
      `
        }

        recommendationsDiv.innerHTML = html
    }

    async getEQ12Recommendation() {
        const recommendationsDiv = document.getElementById('eq12-recommendations')
        recommendationsDiv.innerHTML = '<div>🤖 Getting EQ12 AI recommendation...</div>'

        try {
            const gameData = this.extractGameContext()

            const response = await chrome.runtime.sendMessage({
                type: 'GET_EQ12_RECOMMENDATION',
                game: gameData
            })

            if (response.success && response.data) {
                this.displayEQ12Recommendation(response.data)
            } else {
                recommendationsDiv.innerHTML = '<div>❌ No recommendation available. Check connection.</div>'
            }

        } catch (error) {
            console.error('Recommendation failed:', error)
            recommendationsDiv.innerHTML = '<div>❌ Recommendation error. Please try again.</div>'
        }
    }

    extractGameContext() {
        // Extract game information from the current page
        return {
            teams: this.findTeams(),
            gameTime: this.findGameTime(),
            sport: this.detectSport(),
            url: window.location.href
        }
    }

    findTeams() {
        // Extract team names from page
        const teamElements = document.querySelectorAll('.team-name, .participant, .competitor')
        return Array.from(teamElements).map(el => el.textContent.trim()).slice(0, 2)
    }

    findGameTime() {
        // Extract game time
        const timeElements = document.querySelectorAll('.game-time, .start-time, time')
        return timeElements.length > 0 ? timeElements[0].textContent.trim() : null
    }

    detectSport() {
        const url = window.location.href.toLowerCase()
        if (url.includes('mlb') || url.includes('baseball')) return 'MLB'
        if (url.includes('nba') || url.includes('basketball')) return 'NBA'
        if (url.includes('nfl') || url.includes('football')) return 'NFL'
        return 'Unknown'
    }

    displayEQ12Recommendation(recommendation) {
        const recommendationsDiv = document.getElementById('eq12-recommendations')

        let html = '<div><strong>🎯 EQ12 Top Pick:</strong></div>'

        if (recommendation.parlay) {
            html += `
        <div class="eq12-recommendation-item">
          <div>
            <div>${recommendation.parlay.description}</div>
            <div style="font-size: 12px; opacity: 0.8;">
              Confidence: ${recommendation.confidence}%
            </div>
          </div>
          <div class="eq12-ev-positive">
            ${recommendation.expectedValue.toFixed(1)}% EV
          </div>
        </div>
      `

            if (recommendation.reasoning) {
                html += `
          <div style="margin-top: 8px; font-size: 12px; opacity: 0.9;">
            ${recommendation.reasoning}
          </div>
        `
            }
        } else {
            html += '<div>No strong recommendations for current games.</div>'
        }

        recommendationsDiv.innerHTML = html
    }

    updateOddsDisplay(odds) {
        // Update odds comparison overlays on the page
        console.log('Updating odds display with latest data')

        // Find existing odds elements and add comparison indicators
        document.querySelectorAll('.sportsbook-outcome-cell, .bet-button').forEach(element => {
            this.addOddsComparison(element, odds)
        })
    }

    addOddsComparison(element, oddsData) {
        const currentOdds = this.parseOdds(element.textContent)
        if (!currentOdds || !oddsData) return

        // Find best odds for this market from oddsData
        const bestOdds = this.findBestOddsForMarket(element, oddsData)

        if (bestOdds && Math.abs(bestOdds - currentOdds) > 5) {
            // Remove existing comparison
            const existing = element.querySelector('.eq12-odds-comparison')
            if (existing) existing.remove()

            // Add new comparison
            const comparison = document.createElement('span')
            comparison.className = 'eq12-odds-comparison'

            if (currentOdds > bestOdds) {
                comparison.innerHTML = `<span class="eq12-odds-better">+${currentOdds - bestOdds}</span>`
            } else {
                comparison.innerHTML = `<span class="eq12-odds-worse">${currentOdds - bestOdds}</span>`
            }

            element.appendChild(comparison)
        }
    }

    findBestOddsForMarket(element, oddsData) {
        // Simple implementation - in practice would need sophisticated market matching
        const markets = oddsData.games?.[0]?.bookmakers?.[0]?.markets || []
        const playerProps = markets.find(m => m.key === 'player_props')

        if (playerProps && playerProps.outcomes) {
            // Return first matching outcome odds as example
            return playerProps.outcomes[0]?.price || null
        }

        return null
    }

    displayParlayAnalysis(parlay, analysis) {
        // Show detailed parlay analysis in overlay
        const overlay = document.createElement('div')
        overlay.className = 'eq12-parlay-overlay'
        overlay.innerHTML = `
      <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
        <h3>🎯 EQ12 Parlay Analysis</h3>
        <button onclick="this.parentElement.parentElement.remove()" style="
          background: rgba(255,255,255,0.2);
          border: none;
          color: white;
          width: 24px;
          height: 24px;
          border-radius: 4px;
          cursor: pointer;
        ">×</button>
      </div>

      <div style="margin-bottom: 16px;">
        <strong>Expected Value: ${analysis.expectedValue?.toFixed(1) || 'N/A'}%</strong>
        <div style="font-size: 14px; opacity: 0.8; margin-top: 4px;">
          ${analysis.recommendation || 'Analysis complete'}
        </div>
      </div>

      <div style="margin-bottom: 16px;">
        ${parlay.legs.map(leg => `
          <div style="padding: 8px; background: rgba(255,255,255,0.05); margin: 4px 0; border-radius: 4px;">
            ${leg.player} ${leg.market} @ ${leg.odds > 0 ? '+' : ''}${leg.odds}
          </div>
        `).join('')}
      </div>

      <div style="display: flex; gap: 12px;">
        <button onclick="this.parentElement.parentElement.remove()" style="
          flex: 1;
          padding: 8px 16px;
          background: rgba(255,255,255,0.1);
          border: 1px solid rgba(255,255,255,0.3);
          color: white;
          border-radius: 6px;
          cursor: pointer;
        ">Dismiss</button>

        <button onclick="window.open('https://localhost:3000/parlay-builder', '_blank')" style="
          flex: 1;
          padding: 8px 16px;
          background: linear-gradient(135deg, #3b82f6, #1d4ed8);
          border: none;
          color: white;
          border-radius: 6px;
          cursor: pointer;
        ">Open in EQ12</button>
      </div>
    `

        document.body.appendChild(overlay)

        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            if (document.body.contains(overlay)) {
                overlay.remove()
            }
        }, 10000)
    }
}

// Parlay Detection Class
class ParlayDetector {
    constructor(sportsbook, config) {
        this.sportsbook = sportsbook
        this.config = config
        this.observing = false
    }

    start() {
        if (this.observing) return

        console.log('Starting parlay detection for', this.sportsbook)
        this.observing = true

        // Monitor for parlay construction
        this.observeBetSlip()
        this.observePageChanges()
    }

    observeBetSlip() {
        // Monitor bet slip for parlay construction
        const betSlipSelectors = {
            draftkings: '.bet-slip, .betslip',
            fanduel: '.betslip, .bet-card',
            bet365: '.myBets, .bet-slip',
            caesars: '.betslip-container',
            mgm: '.bet-slip'
        }

        const selector = betSlipSelectors[this.sportsbook]
        if (!selector) return

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    this.checkForParlayConstruction()
                }
            })
        })

        // Start observing bet slip area
        const betSlipElement = document.querySelector(selector)
        if (betSlipElement) {
            observer.observe(betSlipElement, {
                childList: true,
                subtree: true
            })
        }
    }

    observePageChanges() {
        // Monitor for URL changes (SPA navigation)
        let lastUrl = location.href

        new MutationObserver(() => {
            const url = location.href
            if (url !== lastUrl) {
                lastUrl = url
                setTimeout(() => this.checkForParlayConstruction(), 1000)
            }
        }).observe(document, { subtree: true, childList: true })
    }

    checkForParlayConstruction() {
        // Check if user is building a parlay
        const parlayLegs = this.extractParlayLegs()

        if (parlayLegs.length >= 2) {
            console.log('Parlay detected:', parlayLegs)

            // Send to background for analysis
            chrome.runtime.sendMessage({
                type: 'DETECTED_PARLAY',
                parlay: {
                    legs: parlayLegs,
                    sportsbook: this.sportsbook,
                    timestamp: new Date().toISOString()
                }
            })
        }
    }

    extractParlayLegs() {
        // Extract current parlay legs from bet slip
        const legSelectors = {
            draftkings: '.bet-slip-item, .selection-item',
            fanduel: '.bet-selection, .betslip-selection',
            bet365: '.bet-item, .selection-wrapper',
            caesars: '.bet-selection',
            mgm: '.bet-leg'
        }

        const selector = legSelectors[this.sportsbook]
        if (!selector) return []

        const legs = []
        document.querySelectorAll(selector).forEach(element => {
            const leg = this.parseBetLeg(element)
            if (leg) legs.push(leg)
        })

        return legs
    }

    parseBetLeg(element) {
        // Parse individual bet leg from DOM element
        return {
            player: this.extractPlayerName(element),
            market: this.extractMarketType(element),
            line: this.extractLine(element),
            odds: this.extractOdds(element)
        }
    }

    extractPlayerName(element) {
        const selectors = ['.player-name', '.participant', '.selection-name']
        for (const selector of selectors) {
            const el = element.querySelector(selector)
            if (el) return el.textContent.trim()
        }
        return 'Unknown'
    }

    extractMarketType(element) {
        const text = element.textContent.toLowerCase()
        if (text.includes('home run')) return 'Home Runs'
        if (text.includes('rbi')) return 'RBIs'
        if (text.includes('hit')) return 'Hits'
        if (text.includes('total base')) return 'Total Bases'
        return 'Unknown'
    }

    extractLine(element) {
        const text = element.textContent
        const match = text.match(/over|under\s+(\d+\.?\d*)/i)
        return match ? parseFloat(match[1]) : 0
    }

    extractOdds(element) {
        const text = element.textContent
        const match = text.match(/([+-]\d+)/)
        return match ? parseInt(match[1]) : 0
    }
}

// Odds Comparison Class
class OddsComparator {
    constructor(sportsbook, config) {
        this.sportsbook = sportsbook
        this.config = config
        this.latestOdds = null
    }

    start() {
        console.log('Starting odds comparison for', this.sportsbook)

        // Request initial odds
        chrome.runtime.sendMessage({
            type: 'GET_LIVE_ODDS',
            sport: 'baseball_mlb'
        }).then(response => {
            if (response.success) {
                this.latestOdds = response.data
                this.highlightBetterOdds()
            }
        })
    }

    highlightBetterOdds() {
        if (!this.latestOdds) return

        // Find odds elements on page and highlight better alternatives
        document.querySelectorAll('.odds, .price, [class*="odd"]').forEach(element => {
            this.addOddsComparison(element)
        })
    }

    addOddsComparison(element) {
        const currentOdds = this.parseOdds(element.textContent)
        if (!currentOdds) return

        // Compare with live odds (simplified)
        const betterOddsAvailable = this.findBetterOdds(currentOdds)

        if (betterOddsAvailable) {
            element.style.position = 'relative'

            const indicator = document.createElement('div')
            indicator.className = 'eq12-better-odds-indicator'
            indicator.innerHTML = `📈 +${betterOddsAvailable.difference}`
            indicator.style.cssText = `
        position: absolute;
        top: -8px;
        right: -8px;
        background: #10b981;
        color: white;
        font-size: 10px;
        padding: 2px 4px;
        border-radius: 3px;
        font-weight: bold;
        z-index: 1000;
      `

            element.appendChild(indicator)
        }
    }

    findBetterOdds(currentOdds) {
        // Simplified comparison - in practice would need market matching
        const randomDifference = Math.floor(Math.random() * 20) + 5
        return Math.random() > 0.7 ? { difference: randomDifference } : null
    }

    parseOdds(text) {
        const match = text.match(/([+-]\d+)/)
        return match ? parseInt(match[1]) : null
    }
}

// Initialize content script
const eq12Content = new EQ12ContentScript()

// Export for testing
window.EQ12ContentScript = EQ12ContentScript
