
// EQ12 Advertising System  
// Mozilla-compliant ad display (extension UI only)

class EQ12AdManager {
  constructor() {
    this.adConfig = {
      enabled: false, // Disabled by default
      network: 'self_served', // Self-served ads only
      placement: 'extension_ui_only', // Never inject into web pages
      frequency: 'conservative' // Conservative frequency
    };
  }
  
  async loadAdConfig() {
    const config = await browser.storage.sync.get('ad_config');
    if (config.ad_config) {
      this.adConfig = {...this.adConfig, ...config.ad_config};
    }
  }
  
  async showConsentDialog() {
    return new Promise((resolve) => {
      const dialog = document.createElement('div');
      dialog.className = 'eq12-ad-consent';
      dialog.innerHTML = `
        <div class="consent-content">
          <h3>📢 Support EQ12 with Ads</h3>
          <p>Help support EQ12 development by enabling relevant ads in the extension interface.</p>
          
          <div class="consent-details">
            <h4>What this means:</h4>
            <ul>
              <li>✓ Ads shown only in EQ12 extension popup/options</li>
              <li>✓ No ads injected into websites you visit</li>
              <li>✓ Privacy-focused, relevant security/productivity tools</li>
              <li>✓ Can be disabled anytime in settings</li>
            </ul>
          </div>
          
          <div class="consent-buttons">
            <button id="enable-ads">Enable Ads & Support EQ12</button>
            <button id="disable-ads">No Thanks</button>
          </div>
          
          <div class="consent-footer">
            <small>
              <a href="https://eq12.com/privacy" target="_blank">Privacy Policy</a> |
              <a href="https://eq12.com/ad-policy" target="_blank">Ad Policy</a>
            </small>
          </div>
        </div>
      `;
      
      dialog.querySelector('#enable-ads').onclick = async () => {
        await browser.storage.sync.set({
          ad_config: {...this.adConfig, enabled: true},
          ad_consent_given: true
        });
        dialog.remove();
        resolve(true);
      };
      
      dialog.querySelector('#disable-ads').onclick = async () => {
        await browser.storage.sync.set({
          ad_config: {...this.adConfig, enabled: false},
          ad_consent_given: false
        });
        dialog.remove();
        resolve(false);
      };
      
      document.body.appendChild(dialog);
    });
  }
  
  async displayAd(placement) {
    if (!this.adConfig.enabled) return;
    
    // Only show ads in extension UI
    if (placement !== 'extension_ui') return;
    
    const adContainer = document.getElementById('eq12-ad-container');
    if (!adContainer) return;
    
    // Self-served ads for security/productivity tools
    const ads = [
      {
        title: "1Password",
        description: "Secure password manager for teams",
        url: "https://1password.com",
        image: "data:image/svg+xml;base64,PHN2Zw...", // Base64 encoded image
        category: "security"
      },
      {
        title: "Snyk Security",
        description: "Find and fix vulnerabilities in your code",
        url: "https://snyk.io",
        image: "data:image/svg+xml;base64,PHN2Zw...",
        category: "security"
      }
    ];
    
    const randomAd = ads[Math.floor(Math.random() * ads.length)];
    
    adContainer.innerHTML = `
      <div class="eq12-ad" data-category="${randomAd.category}">
        <div class="ad-label">Sponsored</div>
        <div class="ad-content">
          <img src="${randomAd.image}" alt="${randomAd.title}" class="ad-image">
          <div class="ad-text">
            <h4>${randomAd.title}</h4>
            <p>${randomAd.description}</p>
          </div>
        </div>
        <a href="${randomAd.url}" target="_blank" class="ad-link">Learn More</a>
      </div>
    `;
    
    // Track ad impression (privacy-friendly)
    this.trackAdImpression(randomAd.category);
  }
  
  async trackAdImpression(category) {
    const stats = await browser.storage.local.get('ad_stats') || {};
    const today = new Date().toDateString();
    
    if (!stats[today]) stats[today] = {};
    if (!stats[today][category]) stats[today][category] = 0;
    
    stats[today][category]++;
    
    await browser.storage.local.set({ad_stats: stats});
  }
}

// Initialize ad manager
const adManager = new EQ12AdManager();
adManager.loadAdConfig();
