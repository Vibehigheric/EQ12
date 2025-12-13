// EQ12 UI Enhancement Manager
// Enhanced with features inspired by Stylus, Stylebot, Dark Reader, and Tab Reloader
// Provides advanced UI customization and automation capabilities

class EQ12UIEnhancer {
    constructor() {
        this.customStyles = new Map();
        this.darkModeEnabled = false;
        this.autoReloadSettings = new Map();
        this.animations = new Map();
        this.themes = new Map();
        this.fontSettings = {
            family: 'inherit',
            size: '100%',
            weight: 'normal'
        };

        this.init();
    }

    async init() {
        console.log('🎨 EQ12 UI Enhancer initializing...');

        await this.loadUserSettings();
        await this.setupDarkMode();
        await this.setupAutoReload();
        await this.setupCustomStyles();
        await this.setupAnimations();
        await this.setupAccessibility();

        console.log('✅ UI Enhancer ready');
    }

    // Dark mode implementation inspired by Dark Reader
    async setupDarkMode() {
        const darkModeCSS = `
            :root {
                --eq12-dark-bg: #1a1a1a;
                --eq12-dark-surface: #2d2d2d;
                --eq12-dark-text: #e0e0e0;
                --eq12-dark-accent: #4fc3f7;
                --eq12-dark-border: #404040;
                --eq12-dark-success: #4caf50;
                --eq12-dark-warning: #ff9800;
                --eq12-dark-error: #f44336;
            }

            .eq12-dark-mode {
                background-color: var(--eq12-dark-bg) !important;
                color: var(--eq12-dark-text) !important;
            }

            .eq12-dark-mode * {
                background-color: var(--eq12-dark-surface) !important;
                color: var(--eq12-dark-text) !important;
                border-color: var(--eq12-dark-border) !important;
            }

            .eq12-dark-mode img {
                opacity: 0.8 !important;
                filter: brightness(0.8) !important;
            }

            .eq12-dark-mode input,
            .eq12-dark-mode select,
            .eq12-dark-mode textarea {
                background-color: var(--eq12-dark-surface) !important;
                color: var(--eq12-dark-text) !important;
                border: 1px solid var(--eq12-dark-border) !important;
            }

            .eq12-dark-mode button {
                background-color: var(--eq12-dark-accent) !important;
                color: var(--eq12-dark-bg) !important;
                border: none !important;
            }

            .eq12-dark-mode a {
                color: var(--eq12-dark-accent) !important;
            }

            .eq12-dark-mode .eq12-odds-positive {
                color: var(--eq12-dark-success) !important;
            }

            .eq12-dark-mode .eq12-odds-negative {
                color: var(--eq12-dark-error) !important;
            }

            /* Sportsbook-specific dark mode adjustments */
            .eq12-dark-mode [class*="betting"] {
                background-color: var(--eq12-dark-surface) !important;
            }

            .eq12-dark-mode [class*="odds"] {
                background-color: var(--eq12-dark-bg) !important;
                border: 1px solid var(--eq12-dark-border) !important;
            }
        `;

        this.injectCSS('dark-mode', darkModeCSS);

        if (this.darkModeEnabled) {
            this.enableDarkMode();
        }
    }

    enableDarkMode() {
        document.documentElement.classList.add('eq12-dark-mode');
        this.darkModeEnabled = true;
        this.saveUserSettings();

        // Apply intelligent dark mode to images and videos
        this.applySmartDarkMode();

        console.log('🌙 Dark mode enabled');
    }

    disableDarkMode() {
        document.documentElement.classList.remove('eq12-dark-mode');
        this.darkModeEnabled = false;
        this.saveUserSettings();
        console.log('☀️ Dark mode disabled');
    }

    applySmartDarkMode() {
        // Intelligent image filtering
        const images = document.querySelectorAll('img');
        images.forEach(img => {
            if (!img.hasAttribute('data-eq12-processed')) {
                img.style.filter = 'brightness(0.8) contrast(1.1)';
                img.setAttribute('data-eq12-processed', 'true');
            }
        });

        // Video adjustments
        const videos = document.querySelectorAll('video');
        videos.forEach(video => {
            if (!video.hasAttribute('data-eq12-processed')) {
                video.style.filter = 'brightness(0.9)';
                video.setAttribute('data-eq12-processed', 'true');
            }
        });
    }

    // Auto-reload functionality inspired by Tab Reloader
    async setupAutoReload() {
        // Default auto-reload settings for different sportsbooks
        const defaultSettings = {
            'draftkings.com': { enabled: false, interval: 30000 },
            'fanduel.com': { enabled: false, interval: 30000 },
            'betmgm.com': { enabled: false, interval: 30000 }
        };

        for (const [domain, settings] of Object.entries(defaultSettings)) {
            if (!this.autoReloadSettings.has(domain)) {
                this.autoReloadSettings.set(domain, settings);
            }
        }

        // Check if current site should auto-reload
        const currentDomain = window.location?.hostname;
        if (currentDomain && this.autoReloadSettings.has(currentDomain)) {
            const settings = this.autoReloadSettings.get(currentDomain);
            if (settings.enabled) {
                this.startAutoReload(settings.interval);
            }
        }
    }

    startAutoReload(interval) {
        if (this.reloadTimer) {
            clearInterval(this.reloadTimer);
        }

        this.reloadTimer = setInterval(() => {
            // Check if user is active before reloading
            if (this.isUserActive()) {
                console.log('🔄 Auto-reloading page for fresh data...');
                window.location.reload();
            }
        }, interval);

        console.log(`🔄 Auto-reload enabled (${interval / 1000}s)`);
    }

    stopAutoReload() {
        if (this.reloadTimer) {
            clearInterval(this.reloadTimer);
            this.reloadTimer = null;
            console.log('⏹️ Auto-reload disabled');
        }
    }

    isUserActive() {
        // Check if user has been inactive for more than 5 minutes
        const lastActivity = localStorage.getItem('eq12_last_activity') || Date.now();
        const inactiveTime = Date.now() - parseInt(lastActivity);
        return inactiveTime < 300000; // 5 minutes
    }

    // Custom CSS injection inspired by Stylus and Stylebot
    async setupCustomStyles() {
        // Betting odds enhancement styles
        const oddsEnhancementCSS = `
            /* Enhanced odds display */
            .eq12-odds-enhanced {
                position: relative;
                padding: 8px 12px !important;
                margin: 2px !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                text-align: center !important;
                min-width: 80px !important;
                transition: all 0.2s ease !important;
                cursor: pointer !important;
            }

            .eq12-odds-positive {
                background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%) !important;
                border: 2px solid #4caf50 !important;
                color: #2e7d32 !important;
            }

            .eq12-odds-negative {
                background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%) !important;
                border: 2px solid #f44336 !important;
                color: #c62828 !important;
            }

            .eq12-odds-neutral {
                background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%) !important;
                border: 2px solid #9e9e9e !important;
                color: #424242 !important;
            }

            .eq12-odds-enhanced:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
            }

            /* EV (Expected Value) indicators */
            .eq12-ev-indicator {
                position: absolute !important;
                top: -8px !important;
                right: -8px !important;
                background: #ff9800 !important;
                color: white !important;
                border-radius: 50% !important;
                width: 20px !important;
                height: 20px !important;
                font-size: 10px !important;
                font-weight: bold !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
            }

            .eq12-ev-positive {
                background: #4caf50 !important;
            }

            .eq12-ev-negative {
                background: #f44336 !important;
            }

            /* Betting slip enhancements */
            .eq12-betting-slip {
                position: fixed !important;
                top: 20px !important;
                right: 20px !important;
                width: 300px !important;
                background: white !important;
                border-radius: 12px !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
                z-index: 10000 !important;
                padding: 20px !important;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto !important;
            }

            /* VPN status indicator */
            .eq12-vpn-indicator {
                position: fixed !important;
                top: 20px !important;
                left: 20px !important;
                background: rgba(0,0,0,0.8) !important;
                color: white !important;
                padding: 8px 16px !important;
                border-radius: 20px !important;
                font-size: 12px !important;
                font-weight: 600 !important;
                z-index: 10000 !important;
                display: flex !important;
                align-items: center !important;
                gap: 8px !important;
            }

            .eq12-vpn-connected {
                background: rgba(76, 175, 80, 0.9) !important;
            }

            .eq12-vpn-disconnected {
                background: rgba(244, 67, 54, 0.9) !important;
                animation: eq12-pulse 2s infinite !important;
            }

            @keyframes eq12-pulse {
                0% { opacity: 0.8; }
                50% { opacity: 1; }
                100% { opacity: 0.8; }
            }
        `;

        this.injectCSS('odds-enhancement', oddsEnhancementCSS);

        // Responsive design improvements
        const responsiveCSS = `
            /* Mobile-friendly betting interface */
            @media (max-width: 768px) {
                .eq12-odds-enhanced {
                    min-width: 60px !important;
                    padding: 6px 8px !important;
                    font-size: 12px !important;
                }

                .eq12-betting-slip {
                    width: calc(100vw - 40px) !important;
                    top: auto !important;
                    bottom: 20px !important;
                    left: 20px !important;
                    right: 20px !important;
                }

                .eq12-vpn-indicator {
                    position: static !important;
                    margin: 10px !important;
                }
            }

            @media (max-width: 480px) {
                .eq12-odds-enhanced {
                    min-width: 50px !important;
                    padding: 4px 6px !important;
                    font-size: 10px !important;
                }
            }
        `;

        this.injectCSS('responsive', responsiveCSS);
    }

    // Animation system
    async setupAnimations() {
        const animationCSS = `
            /* Smooth transitions for all betting elements */
            .eq12-animate {
                transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1) !important;
            }

            /* Fade in animation for new odds */
            @keyframes eq12-fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .eq12-fade-in {
                animation: eq12-fadeIn 0.4s ease-out !important;
            }

            /* Highlight animation for updated odds */
            @keyframes eq12-highlight {
                0% {
                    background-color: #fff3cd;
                    transform: scale(1);
                }
                50% {
                    background-color: #ffeaa7;
                    transform: scale(1.02);
                }
                100% {
                    background-color: inherit;
                    transform: scale(1);
                }
            }

            .eq12-highlight {
                animation: eq12-highlight 1s ease-in-out !important;
            }

            /* Loading spinner */
            @keyframes eq12-spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .eq12-loading {
                display: inline-block !important;
                width: 20px !important;
                height: 20px !important;
                border: 3px solid rgba(0,0,0,.1) !important;
                border-radius: 50% !important;
                border-top-color: #007bff !important;
                animation: eq12-spin 1s ease-in-out infinite !important;
            }
        `;

        this.injectCSS('animations', animationCSS);
    }

    // Accessibility improvements
    async setupAccessibility() {
        const accessibilityCSS = `
            /* High contrast mode */
            .eq12-high-contrast {
                filter: contrast(150%) !important;
            }

            /* Large text mode */
            .eq12-large-text * {
                font-size: 1.2em !important;
                line-height: 1.5 !important;
            }

            /* Focus indicators */
            .eq12-odds-enhanced:focus,
            button:focus,
            input:focus {
                outline: 3px solid #007bff !important;
                outline-offset: 2px !important;
            }

            /* Reduced motion for users who prefer it */
            @media (prefers-reduced-motion: reduce) {
                .eq12-animate,
                .eq12-fade-in,
                .eq12-highlight {
                    animation: none !important;
                    transition: none !important;
                }
            }

            /* Screen reader friendly content */
            .eq12-sr-only {
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                padding: 0 !important;
                margin: -1px !important;
                overflow: hidden !important;
                clip: rect(0, 0, 0, 0) !important;
                white-space: nowrap !important;
                border: 0 !important;
            }
        `;

        this.injectCSS('accessibility', accessibilityCSS);

        // Add keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 'd') {
                e.preventDefault();
                this.toggleDarkMode();
            }
            if (e.altKey && e.key === 'r') {
                e.preventDefault();
                this.toggleAutoReload();
            }
        });
    }

    // CSS injection utility
    injectCSS(id, css) {
        const existing = document.getElementById(`eq12-style-${id}`);
        if (existing) {
            existing.remove();
        }

        const style = document.createElement('style');
        style.id = `eq12-style-${id}`;
        style.textContent = css;

        (document.head || document.documentElement).appendChild(style);

        this.customStyles.set(id, css);
    }

    removeCSS(id) {
        const existing = document.getElementById(`eq12-style-${id}`);
        if (existing) {
            existing.remove();
        }
        this.customStyles.delete(id);
    }

    // Theme system
    createTheme(name, colors) {
        const themeCSS = `
            .eq12-theme-${name} {
                --primary: ${colors.primary};
                --secondary: ${colors.secondary};
                --success: ${colors.success};
                --danger: ${colors.danger};
                --warning: ${colors.warning};
                --info: ${colors.info};
                --background: ${colors.background};
                --surface: ${colors.surface};
                --text: ${colors.text};
            }

            .eq12-theme-${name} .eq12-odds-positive {
                background: var(--success) !important;
                color: white !important;
            }

            .eq12-theme-${name} .eq12-odds-negative {
                background: var(--danger) !important;
                color: white !important;
            }

            .eq12-theme-${name} .eq12-betting-slip {
                background: var(--surface) !important;
                color: var(--text) !important;
            }
        `;

        this.injectCSS(`theme-${name}`, themeCSS);
        this.themes.set(name, colors);
    }

    applyTheme(name) {
        // Remove existing theme classes
        document.documentElement.classList.forEach(className => {
            if (className.startsWith('eq12-theme-')) {
                document.documentElement.classList.remove(className);
            }
        });

        // Apply new theme
        document.documentElement.classList.add(`eq12-theme-${name}`);
        console.log(`🎨 Applied theme: ${name}`);
    }

    // Font customization
    updateFontSettings(settings) {
        this.fontSettings = { ...this.fontSettings, ...settings };

        const fontCSS = `
            .eq12-custom-font * {
                font-family: ${this.fontSettings.family} !important;
                font-size: ${this.fontSettings.size} !important;
                font-weight: ${this.fontSettings.weight} !important;
            }
        `;

        this.injectCSS('custom-font', fontCSS);

        if (settings.family !== 'inherit') {
            document.documentElement.classList.add('eq12-custom-font');
        } else {
            document.documentElement.classList.remove('eq12-custom-font');
        }

        this.saveUserSettings();
    }

    // Odds styling based on value
    styleOddsElement(element, odds, expectedValue = null) {
        element.classList.add('eq12-odds-enhanced', 'eq12-animate');

        // Determine style based on odds value
        if (odds > 0) {
            element.classList.add('eq12-odds-positive');
        } else if (odds < 0) {
            element.classList.add('eq12-odds-negative');
        } else {
            element.classList.add('eq12-odds-neutral');
        }

        // Add EV indicator if provided
        if (expectedValue !== null) {
            this.addEVIndicator(element, expectedValue);
        }

        // Add fade-in animation
        element.classList.add('eq12-fade-in');
    }

    addEVIndicator(element, ev) {
        // Remove existing indicator
        const existing = element.querySelector('.eq12-ev-indicator');
        if (existing) {
            existing.remove();
        }

        const indicator = document.createElement('div');
        indicator.className = 'eq12-ev-indicator';
        indicator.textContent = ev > 0 ? '+' : ev < 0 ? '-' : '0';

        if (ev > 0) {
            indicator.classList.add('eq12-ev-positive');
        } else if (ev < 0) {
            indicator.classList.add('eq12-ev-negative');
        }

        element.style.position = 'relative';
        element.appendChild(indicator);
    }

    // VPN status UI
    updateVPNIndicator(isConnected, location = null) {
        let indicator = document.getElementById('eq12-vpn-indicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'eq12-vpn-indicator';
            indicator.className = 'eq12-vpn-indicator';
            document.body.appendChild(indicator);
        }

        indicator.className = isConnected ?
            'eq12-vpn-indicator eq12-vpn-connected' :
            'eq12-vpn-indicator eq12-vpn-disconnected';

        const status = isConnected ? '🔒 Protected' : '⚠️ Unprotected';
        const locationText = location ? ` (${location})` : '';

        indicator.innerHTML = `${status}${locationText}`;
    }

    // User activity tracking
    trackUserActivity() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

        events.forEach(event => {
            document.addEventListener(event, () => {
                localStorage.setItem('eq12_last_activity', Date.now().toString());
            }, { passive: true });
        });
    }

    // Settings persistence
    async saveUserSettings() {
        const settings = {
            darkMode: this.darkModeEnabled,
            autoReload: Object.fromEntries(this.autoReloadSettings),
            fontSettings: this.fontSettings,
            customStyles: Object.fromEntries(this.customStyles)
        };

        await chrome.storage.local.set({ ui_settings: settings });
    }

    async loadUserSettings() {
        const stored = await chrome.storage.local.get('ui_settings');

        if (stored.ui_settings) {
            const settings = stored.ui_settings;

            this.darkModeEnabled = settings.darkMode || false;
            this.fontSettings = settings.fontSettings || this.fontSettings;

            if (settings.autoReload) {
                this.autoReloadSettings = new Map(Object.entries(settings.autoReload));
            }

            if (settings.customStyles) {
                for (const [id, css] of Object.entries(settings.customStyles)) {
                    this.customStyles.set(id, css);
                }
            }
        }

        this.trackUserActivity();
    }

    // Public API methods
    toggleDarkMode() {
        if (this.darkModeEnabled) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode();
        }
    }

    toggleAutoReload() {
        const domain = window.location?.hostname;
        if (domain && this.autoReloadSettings.has(domain)) {
            const settings = this.autoReloadSettings.get(domain);
            settings.enabled = !settings.enabled;

            if (settings.enabled) {
                this.startAutoReload(settings.interval);
            } else {
                this.stopAutoReload();
            }

            this.saveUserSettings();
        }
    }

    highlightOddsChange(element) {
        element.classList.remove('eq12-highlight');
        // Force reflow
        void element.offsetWidth;
        element.classList.add('eq12-highlight');
    }

    showLoadingIndicator(element) {
        const loading = document.createElement('div');
        loading.className = 'eq12-loading';
        element.appendChild(loading);
        return loading;
    }

    removeLoadingIndicator(element) {
        const loading = element.querySelector('.eq12-loading');
        if (loading) {
            loading.remove();
        }
    }

    createBettingSlip() {
        const slip = document.createElement('div');
        slip.className = 'eq12-betting-slip';
        slip.innerHTML = `
            <h3>EQ12 Betting Slip</h3>
            <div id="eq12-selected-bets"></div>
            <div id="eq12-slip-controls">
                <button onclick="EQ12UI.clearSlip()">Clear</button>
                <button onclick="EQ12UI.calculateEV()">Calculate EV</button>
            </div>
        `;
        document.body.appendChild(slip);
        return slip;
    }

    getUIState() {
        return {
            darkMode: this.darkModeEnabled,
            autoReload: this.reloadTimer !== null,
            themes: Array.from(this.themes.keys()),
            customStyles: Array.from(this.customStyles.keys()),
            fontSettings: this.fontSettings
        };
    }
}

// Initialize UI enhancer
const EQ12UI = new EQ12UIEnhancer();

// Export for global use
if (typeof window !== 'undefined') {
    window.EQ12UI = EQ12UI;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EQ12UIEnhancer;
} else if (typeof self !== 'undefined') {
    self.EQ12UIEnhancer = EQ12UIEnhancer;
}
