# EQ12 Governance Assistant - Mozilla Submission Guide

## Overview
This document provides comprehensive guidance for submitting the EQ12 Governance Assistant to Mozilla Add-ons (addons.mozilla.org) following all Mozilla policies and requirements.

## Pre-Submission Checklist

### ✅ Mozilla Policy Compliance
- [x] **No Surprises**: Extension functionality clearly described in manifest and listing
- [x] **Content Policy**: Complies with Mozilla Acceptable Use Policy
- [x] **Data Collection**: Implements proper user consent mechanisms
- [x] **Security**: Follows WebExtension security best practices
- [x] **Source Code**: Reviewable source code provided
- [x] **Development Practices**: Uses required permissions only, self-contained code

### ✅ Technical Requirements
- [x] **Manifest Version**: Uses Manifest V2 with Firefox compatibility
- [x] **Permissions**: Only requests necessary permissions (activeTab, storage, contextMenus, notifications)
- [x] **CSP**: Content Security Policy properly configured
- [x] **Icons**: Proper icon sizes (16x16, 48x48, 128x128) included
- [x] **Extension ID**: Unique extension ID configured for Firefox

### ✅ Privacy and Data Protection
- [x] **Privacy Policy**: Comprehensive privacy consent page implemented
- [x] **Data Collection Disclosure**: Clear user control over data transmission
- [x] **Opt-in Consent**: Explicit consent required for any data collection
- [x] **Local Storage**: All data stored locally by default
- [x] **No Personal Data**: No personal data collection without explicit consent

## File Structure for Submission

```
example_extension/
├── manifest.json              # Main extension manifest
├── background.js              # Background script with privacy compliance
├── content.js                 # Content script with debug capabilities
├── popup.html                 # Popup interface
├── popup.js                   # Popup logic with privacy controls
├── privacy-consent.html       # Privacy consent and policy page
├── debug-utils.js            # Debug utilities (self-contained)
├── polyfill.js               # Cross-browser compatibility
├── icons/                    # Required icon sizes
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
├── package.json              # Development configuration
├── .eslintrc.js             # ESLint configuration
└── .web-ext-config.js       # Web-ext build configuration
```

## Development Workflow

### 1. Install Dependencies
```bash
cd example_extension
npm install
```

### 2. Development Testing
```bash
# Run extension in Firefox
npm run start

# Run in Firefox Nightly
npm run start:nightly

# Lint extension code
npm run lint

# Build extension package
npm run build
```

### 3. Validation Before Submission
```bash
# Comprehensive validation
npm run validate

# Check for policy compliance
npm run lint
web-ext lint --source-dir=.
```

## Mozilla Submission Process

### 1. Developer Account Setup
1. Create account at https://addons.mozilla.org/developers/
2. Read and accept Firefox Add-on Distribution Agreement
3. Verify email address and complete developer profile

### 2. Extension Package Preparation
```bash
# Build production-ready package
npm run build

# The built .zip file will be in ../builds/web-ext/
```

### 3. Submission Steps
1. **Upload Extension**: Upload the .zip file from builds/web-ext/
2. **Source Code**: Provide source code if using build tools (our package.json and scripts)
3. **Description**: Use clear, policy-compliant description
4. **Categories**: Select appropriate categories (Developer Tools, Privacy & Security)
5. **Privacy Policy**: Link to our privacy-consent.html or external policy
6. **Screenshots**: Provide clear screenshots showing functionality

### 4. Review Process
- **Automated Review**: Initial automated checks for common issues
- **Human Review**: Manual review for policy compliance and functionality
- **Approval Timeline**: Typically 1-7 days for new submissions

## Required Information for Submission

### Extension Details
- **Name**: EQ12 Governance Assistant
- **Summary**: Helps analyze web pages for governance compliance and security best practices
- **Description**: 
  ```
  EQ12 Governance Assistant is a developer-focused extension that helps analyze web pages 
  for governance compliance, security best practices, and privacy considerations. 
  
  Key Features:
  • Local page analysis for security headers and compliance
  • Privacy-first approach - no data collection without explicit consent
  • Developer debugging tools and governance indicators
  • Cross-browser compatibility with Firefox, Chrome, and Edge
  
  Privacy Notice:
  This extension does not collect or transmit personal data by default. All analysis 
  is performed locally on your device. Optional technical data collection requires 
  explicit user consent and can be disabled at any time.
  ```

### Categories
- **Primary**: Developer Tools
- **Secondary**: Privacy & Security

### Privacy Policy URL
- Point to the privacy-consent.html file or create external policy page

### Source Code Submission
Since we use npm scripts and build tools, include:
- Complete source code in ZIP format
- package.json with build instructions
- README with build steps
- All source files (unminified, reviewable)

## Mozilla Policy Compliance Details

### Data Collection Compliance
Our extension implements Mozilla's data collection requirements:

1. **No Personal Data by Default**: Extension functions without collecting personal information
2. **Explicit Consent**: Privacy consent page shown on first install
3. **Granular Controls**: Users can choose specific data collection preferences
4. **Opt-out Capability**: All data collection can be disabled
5. **Clear Disclosure**: Privacy policy explains all data handling

### Security Compliance
- **Content Security Policy**: Properly configured to prevent XSS
- **Secure Permissions**: Only requests necessary permissions
- **No Remote Code**: All code is self-contained in the extension
- **HTTPS Only**: Any optional data transmission uses HTTPS
- **Input Validation**: All user inputs properly validated

### Development Practices Compliance
- **Self-contained**: Extension doesn't load remote code
- **Minimal Permissions**: Only uses activeTab, storage, contextMenus, notifications
- **No Obfuscation**: All code is readable and reviewable
- **Standard Libraries**: Uses standard browser APIs and polyfills
- **Performance**: Doesn't negatively impact browser performance

## Common Review Issues to Avoid

### 1. Permission Issues
- ❌ Don't request broad permissions like `<all_urls>`
- ✅ Use `activeTab` and `optional_permissions` instead

### 2. Data Collection Issues
- ❌ Don't collect data without clear disclosure
- ✅ Implement explicit consent with granular controls

### 3. Code Quality Issues
- ❌ Don't include minified or obfuscated code without source
- ✅ Provide clean, reviewable source code

### 4. Description Issues
- ❌ Don't use unclear or misleading descriptions
- ✅ Clearly explain functionality and any data handling

## Testing Before Submission

### Functional Testing
```bash
# Test in clean Firefox profile
web-ext run --source-dir=. --keep-profile-changes=false

# Test privacy consent flow
# 1. Install extension
# 2. Verify privacy consent page appears
# 3. Test both accept and decline flows
# 4. Verify extension works with minimal permissions
```

### Policy Compliance Testing
1. **Privacy Flow**: Ensure consent page appears on first install
2. **Data Collection**: Verify no data is collected without consent
3. **Permissions**: Test with minimal permissions
4. **Security**: Verify CSP compliance and secure practices

### Cross-Browser Testing
```bash
# Test in different Firefox versions
npm run start:firefox
npm run start:nightly

# Test cross-browser build
python ../scripts/eq12_cross_browser_extension_builder.py -s . -o ../builds
```

## Post-Submission

### Monitoring
- Monitor extension analytics through addons.mozilla.org dashboard
- Respond promptly to user reviews and feedback
- Track any policy compliance issues

### Updates
- Follow semantic versioning for updates
- Provide clear changelog for each version
- Ensure updates maintain policy compliance

### Support
- Respond to user support requests
- Monitor Mozilla developer forums for extension-related discussions
- Keep up with Mozilla policy updates

## Resources

### Mozilla Documentation
- [Extension Workshop](https://extensionworkshop.com/)
- [Add-on Policies](https://extensionworkshop.com/documentation/publish/add-on-policies/)
- [Firefox Add-on Distribution Agreement](https://extensionworkshop.com/documentation/publish/firefox-add-on-distribution-agreement/)

### Development Tools
- [web-ext CLI tool](https://github.com/mozilla/web-ext)
- [Extension validator](https://addons.mozilla.org/developers/addon/validate)
- [MDN WebExtensions API](https://developer.mozilla.org/docs/Mozilla/Add-ons/WebExtensions)

### Community
- [Mozilla Add-ons Forum](https://discourse.mozilla.org/c/add-ons/)
- [Matrix Chat](https://wiki.mozilla.org/Matrix)
- [Developer Newsletter](https://extensionworkshop.com/community/)

---

**This submission guide ensures full compliance with Mozilla Add-on Policies and provides a clear path to successful extension publication.**