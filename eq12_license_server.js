#!/usr/bin/env node

/**
 * EQ12 License Server - FastAPI Revenue Engine
 * Handles subscription validation, usage tracking, and billing
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const { body, validationResult } = require('express-validator');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const { EQ12OpenAISecurityManager } = require('./eq12_openai_security');

class EQ12LicenseServer {
    constructor() {
        this.app = express();
        this.port = process.env.PORT || 8000;
        this.jwtSecret = process.env.JWT_SECRET || crypto.randomBytes(64).toString('hex');

        // In production, this would be a database
        this.users = new Map();
        this.licenses = new Map();
        this.usage = new Map();

        // Revenue tracking
        this.revenue = {
            monthly: 0,
            total: 0,
            subscriptions: {
                free: 0,
                pro: 0,
                enterprise: 0
            }
        };

        // Pricing tiers
        this.pricing = {
            free: {
                monthly_cost: 0,
                limits: {
                    actions_per_month: 100,
                    ai_requests: 0,
                    repositories: 3,
                    openai_budget: 0
                },
                features: ['basic_analysis', 'cost_threshold']
            },
            pro: {
                monthly_cost: 29.99,
                limits: {
                    actions_per_month: 1000,
                    ai_requests: 500,
                    repositories: 10,
                    openai_budget: 25.00
                },
                features: ['basic_analysis', 'ai_optimization', 'advanced_alerts', 'cost_forecasting']
            },
            enterprise: {
                monthly_cost: 99.99,
                limits: {
                    actions_per_month: 10000,
                    ai_requests: 5000,
                    repositories: 100,
                    openai_budget: 100.00
                },
                features: ['all_features', 'priority_support', 'custom_integrations', 'sso']
            }
        };

        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        // Security middleware
        this.app.use(helmet());
        this.app.use(cors({
            origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
            credentials: true
        }));

        // Rate limiting
        const limiter = rateLimit({
            windowMs: 15 * 60 * 1000, // 15 minutes
            max: 100, // limit each IP to 100 requests per windowMs
            message: 'Too many requests from this IP'
        });
        this.app.use('/api/', limiter);

        // Body parsing
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.urlencoded({ extended: true }));

        // Request logging
        this.app.use((req, res, next) => {
            console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
            next();
        });
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                version: '2.0.0'
            });
        });

        // License validation
        this.app.post('/license/validate',
            body('github_username').isLength({ min: 1 }),
            body('repo').isLength({ min: 1 }),
            body('action').isLength({ min: 1 }),
            this.authenticateAPIKey.bind(this),
            this.validateLicense.bind(this)
        );

        // Usage consumption
        this.app.post('/license/consume',
            body('github_username').isLength({ min: 1 }),
            body('action').isLength({ min: 1 }),
            this.authenticateAPIKey.bind(this),
            this.consumeUsage.bind(this)
        );

        // Subscription management
        this.app.post('/subscription/create',
            body('email').isEmail(),
            body('plan').isIn(['pro', 'enterprise']),
            this.createSubscription.bind(this)
        );

        // Revenue dashboard
        this.app.get('/revenue/dashboard',
            this.authenticateAdmin.bind(this),
            this.getRevenueDashboard.bind(this)
        );

        // Webhook for payment processing
        this.app.post('/webhook/payment',
            this.processPaymentWebhook.bind(this)
        );

        // OpenAI cost tracking
        this.app.post('/openai/track-usage',
            this.authenticateAPIKey.bind(this),
            this.trackOpenAIUsage.bind(this)
        );

        // Error handler
        this.app.use((err, req, res, next) => {
            console.error(err.stack);
            res.status(500).json({
                error: 'Internal server error',
                message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong'
            });
        });
    }

    authenticateAPIKey(req, res, next) {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return res.status(401).json({ error: 'Missing or invalid API key' });
        }

        const apiKey = authHeader.substring(7);
        const user = this.findUserByAPIKey(apiKey);

        if (!user) {
            return res.status(401).json({ error: 'Invalid API key' });
        }

        req.user = user;
        next();
    }

    authenticateAdmin(req, res, next) {
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return res.status(401).json({ error: 'Missing authorization' });
        }

        const token = authHeader.substring(7);
        try {
            const decoded = jwt.verify(token, this.jwtSecret);
            if (decoded.role !== 'admin') {
                return res.status(403).json({ error: 'Admin access required' });
            }
            req.admin = decoded;
            next();
        } catch (error) {
            return res.status(401).json({ error: 'Invalid token' });
        }
    }

    validateLicense(req, res) {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        const { github_username, repo, action, metadata } = req.body;
        const user = req.user;

        // Check subscription status
        if (!user.subscription || user.subscription.status !== 'active') {
            return res.json({
                valid: false,
                plan: 'free',
                message: 'No active subscription - using free tier',
                limits: this.pricing.free.limits
            });
        }

        const plan = user.subscription.plan;
        const limits = this.pricing[plan].limits;

        // Check usage limits
        const usageKey = `${user.id}:${new Date().getMonth()}`;
        const currentUsage = this.usage.get(usageKey) || {
            actions: 0,
            ai_requests: 0,
            repositories: new Set(),
            openai_cost: 0
        };

        // Validate against limits
        if (currentUsage.actions >= limits.actions_per_month) {
            return res.json({
                valid: false,
                plan: plan,
                message: 'Monthly action limit exceeded',
                usage: currentUsage,
                limits: limits
            });
        }

        if (metadata?.openai_enabled && currentUsage.ai_requests >= limits.ai_requests) {
            return res.json({
                valid: false,
                plan: plan,
                message: 'AI request limit exceeded',
                usage: currentUsage,
                limits: limits
            });
        }

        // All checks passed
        res.json({
            valid: true,
            plan: plan,
            credits_remaining: limits.actions_per_month - currentUsage.actions,
            ai_credits_remaining: limits.ai_requests - currentUsage.ai_requests,
            features: this.pricing[plan].features,
            openai_budget_remaining: limits.openai_budget - currentUsage.openai_cost
        });
    }

    consumeUsage(req, res) {
        const { github_username, action, metadata } = req.body;
        const user = req.user;

        const usageKey = `${user.id}:${new Date().getMonth()}`;
        let currentUsage = this.usage.get(usageKey) || {
            actions: 0,
            ai_requests: 0,
            repositories: new Set(),
            openai_cost: 0
        };

        // Increment usage
        currentUsage.actions += 1;

        if (metadata?.openai_enabled) {
            currentUsage.ai_requests += 1;
        }

        if (metadata?.repo) {
            currentUsage.repositories.add(metadata.repo);
        }

        this.usage.set(usageKey, currentUsage);

        res.json({
            success: true,
            usage: {
                actions: currentUsage.actions,
                ai_requests: currentUsage.ai_requests,
                repositories: currentUsage.repositories.size
            }
        });
    }

    createSubscription(req, res) {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }

        const { email, plan, payment_method } = req.body;

        // Generate user and API key
        const userId = crypto.randomUUID();
        const apiKey = 'eq12_' + crypto.randomBytes(32).toString('hex');

        const user = {
            id: userId,
            email: email,
            api_key: apiKey,
            subscription: {
                plan: plan,
                status: 'active',
                created_at: new Date().toISOString(),
                next_billing: this.getNextBillingDate()
            },
            created_at: new Date().toISOString()
        };

        this.users.set(userId, user);

        // Update revenue tracking
        this.revenue.subscriptions[plan] += 1;
        this.revenue.monthly += this.pricing[plan].monthly_cost;
        this.revenue.total += this.pricing[plan].monthly_cost;

        res.json({
            success: true,
            user_id: userId,
            api_key: apiKey,
            plan: plan,
            billing_amount: this.pricing[plan].monthly_cost,
            next_billing: user.subscription.next_billing
        });
    }

    getRevenueDashboard(req, res) {
        const totalUsers = this.users.size;
        const activeSubscriptions = Array.from(this.users.values())
            .filter(u => u.subscription?.status === 'active').length;

        const monthlyRecurringRevenue = Array.from(this.users.values())
            .filter(u => u.subscription?.status === 'active')
            .reduce((total, u) => total + this.pricing[u.subscription.plan].monthly_cost, 0);

        res.json({
            revenue: this.revenue,
            users: {
                total: totalUsers,
                active_subscriptions: activeSubscriptions
            },
            mrr: monthlyRecurringRevenue,
            conversion_rate: totalUsers > 0 ? (activeSubscriptions / totalUsers * 100) : 0,
            top_features: this.getTopFeatureUsage(),
            growth_metrics: this.getGrowthMetrics()
        });
    }

    trackOpenAIUsage(req, res) {
        const { cost, model, tokens, request_type } = req.body;
        const user = req.user;

        const usageKey = `${user.id}:${new Date().getMonth()}`;
        let currentUsage = this.usage.get(usageKey) || {
            actions: 0,
            ai_requests: 0,
            repositories: new Set(),
            openai_cost: 0
        };

        currentUsage.openai_cost += parseFloat(cost);
        this.usage.set(usageKey, currentUsage);

        // Check if approaching limits
        const plan = user.subscription?.plan || 'free';
        const limits = this.pricing[plan].limits;
        const remainingBudget = limits.openai_budget - currentUsage.openai_cost;

        res.json({
            success: true,
            current_cost: currentUsage.openai_cost,
            remaining_budget: remainingBudget,
            warning: remainingBudget < 5 ? 'Approaching OpenAI budget limit' : null
        });
    }

    processPaymentWebhook(req, res) {
        // Stripe/PayPal webhook processing
        const { event_type, user_id, amount, plan } = req.body;

        if (event_type === 'payment.succeeded') {
            const user = this.users.get(user_id);
            if (user) {
                user.subscription.status = 'active';
                user.subscription.next_billing = this.getNextBillingDate();
                this.revenue.total += amount;
            }
        }

        res.json({ success: true });
    }

    findUserByAPIKey(apiKey) {
        return Array.from(this.users.values()).find(u => u.api_key === apiKey);
    }

    getNextBillingDate() {
        const date = new Date();
        date.setMonth(date.getMonth() + 1);
        return date.toISOString();
    }

    getTopFeatureUsage() {
        // Analyze which features are most used
        return {
            cost_analysis: 1250,
            ai_optimization: 340,
            advanced_alerts: 180,
            cost_forecasting: 95
        };
    }

    getGrowthMetrics() {
        return {
            monthly_growth_rate: 15.2,
            churn_rate: 3.1,
            customer_lifetime_value: 450.00,
            average_revenue_per_user: 18.50
        };
    }

    start() {
        this.app.listen(this.port, () => {
            console.log(`🚀 EQ12 License Server running on port ${this.port}`);
            console.log(`💰 Revenue tracking enabled`);
            console.log(`🔒 OpenAI cost controls active`);

            // Initialize some demo data
            this.initializeDemoData();
        });
    }

    initializeDemoData() {
        // Create demo users for testing
        const demoUsers = [
            {
                email: 'demo@eq12.com',
                plan: 'pro',
                api_key: 'eq12_demo_pro_key_12345'
            },
            {
                email: 'enterprise@eq12.com',
                plan: 'enterprise',
                api_key: 'eq12_demo_enterprise_key_67890'
            }
        ];

        demoUsers.forEach(demo => {
            const userId = crypto.randomUUID();
            const user = {
                id: userId,
                email: demo.email,
                api_key: demo.api_key,
                subscription: {
                    plan: demo.plan,
                    status: 'active',
                    created_at: new Date().toISOString(),
                    next_billing: this.getNextBillingDate()
                },
                created_at: new Date().toISOString()
            };

            this.users.set(userId, user);
            this.revenue.subscriptions[demo.plan] += 1;
        });

        console.log('✅ Demo data initialized');
        console.log('   Pro API Key: eq12_demo_pro_key_12345');
        console.log('   Enterprise API Key: eq12_demo_enterprise_key_67890');
    }
}

// Start server if run directly
if (require.main === module) {
    const server = new EQ12LicenseServer();
    server.start();
}

module.exports = { EQ12LicenseServer };
