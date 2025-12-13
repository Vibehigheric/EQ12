
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
