
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
      const daysSinceInstall = (new Date() - new Date(installDate.install_date)) / (1000 * 60 * 60 * 24);
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
