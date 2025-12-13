// secure-communication.js - Secure data handling for EQ12 Governance Assistant
class SecureCommunication {
    constructor() {
        this.encryptionKey = null;
        this.initializeEncryption();
    }
    
    async initializeEncryption() {
        // Generate or retrieve encryption key for sensitive data
        const keyData = await this.getOrCreateKey();
        this.encryptionKey = await crypto.subtle.importKey(
            'raw',
            keyData,
            { name: 'AES-GCM' },
            false,
            ['encrypt', 'decrypt']
        );
    }
    
    async getOrCreateKey() {
        let keyData = await this.getStoredKey();
        if (!keyData) {
            keyData = crypto.getRandomValues(new Uint8Array(32));
            await this.storeKey(keyData);
        }
        return keyData;
    }
    
    async getStoredKey() {
        return new Promise((resolve) => {
            chrome.storage.local.get(['encryptionKey'], (result) => {
                resolve(result.encryptionKey ? new Uint8Array(result.encryptionKey) : null);
            });
        });
    }
    
    async storeKey(keyData) {
        return new Promise((resolve) => {
            chrome.storage.local.set({ 
                encryptionKey: Array.from(keyData) 
            }, resolve);
        });
    }
    
    async encryptData(data) {
        if (!this.encryptionKey) {
            await this.initializeEncryption();
        }
        
        const encoder = new TextEncoder();
        const encodedData = encoder.encode(JSON.stringify(data));
        const iv = crypto.getRandomValues(new Uint8Array(12));
        
        const encryptedData = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: iv },
            this.encryptionKey,
            encodedData
        );
        
        return {
            iv: Array.from(iv),
            data: Array.from(new Uint8Array(encryptedData))
        };
    }
    
    async decryptData(encryptedObj) {
        if (!this.encryptionKey) {
            await this.initializeEncryption();
        }
        
        const iv = new Uint8Array(encryptedObj.iv);
        const encryptedData = new Uint8Array(encryptedObj.data);
        
        const decryptedData = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: iv },
            this.encryptionKey,
            encryptedData
        );
        
        const decoder = new TextDecoder();
        const decodedData = decoder.decode(decryptedData);
        return JSON.parse(decodedData);
    }
}

// input-validator.js - Input validation and sanitization
class InputValidator {
    static sanitizeHTML(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }
    
    static validateURL(url) {
        try {
            const parsedURL = new URL(url);
            // Only allow HTTP/HTTPS protocols
            if (!['http:', 'https:'].includes(parsedURL.protocol)) {
                return false;
            }
            // Prevent data: and javascript: URLs
            return !url.toLowerCase().startsWith('data:') && 
                   !url.toLowerCase().startsWith('javascript:');
        } catch {
            return false;
        }
    }
    
    static sanitizeErrorMessage(error) {
        // Remove potentially sensitive information from error messages
        const sanitized = error.toString()
            .replace(/file:\/\/[^\s]*/g, '[LOCAL_FILE]')
            .replace(/chrome-extension:\/\/[^\s]*/g, '[EXTENSION_FILE]')
            .replace(/\/[^\s]*\/[^\s]*/g, '[PATH]')
            .substring(0, 500); // Limit length
        return this.sanitizeHTML(sanitized);
    }
    
    static validateStorageKey(key) {
        // Validate storage keys to prevent injection
        return /^[a-zA-Z0-9_\-\.]+$/.test(key) && key.length <= 100;
    }
    
    static sanitizeStorageValue(value) {
        // Ensure storage values are safe
        if (typeof value === 'string') {
            return value.substring(0, 10000); // Limit size
        }
        return value;
    }
}

// permission-manager.js - Permission management
class PermissionManager {
    constructor() {
        this.requiredPermissions = ['activeTab', 'storage'];
        this.optionalPermissions = ['contextMenus', 'notifications'];
    }
    
    async checkRequiredPermissions() {
        return new Promise((resolve) => {
            chrome.permissions.contains({
                permissions: this.requiredPermissions
            }, resolve);
        });
    }
    
    async requestOptionalPermission(permission) {
        if (!this.optionalPermissions.includes(permission)) {
            throw new Error('Permission not in allowed list');
        }
        
        return new Promise((resolve) => {
            chrome.permissions.request({
                permissions: [permission]
            }, (granted) => {
                if (granted) {
                    this.logPermissionChange('granted', permission);
                }
                resolve(granted);
            });
        });
    }
    
    async removeOptionalPermission(permission) {
        return new Promise((resolve) => {
            chrome.permissions.remove({
                permissions: [permission]
            }, (removed) => {
                if (removed) {
                    this.logPermissionChange('removed', permission);
                }
                resolve(removed);
            });
        });
    }
    
    logPermissionChange(action, permission) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] Permission ${action}: ${permission}`);
        
        // Store permission change log locally
        chrome.storage.local.get(['permissionLog'], (result) => {
            const log = result.permissionLog || [];
            log.push({
                timestamp,
                action,
                permission
            });
            
            // Keep only last 100 entries
            if (log.length > 100) {
                log.splice(0, log.length - 100);
            }
            
            chrome.storage.local.set({ permissionLog: log });
        });
    }
}