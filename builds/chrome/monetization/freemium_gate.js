
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
