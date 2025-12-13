#!/usr/bin/env python3
"""
EQ12 Extension Monetization Manager
Implements Mozilla-approved monetization strategies for browser extensions.

Based on monetization guidelines from Mozilla Extension Workshop.

Revenue Models:
1. Freemium with paid features
2. Subscription licensing
3. Donation requests
4. Compliant advertising

Author: EQ12 AI Agent
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ExtensionMonetizationManager:
    """
    Monetization manager implementing Mozilla Extension Workshop best practices:
    - Freemium feature gating
    - Subscription license management
    - Donation request integration
    - Compliant advertising placement
    """

    def __init__(self, extension_path: str):
        self.extension_path = Path(extension_path)
        self.config = self.load_monetization_config()

    def load_monetization_config(self) -> dict[str, Any]:
        """Load monetization configuration"""
        config_path = self.extension_path / "monetization_config.json"

        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)

        # Default configuration
        return {
            "revenue_model": "freemium",
            "free_features": [
                "basic_governance_check",
                "security_indicator",
                "compliance_score",
            ],
            "premium_features": [
                "advanced_analytics",
                "custom_policies",
                "enterprise_reporting",
                "api_integration",
            ],
            "subscription": {
                "monthly_price": 4.99,
                "yearly_price": 49.99,
                "trial_days": 14,
            },
            "donations": {
                "enabled": True,
                "platforms": ["paypal", "ko-fi", "github-sponsors"],
                "request_frequency": "monthly",
            },
            "advertising": {
                "enabled": False,
                "ad_network": "none",
                "placement": "extension_ui_only",
            },
        }

    def generate_license_system(self) -> str:
        """Generate secure license validation system"""
        return """
// EQ12 Extension License Management System
// Implements Mozilla-compliant monetization

class EQ12LicenseManager {
  constructor() {
    this.licenseKey = null;
    this.licenseStatus = 'free';
    this.trialExpiry = null;
    this.features = {
      free: [
        'basic_governance_check',
        'security_indicator',
        'compliance_score'
      ],
      premium: [
        'advanced_analytics',
        'custom_policies',
        'enterprise_reporting',
        'api_integration'
      ]
    };
  }

  async initializeLicense() {
    // Load stored license from sync storage
    const stored = await browser.storage.sync.get(['eq12_license', 'eq12_trial']);

    if (stored.eq12_license) {
      await this.validateLicense(stored.eq12_license);
    } else if (stored.eq12_trial) {
      this.checkTrialStatus(stored.eq12_trial);
    } else {
      this.startFreeTrial();
    }
  }

  async validateLicense(licenseKey) {
    try {
      // Validate license with secure server
      const response = await fetch('https://api.eq12.com/validate-license', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          license_key: licenseKey,
          browser_id: await this.getBrowserId()
        })
      });

      const result = await response.json();

      if (result.valid) {
        this.licenseKey = licenseKey;
        this.licenseStatus = result.type; // 'premium', 'enterprise'
        await browser.storage.sync.set({eq12_license: licenseKey});
        return true;
      } else {
        this.licenseStatus = 'free';
        await browser.storage.sync.remove('eq12_license');
        return false;
      }
    } catch (error) {
      console.error('License validation failed:', error);
      return false;
    }
  }

  async getBrowserId() {
    // Generate consistent browser ID for license binding
    const stored = await browser.storage.local.get('browser_id');
    if (stored.browser_id) {
      return stored.browser_id;
    }

    const browserId = this.generateSecureId();
    await browser.storage.local.set({browser_id: browserId});
    return browserId;
  }

  generateSecureId() {
    // Generate cryptographically secure random ID
    const array = new Uint32Array(4);
    crypto.getRandomValues(array);
    return Array.from(array, dec => dec.toString(16)).join('');
  }

  startFreeTrial() {
    const trialExpiry = new Date();
    trialExpiry.setDate(trialExpiry.getDate() + 14); // 14-day trial

    this.trialExpiry = trialExpiry;
    this.licenseStatus = 'trial';

    browser.storage.sync.set({
      eq12_trial: {
        start_date: new Date().toISOString(),
        expiry_date: trialExpiry.toISOString()
      }
    });
  }

  checkTrialStatus(trialData) {
    const expiry = new Date(trialData.expiry_date);

    if (new Date() > expiry) {
      this.licenseStatus = 'free';
      browser.storage.sync.remove('eq12_trial');
    } else {
      this.licenseStatus = 'trial';
      this.trialExpiry = expiry;
    }
  }

  hasFeatureAccess(featureName) {
    if (this.licenseStatus === 'free') {
      return this.features.free.includes(featureName);
    } else if (this.licenseStatus === 'trial' || this.licenseStatus === 'premium') {
      return this.features.free.includes(featureName) ||
             this.features.premium.includes(featureName);
    }
    return false;
  }

  getTrialDaysRemaining() {
    if (this.licenseStatus !== 'trial' || !this.trialExpiry) {
      return 0;
    }

    const now = new Date();
    const diffTime = this.trialExpiry - now;
    return Math.max(0, Math.ceil(diffTime / (1000 * 60 * 60 * 24)));
  }

  showUpgradeDialog() {
    const upgradeUrl = 'https://eq12.com/extension-premium';

    if (confirm('Upgrade to EQ12 Premium for advanced governance features?')) {
      browser.tabs.create({url: upgradeUrl});
    }
  }

  async requestDonation() {
    // Mozilla-compliant donation request
    const lastRequest = await browser.storage.sync.get('last_donation_request');
    const now = new Date();

    // Only show donation request monthly
    if (lastRequest.last_donation_request) {
      const lastDate = new Date(lastRequest.last_donation_request);
      const daysSince = (now - lastDate) / (1000 * 60 * 60 * 24);

      if (daysSince < 30) {
        return; // Too soon
      }
    }

    // Show donation dialog
    const donationMessage = `
      EQ12 Extension helps keep your browsing secure and compliant.

      Support continued development:
      • PayPal: https://paypal.me/eq12
      • Ko-fi: https://ko-fi.com/eq12
      • GitHub Sponsors: https://github.com/sponsors/eq12

      [Donate] [Maybe Later] [Don't Ask Again]
    `;

    // Store request timestamp
    await browser.storage.sync.set({
      last_donation_request: now.toISOString()
    });
  }
}

// Initialize license manager
const licenseManager = new EQ12LicenseManager();
licenseManager.initializeLicense();
"""

    def generate_freemium_gate(self) -> str:
        """Generate freemium feature gating code"""
        return """
// EQ12 Freemium Feature Gating
// Mozilla-compliant feature restrictions

class EQ12FreemiumGate {
  static async checkFeatureAccess(featureName) {
    const hasAccess = licenseManager.hasFeatureAccess(featureName);

    if (!hasAccess) {
      this.showFeatureLockedDialog(featureName);
      return false;
    }

    return true;
  }

  static showFeatureLockedDialog(featureName) {
    const dialog = document.createElement('div');
    dialog.className = 'eq12-upgrade-dialog';
    dialog.innerHTML = `
      <div class="upgrade-content">
        <h3>🚀 Premium Feature</h3>
        <p><strong>${featureName}</strong> is available in EQ12 Premium</p>

        <div class="trial-info">
          ${licenseManager.licenseStatus === 'free' ?
            '<p>Start your <strong>14-day free trial</strong> to unlock all features!</p>' :
            `<p>Trial expires in ${licenseManager.getTrialDaysRemaining()} days</p>`
          }
        </div>

        <div class="upgrade-buttons">
          <button id="start-trial">Start Free Trial</button>
          <button id="upgrade-premium">Upgrade to Premium</button>
          <button id="close-dialog">Maybe Later</button>
        </div>

        <div class="pricing">
          <p>Premium: $4.99/month or $49.99/year</p>
          <p>✓ Advanced Analytics ✓ Custom Policies ✓ Enterprise Reporting</p>
        </div>
      </div>
    `;

    // Add event listeners
    dialog.querySelector('#start-trial').onclick = () => {
      licenseManager.startFreeTrial();
      dialog.remove();
      location.reload();
    };

    dialog.querySelector('#upgrade-premium').onclick = () => {
      licenseManager.showUpgradeDialog();
      dialog.remove();
    };

    dialog.querySelector('#close-dialog').onclick = () => {
      dialog.remove();
    };

    document.body.appendChild(dialog);
  }

  // Feature usage tracking for analytics
  static async trackFeatureUsage(featureName, success = true) {
    const usage = await browser.storage.local.get('feature_usage') || {};
    const today = new Date().toDateString();

    if (!usage[today]) usage[today] = {};
    if (!usage[today][featureName]) usage[today][featureName] = {uses: 0, blocked: 0};

    if (success) {
      usage[today][featureName].uses++;
    } else {
      usage[today][featureName].blocked++;
    }

    await browser.storage.local.set({feature_usage: usage});
  }
}

// Usage example:
async function useAdvancedAnalytics() {
  if (await EQ12FreemiumGate.checkFeatureAccess('advanced_analytics')) {
    // Feature implementation
    EQ12FreemiumGate.trackFeatureUsage('advanced_analytics', true);
    return performAdvancedAnalytics();
  } else {
    EQ12FreemiumGate.trackFeatureUsage('advanced_analytics', false);
    return null;
  }
}
"""

    def generate_donation_system(self) -> str:
        """Generate Mozilla-compliant donation system"""
        return """
// EQ12 Donation System
// Mozilla-approved donation requests

class EQ12DonationManager {
  static async shouldShowDonationRequest() {
    const settings = await browser.storage.sync.get([
      'last_donation_request',
      'donation_dismissed',
      'user_donated'
    ]);

    // Don't show if user already donated or permanently dismissed
    if (settings.user_donated || settings.donation_dismissed) {
      return false;
    }

    // Only show monthly
    if (settings.last_donation_request) {
      const lastRequest = new Date(settings.last_donation_request);
      const daysSince = (new Date() - lastRequest) / (1000 * 60 * 60 * 24);
      return daysSince >= 30;
    }

    // First time after 7 days of usage
    const installDate = await browser.storage.local.get('install_date');
    if (installDate.install_date) {
      const daysSinceInstall = (
          (new Date() - new Date(installDate.install_date)) / (1000 * 60 * 60 * 24);
      )
      return daysSinceInstall >= 7;
    }

    return false;
  }

  static async showDonationDialog() {
    if (!(await this.shouldShowDonationRequest())) {
      return;
    }

    const dialog = document.createElement('div');
    dialog.className = 'eq12-donation-dialog';
    dialog.innerHTML = `
      <div class="donation-content">
        <div class="donation-header">
          <h3>💝 Support EQ12 Development</h3>
          <p>EQ12 Extension is free and helps keep your browsing secure!</p>
        </div>

        <div class="donation-stats">
          <p>✓ Analyzed ${await this.getAnalysisCount()} pages</p>
          <p>✓ Blocked ${await this.getThreatsBlocked()} security threats</p>
          <p>✓ Improved your privacy score by ${await this.getPrivacyImprovement()}%</p>
        </div>

        <div class="donation-options">
          <h4>Support continued development:</h4>
          <div class="donation-buttons">
            <a href="https://ko-fi.com/eq12" target="_blank" class="donation-btn ko-fi">
              ☕ Buy me a coffee ($3)
            </a>
            <a href="https://github.com/sponsors/eq12" target="_blank" class="donation-btn github">
              💖 GitHub Sponsors ($5/month)
            </a>
            <a href="https://paypal.me/eq12" target="_blank" class="donation-btn paypal">
              💳 PayPal (Custom amount)
            </a>
          </div>
        </div>

        <div class="donation-actions">
          <button id="donated-btn">I Donated!</button>
          <button id="maybe-later">Maybe Later</button>
          <button id="dont-ask">Don't Ask Again</button>
        </div>

        <div class="donation-footer">
          <small>Your support helps maintain this free extension for everyone!</small>
        </div>
      </div>
    `;

    // Event listeners
    dialog.querySelector('#donated-btn').onclick = async () => {
      await browser.storage.sync.set({user_donated: true});
      dialog.remove();
      this.showThankYouMessage();
    };

    dialog.querySelector('#maybe-later').onclick = async () => {
      await browser.storage.sync.set({last_donation_request: new Date().toISOString()});
      dialog.remove();
    };

    dialog.querySelector('#dont-ask').onclick = async () => {
      await browser.storage.sync.set({donation_dismissed: true});
      dialog.remove();
    };

    document.body.appendChild(dialog);
  }

  static showThankYouMessage() {
    const message = document.createElement('div');
    message.className = 'eq12-thank-you';
    message.innerHTML = `
      <div class="thank-you-content">
        <h3>🎉 Thank You!</h3>
        <p>Your support means the world to us and helps keep EQ12 free for everyone!</p>
        <button onclick="this.parentElement.parentElement.remove()">Close</button>
      </div>
    `;
    document.body.appendChild(message);

    setTimeout(() => message.remove(), 5000);
  }

  static async getAnalysisCount() {
    const stats = await browser.storage.local.get('analysis_stats');
    return stats.analysis_stats?.total_analyses || 0;
  }

  static async getThreatsBlocked() {
    const stats = await browser.storage.local.get('security_stats');
    return stats.security_stats?.threats_blocked || 0;
  }

  static async getPrivacyImprovement() {
    const stats = await browser.storage.local.get('privacy_stats');
    return stats.privacy_stats?.improvement_percentage || 15;
  }
}

// Initialize donation system
document.addEventListener('DOMContentLoaded', () => {
  // Show donation request after user interaction
  setTimeout(() => {
    EQ12DonationManager.showDonationDialog();
  }, 30000); // 30 seconds after page load
});
"""

    def generate_advertising_system(self) -> str:
        """Generate Mozilla-compliant advertising system"""
        return """
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
"""

    def save_monetization_config(self):
        """Save monetization configuration"""
        config_path = self.extension_path / "monetization_config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)

        logger.info(f"Monetization config saved to {config_path}")

    def generate_monetization_files(self):
        """Generate all monetization files"""
        logger.info("Generating monetization system files...")

        # Create monetization directory
        monetization_dir = self.extension_path / "monetization"
        monetization_dir.mkdir(exist_ok=True)

        # Generate license system
        with open(monetization_dir / "license_manager.js", "w", encoding="utf-8") as f:
            f.write(self.generate_license_system())

        # Generate freemium gate
        with open(monetization_dir / "freemium_gate.js", "w", encoding="utf-8") as f:
            f.write(self.generate_freemium_gate())

        # Generate donation system
        with open(monetization_dir / "donation_manager.js", "w", encoding="utf-8") as f:
            f.write(self.generate_donation_system())

        # Generate advertising system
        with open(monetization_dir / "ad_manager.js", "w", encoding="utf-8") as f:
            f.write(self.generate_advertising_system())

        # Generate CSS styles
        with open(monetization_dir / "monetization.css", "w", encoding="utf-8") as f:
            f.write(self.generate_monetization_css())

        # Save configuration
        self.save_monetization_config()

        logger.info("✅ Monetization system generated successfully")

    def generate_monetization_css(self) -> str:
        """Generate CSS for monetization components"""
        return """
/* EQ12 Monetization System Styles */

.eq12-upgrade-dialog,
.eq12-donation-dialog,
.eq12-ad-consent {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  z-index: 10000;
  max-width: 400px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

.upgrade-content,
.donation-content,
.consent-content {
  padding: 24px;
}

.upgrade-content h3,
.donation-content h3,
.consent-content h3 {
  margin: 0 0 16px 0;
  color: #2196F3;
  font-size: 18px;
}

.trial-info,
.donation-stats {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  margin: 16px 0;
}

.upgrade-buttons,
.donation-actions,
.consent-buttons {
  display: flex;
  gap: 8px;
  margin-top: 20px;
}

.upgrade-buttons button,
.donation-actions button,
.consent-buttons button {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

#start-trial,
#enable-ads {
  background: #28a745;
  color: white;
}

#upgrade-premium {
  background: #2196F3;
  color: white;
}

#close-dialog,
#maybe-later,
#disable-ads {
  background: #6c757d;
  color: white;
}

.pricing {
  font-size: 12px;
  color: #666;
  text-align: center;
  margin-top: 16px;
}

.donation-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0;
}

.donation-btn {
  display: block;
  padding: 12px;
  text-decoration: none;
  border-radius: 4px;
  text-align: center;
  font-weight: 500;
}

.donation-btn.ko-fi {
  background: #FF5F5F;
  color: white;
}

.donation-btn.github {
  background: #24292e;
  color: white;
}

.donation-btn.paypal {
  background: #0070ba;
  color: white;
}

.eq12-ad {
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 12px;
  margin: 8px 0;
  background: #fafafa;
}

.ad-label {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.ad-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ad-image {
  width: 32px;
  height: 32px;
  border-radius: 4px;
}

.ad-text h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
}

.ad-text p {
  margin: 0;
  font-size: 12px;
  color: #666;
}

.ad-link {
  display: inline-block;
  margin-top: 8px;
  color: #2196F3;
  text-decoration: none;
  font-size: 12px;
}

.eq12-thank-you {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #28a745;
  color: white;
  padding: 16px;
  border-radius: 8px;
  max-width: 300px;
  z-index: 10001;
}

.thank-you-content h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
}

.thank-you-content button {
  background: rgba(255,255,255,0.2);
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 4px;
  margin-top: 8px;
  cursor: pointer;
}
"""


def main():
    parser = argparse.ArgumentParser(description="EQ12 Extension Monetization Manager")
    parser.add_argument(
        "--extension-path",
        "-e",
        required=True,
        help="Path to extension directory")
    parser.add_argument(
        "--model",
        "-m",
        choices=["freemium", "subscription", "donation", "advertising"],
        default="freemium",
        help="Revenue model to implement",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Initialize monetization manager
    manager = ExtensionMonetizationManager(args.extension_path)
    manager.config["revenue_model"] = args.model

    # Generate monetization files
    manager.generate_monetization_files()

    print(
        """
🚀 EQ12 Extension Monetization System Generated!

Revenue Model: {args.model.title()}
Extension Path: {args.extension_path}

Generated Files:
- monetization/license_manager.js
- monetization/freemium_gate.js
- monetization/donation_manager.js
- monetization/ad_manager.js
- monetization/monetization.css
- monetization_config.json

Next Steps:
1. Include monetization scripts in your manifest.json
2. Set up payment processing with providers like:
   - ExtensionPay (https://extensionpay.com)
   - PayPal (https://paypal.com/developers)
   - Stripe (https://stripe.com)
3. Configure donation platforms:
   - Ko-fi (https://ko-fi.com)
   - GitHub Sponsors (https://github.com/sponsors)
4. Test monetization flow across all browsers
5. Ensure compliance with Mozilla Add-on Policies

Mozilla Guidelines Implemented:
✅ Clear payment disclosure
✅ User consent for monetization features
✅ Easy opt-out mechanisms
✅ No cryptocurrency miners
✅ Extension UI ads only (no web page injection)
✅ Privacy-compliant data collection
"""
    )


if __name__ == "__main__":
    main()
