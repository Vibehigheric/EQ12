const { EQ12OpenAISecurityManager } = require('../../eq12_openai_security');

/**
 * OpenAI Security Integration for GitHub Actions
 * Provides secure OpenAI API access with cost controls
 */
class EQ12OpenAISecurityNode {
    constructor(environment = 'ci') {
        this.securityManager = new EQ12OpenAISecurityManager(environment);
    }

    async secureOpenAIRequest(model, messages, options = {}) {
        // Set Node.js specific configuration
        process.env.EQ12_RUNTIME = 'nodejs';
        process.env.EQ12_CI_MODE = 'true';

        return await this.securityManager.secure_openai_request(
            model,
            messages,
            options
        );
    }

    async validateEnvironment() {
        return this.securityManager.validate_environment();
    }

    async getCostLimits() {
        return this.securityManager.get_cost_limits();
    }

    async trackUsage(cost, model, tokens) {
        return this.securityManager.track_usage(cost, model, tokens);
    }
}

module.exports = { EQ12OpenAISecurityNode };
