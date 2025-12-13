// eq12_realtime_betting_dashboard.js
/**
 * EQ12 Real-time Sports Betting Dashboard Server
 * Node.js/Express/Socket.IO with Redis integration, structured logging,
 * responsible gaming protections, and comprehensive observability
 */

const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const redis = require('redis');
const winston = require('winston');
const helmet = require('helmet');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const fs = require('fs').promises;
const path = require('path');

// Configuration from environment
const config = {
    port: process.env.PORT || 3000,
    redis: {
        url: process.env.REDIS_URL || 'redis://localhost:6379',
        db: process.env.REDIS_DB || 0
    },
    openai: {
        apiKey: process.env.OPENAI_API_KEY,
        model: process.env.OPENAI_MODEL || 'gpt-4-turbo'
    },
    security: {
        jwtSecret: process.env.JWT_SECRET || crypto.randomBytes(64).toString('hex'),
        rateLimitWindow: 15 * 60 * 1000, // 15 minutes
        rateLimitMax: 100
    },
    logging: {
        level: process.env.LOG_LEVEL || 'info',
        logDir: process.env.LOG_DIR || './logs'
    },
    responsibleGaming: {
        enableProtections: process.env.RG_ENABLED !== 'false',
        maxDailyBets: parseInt(process.env.RG_MAX_DAILY_BETS) || 50,
        maxSessionTime: parseInt(process.env.RG_MAX_SESSION_TIME) || 240, // minutes
        coolingPeriod: parseInt(process.env.RG_COOLING_PERIOD) || 60 // minutes
    }
};

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: process.env.ALLOWED_ORIGINS ? process.env.ALLOWED_ORIGINS.split(',') : ["http://localhost:3000"],
        methods: ["GET", "POST"]
    }
});

// Initialize Redis client
let redisClient;
let redisConnected = false;

// Structured logger setup
const logger = winston.createLogger({
    level: config.logging.level,
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: {
        service: 'eq12-betting-dashboard',
        version: '2.1.0',
        environment: process.env.NODE_ENV || 'development'
    },
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.simple()
            )
        }),
        new winston.transports.File({
            filename: path.join(config.logging.logDir, 'dashboard-error.log'),
            level: 'error'
        }),
        new winston.transports.File({
            filename: path.join(config.logging.logDir, 'dashboard-combined.log')
        })
    ]
});

// Circuit breaker for external services
class CircuitBreaker {
    constructor(threshold = 5, timeout = 60000) {
        this.threshold = threshold;
        this.timeout = timeout;
        this.failureCount = 0;
        this.lastFailureTime = null;
        this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    }

    async call(fn) {
        if (this.state === 'OPEN') {
            if (Date.now() - this.lastFailureTime > this.timeout) {
                this.state = 'HALF_OPEN';
            } else {
                throw new Error('Circuit breaker is OPEN');
            }
        }

        try {
            const result = await fn();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            throw error;
        }
    }

    onSuccess() {
        this.failureCount = 0;
        this.state = 'CLOSED';
    }

    onFailure() {
        this.failureCount++;
        this.lastFailureTime = Date.now();
        if (this.failureCount >= this.threshold) {
            this.state = 'OPEN';
        }
    }
}

// Initialize circuit breakers
const redisCircuitBreaker = new CircuitBreaker();
const openaiCircuitBreaker = new CircuitBreaker();

// Middleware setup
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
            scriptSrc: ["'self'", "https://cdn.jsdelivr.net"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "ws:", "wss:"]
        }
    }
}));

app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
    windowMs: config.security.rateLimitWindow,
    max: config.security.rateLimitMax,
    message: {
        error: 'Too many requests',
        retryAfter: Math.ceil(config.security.rateLimitWindow / 1000)
    },
    standardHeaders: true,
    legacyHeaders: false,
});
app.use(limiter);

// Request tracking middleware
app.use((req, res, next) => {
    req.requestId = uuidv4();
    req.startTime = Date.now();

    logger.info('HTTP Request', {
        requestId: req.requestId,
        method: req.method,
        url: req.url,
        userAgent: req.get('User-Agent'),
        ip: req.ip,
        timestamp: new Date().toISOString()
    });

    res.on('finish', () => {
        const duration = Date.now() - req.startTime;
        logger.info('HTTP Response', {
            requestId: req.requestId,
            statusCode: res.statusCode,
            duration,
            timestamp: new Date().toISOString()
        });
    });

    next();
});

// Sports betting data structures
class BettingOdds {
    constructor(data) {
        this.id = data.id || uuidv4();
        this.sport = data.sport;
        this.league = data.league;
        this.event = data.event;
        this.market = data.market;
        this.selection = data.selection;
        this.odds = data.odds;
        this.decimalOdds = this.americanToDecimal(data.odds);
        this.impliedProbability = 1 / this.decimalOdds;
        this.sportsbook = data.sportsbook;
        this.timestamp = data.timestamp || new Date().toISOString();
        this.confidence = data.confidence || 1.0;
        this.volume = data.volume || null;
        this.lineMovement = data.lineMovement || null;
    }

    americanToDecimal(americanOdds) {
        if (americanOdds > 0) {
            return (americanOdds / 100) + 1;
        } else {
            return (100 / Math.abs(americanOdds)) + 1;
        }
    }

    calculateKellyFraction(trueProbability, bankroll) {
        const edge = trueProbability - this.impliedProbability;
        const b = this.decimalOdds - 1;
        const kelly = (b * trueProbability - (1 - trueProbability)) / b;

        return {
            kelly: Math.max(0, Math.min(kelly, 0.25)), // Cap at 25% for risk management
            edge: edge,
            recommendedBet: Math.max(0, kelly * bankroll),
            expectedValue: edge * bankroll * kelly
        };
    }
}

class ParlayBuilder {
    constructor() {
        this.legs = [];
        this.id = uuidv4();
        this.createdAt = new Date().toISOString();
    }

    addLeg(bettingOdds) {
        if (this.legs.length >= 20) {
            throw new Error('Maximum 20 legs allowed in parlay');
        }
        this.legs.push(bettingOdds);
        return this;
    }

    removeLeg(legId) {
        this.legs = this.legs.filter(leg => leg.id !== legId);
        return this;
    }

    calculateCombinedOdds() {
        if (this.legs.length === 0) return { odds: 0, payout: 0 };

        const combinedDecimal = this.legs.reduce((acc, leg) => acc * leg.decimalOdds, 1);
        const combinedAmerican = combinedDecimal >= 2 ?
            (combinedDecimal - 1) * 100 :
            -100 / (combinedDecimal - 1);

        return {
            american: Math.round(combinedAmerican),
            decimal: combinedDecimal,
            impliedProbability: 1 / combinedDecimal,
            payout: (stake) => stake * combinedDecimal
        };
    }

    assessCorrelationRisk() {
        // Simple correlation assessment based on same game/time
        const events = new Set(this.legs.map(leg => leg.event));
        const correlationRisk = 1 - (events.size / this.legs.length);

        return {
            risk: correlationRisk,
            level: correlationRisk > 0.7 ? 'HIGH' :
                correlationRisk > 0.4 ? 'MEDIUM' : 'LOW',
            recommendation: correlationRisk > 0.7 ? 'SPLIT' :
                correlationRisk > 0.4 ? 'CAUTION' : 'PROCEED'
        };
    }

    toJSON() {
        const odds = this.calculateCombinedOdds();
        const correlation = this.assessCorrelationRisk();

        return {
            id: this.id,
            legs: this.legs,
            legCount: this.legs.length,
            combinedOdds: odds,
            correlationRisk: correlation,
            createdAt: this.createdAt,
            lastModified: new Date().toISOString()
        };
    }
}

// Responsible Gaming Manager
class ResponsibleGamingManager {
    constructor() {
        this.userSessions = new Map();
        this.dailyLimits = new Map();
    }

    async checkBettingLimits(userId, betAmount, betType = 'standard') {
        const userIdHash = this.hashUserId(userId);
        const session = this.getUserSession(userIdHash);
        const dailyStats = await this.getDailyStats(userIdHash);

        const checks = {
            dailyBetLimit: dailyStats.totalBets < config.responsibleGaming.maxDailyBets,
            sessionTimeLimit: session.duration < config.responsibleGaming.maxSessionTime * 60000,
            betSizeReasonable: betAmount <= (dailyStats.averageBet * 5), // Max 5x average
            coolingPeriodRespected: await this.checkCoolingPeriod(userIdHash),
            velocityCheck: this.checkBettingVelocity(session, betAmount)
        };

        const riskLevel = this.assessRiskLevel(checks, session, dailyStats);
        const interventions = this.determineInterventions(riskLevel, checks);

        // Log responsible gaming event
        await this.logResponsibleGamingEvent({
            userIdHash,
            eventType: 'betting_limit_check',
            betAmount,
            betType,
            checks,
            riskLevel,
            interventions,
            sessionData: this.sanitizeSessionData(session)
        });

        return {
            allowed: interventions.length === 0 || !interventions.includes('BLOCK'),
            riskLevel,
            checks,
            interventions,
            recommendations: this.generateRecommendations(riskLevel, checks)
        };
    }

    hashUserId(userId) {
        return crypto.createHash('sha256')
            .update(`${userId}:${process.env.RG_SALT || 'eq12-rg-salt'}`)
            .digest('hex')
            .substring(0, 16);
    }

    getUserSession(userIdHash) {
        if (!this.userSessions.has(userIdHash)) {
            this.userSessions.set(userIdHash, {
                id: uuidv4(),
                startTime: Date.now(),
                betCount: 0,
                totalWagered: 0,
                consecutiveLosses: 0,
                lastBetTime: null,
                riskFlags: new Set()
            });
        }

        const session = this.userSessions.get(userIdHash);
        session.duration = Date.now() - session.startTime;

        return session;
    }

    async getDailyStats(userIdHash) {
        const today = new Date().toISOString().split('T')[0];
        const key = `daily_stats:${userIdHash}:${today}`;

        try {
            const stats = await redisCircuitBreaker.call(async () => {
                if (!redisConnected) throw new Error('Redis not connected');
                const data = await redisClient.get(key);
                return data ? JSON.parse(data) : null;
            });

            return stats || {
                totalBets: 0,
                totalWagered: 0,
                totalWinnings: 0,
                netResult: 0,
                averageBet: 0,
                largestBet: 0,
                winRate: 0
            };
        } catch (error) {
            logger.warn('Failed to fetch daily stats from Redis', {
                error: error.message,
                userIdHash,
                fallback: 'using default values'
            });

            return {
                totalBets: 0,
                totalWagered: 0,
                totalWinnings: 0,
                netResult: 0,
                averageBet: 0,
                largestBet: 0,
                winRate: 0
            };
        }
    }

    async checkCoolingPeriod(userIdHash) {
        const key = `cooling_period:${userIdHash}`;

        try {
            const coolingEnd = await redisCircuitBreaker.call(async () => {
                if (!redisConnected) throw new Error('Redis not connected');
                return await redisClient.get(key);
            });

            if (coolingEnd) {
                return Date.now() > parseInt(coolingEnd);
            }
            return true;
        } catch (error) {
            logger.warn('Failed to check cooling period', {
                error: error.message,
                userIdHash,
                fallback: 'allowing bet'
            });
            return true; // Default to allowing if can't check
        }
    }

    checkBettingVelocity(session, betAmount) {
        if (session.betCount === 0) return true;

        const timeSinceStart = Date.now() - session.startTime;
        const hoursSinceStart = timeSinceStart / (1000 * 60 * 60);
        const projectedHourlyWager = (session.totalWagered + betAmount) / Math.max(hoursSinceStart, 0.1);

        // Flag if betting more than $500/hour equivalent
        return projectedHourlyWager <= 500;
    }

    assessRiskLevel(checks, session, dailyStats) {
        const failedChecks = Object.values(checks).filter(check => !check).length;
        const riskFlags = session.riskFlags.size;

        if (failedChecks >= 3 || riskFlags >= 4) return 'CRITICAL';
        if (failedChecks >= 2 || riskFlags >= 3) return 'HIGH';
        if (failedChecks >= 1 || riskFlags >= 2) return 'MODERATE';
        if (riskFlags >= 1) return 'LOW';
        return 'MINIMAL';
    }

    determineInterventions(riskLevel, checks) {
        const interventions = [];

        if (riskLevel === 'CRITICAL') {
            interventions.push('BLOCK', 'MANDATORY_BREAK', 'ACCOUNT_REVIEW');
        } else if (riskLevel === 'HIGH') {
            interventions.push('WARNING', 'COOL_DOWN_SUGGEST');
        } else if (riskLevel === 'MODERATE') {
            interventions.push('GENTLE_WARNING');
        }

        if (!checks.sessionTimeLimit) {
            interventions.push('SESSION_BREAK_SUGGEST');
        }

        if (!checks.velocityCheck) {
            interventions.push('VELOCITY_WARNING');
        }

        return interventions;
    }

    generateRecommendations(riskLevel, checks) {
        const recommendations = [];

        if (riskLevel !== 'MINIMAL') {
            recommendations.push('Consider taking a short break');
        }

        if (!checks.velocityCheck) {
            recommendations.push('You\'re betting faster than usual - slow down');
        }

        if (!checks.sessionTimeLimit) {
            recommendations.push('You\'ve been playing for a while - take a break');
        }

        return recommendations;
    }

    sanitizeSessionData(session) {
        return {
            duration: session.duration,
            betCount: session.betCount,
            totalWagered: session.totalWagered,
            consecutiveLosses: session.consecutiveLosses,
            riskFlagCount: session.riskFlags.size
        };
    }

    async logResponsibleGamingEvent(eventData) {
        const event = {
            eventId: uuidv4(),
            timestamp: new Date().toISOString(),
            ...eventData
        };

        // Structured logging
        logger.info('Responsible Gaming Event', {
            eventType: 'responsible_gaming',
            ...event
        });

        // Store in Redis for retrieval
        try {
            await redisCircuitBreaker.call(async () => {
                if (!redisConnected) throw new Error('Redis not connected');
                const key = `rg_event:${event.eventId}`;
                await redisClient.setEx(key, 86400 * 30, JSON.stringify(event)); // 30-day retention
            });
        } catch (error) {
            logger.warn('Failed to store RG event in Redis', {
                error: error.message,
                eventId: event.eventId
            });
        }

        return event.eventId;
    }
}

// Initialize responsible gaming manager
const rgManager = new ResponsibleGamingManager();

// Real-time data manager
class RealTimeDataManager {
    constructor() {
        this.subscribers = new Map();
        this.oddsCache = new Map();
        this.parlayBuilders = new Map();
        this.updateInterval = null;
    }

    subscribe(socketId, topics) {
        this.subscribers.set(socketId, { topics, socket: null });
        logger.info('Client subscribed to topics', { socketId, topics });
    }

    unsubscribe(socketId) {
        this.subscribers.delete(socketId);
        logger.info('Client unsubscribed', { socketId });
    }

    async broadcastOddsUpdate(oddsData) {
        const odds = new BettingOdds(oddsData);
        this.oddsCache.set(odds.id, odds);

        // Broadcast to subscribers
        for (const [socketId, subscriber] of this.subscribers.entries()) {
            if (subscriber.topics.includes('odds') || subscriber.topics.includes(odds.sport)) {
                if (subscriber.socket && subscriber.socket.connected) {
                    subscriber.socket.emit('odds_update', odds);
                }
            }
        }

        // Store in Redis
        try {
            await redisCircuitBreaker.call(async () => {
                if (!redisConnected) throw new Error('Redis not connected');
                await redisClient.setEx(`odds:${odds.id}`, 3600, JSON.stringify(odds));
            });
        } catch (error) {
            logger.warn('Failed to cache odds in Redis', {
                error: error.message,
                oddsId: odds.id
            });
        }

        logger.info('Odds update broadcasted', {
            oddsId: odds.id,
            sport: odds.sport,
            sportsbook: odds.sportsbook,
            subscriberCount: this.subscribers.size
        });
    }

    createParlayBuilder(userId) {
        const builder = new ParlayBuilder();
        this.parlayBuilders.set(builder.id, { builder, userId, lastAccess: Date.now() });

        logger.info('Parlay builder created', {
            parlayId: builder.id,
            userId: this.hashUserId(userId)
        });

        return builder;
    }

    getParlayBuilder(parlayId) {
        const entry = this.parlayBuilders.get(parlayId);
        if (entry) {
            entry.lastAccess = Date.now();
            return entry.builder;
        }
        return null;
    }

    hashUserId(userId) {
        return crypto.createHash('sha256')
            .update(`${userId}:parlay`)
            .digest('hex')
            .substring(0, 16);
    }

    async startRealTimeUpdates() {
        this.updateInterval = setInterval(async () => {
            try {
                // Simulate live odds updates (in production, this would fetch from sportsbook APIs)
                const mockOdds = this.generateMockOddsUpdate();
                await this.broadcastOddsUpdate(mockOdds);

                // Clean up old parlay builders
                const now = Date.now();
                for (const [id, entry] of this.parlayBuilders.entries()) {
                    if (now - entry.lastAccess > 3600000) { // 1 hour timeout
                        this.parlayBuilders.delete(id);
                    }
                }
            } catch (error) {
                logger.error('Error in real-time update cycle', { error: error.message });
            }
        }, 5000); // Update every 5 seconds

        logger.info('Real-time updates started');
    }

    generateMockOddsUpdate() {
        const sports = ['NFL', 'NBA', 'MLB', 'NHL'];
        const sportsbooks = ['DraftKings', 'FanDuel', 'Caesars', 'BetMGM'];
        const markets = ['Moneyline', 'Spread', 'Total', 'Props'];

        return {
            sport: sports[Math.floor(Math.random() * sports.length)],
            league: 'Mock League',
            event: `Team A vs Team B - ${new Date().toLocaleDateString()}`,
            market: markets[Math.floor(Math.random() * markets.length)],
            selection: Math.random() > 0.5 ? 'Team A' : 'Team B',
            odds: Math.floor(Math.random() * 600) - 300, // -300 to +300
            sportsbook: sportsbooks[Math.floor(Math.random() * sportsbooks.length)],
            confidence: 0.8 + Math.random() * 0.2, // 80-100%
            volume: Math.floor(Math.random() * 10000),
            lineMovement: (Math.random() - 0.5) * 20 // -10 to +10
        };
    }

    stopRealTimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            logger.info('Real-time updates stopped');
        }
    }
}

// Initialize real-time data manager
const dataManager = new RealTimeDataManager();

// OpenAI integration for betting analysis
class BettingAnalysisEngine {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.rateLimiter = {
            requests: 0,
            tokens: 0,
            resetTime: Date.now() + 60000
        };
    }

    async analyzeParlayWithLLM(parlayBuilder, userPreferences = {}) {
        if (!this.apiKey) {
            throw new Error('OpenAI API key not configured');
        }

        await this.checkRateLimits();

        const prompt = this.buildAnalysisPrompt(parlayBuilder, userPreferences);

        try {
            const response = await openaiCircuitBreaker.call(async () => {
                const { OpenAI } = require('openai');
                const openai = new OpenAI({ apiKey: this.apiKey });

                return await openai.chat.completions.create({
                    model: config.openai.model,
                    messages: [
                        {
                            role: "system",
                            content: "You are an expert sports betting analyst specializing in expected value, Kelly criterion, and risk assessment. Provide actionable insights in JSON format."
                        },
                        {
                            role: "user",
                            content: prompt
                        }
                    ],
                    max_tokens: 1000,
                    temperature: 0.1,
                    response_format: { type: "json_object" }
                });
            });

            this.updateTokenUsage(response.usage);

            const analysis = JSON.parse(response.choices[0].message.content);

            logger.info('LLM parlay analysis completed', {
                parlayId: parlayBuilder.id,
                legCount: parlayBuilder.legs.length,
                tokensUsed: response.usage.total_tokens,
                recommendation: analysis.recommendation
            });

            return analysis;

        } catch (error) {
            logger.error('LLM analysis failed', {
                error: error.message,
                parlayId: parlayBuilder.id,
                fallback: 'using heuristic analysis'
            });

            // Fallback to heuristic analysis
            return this.fallbackAnalysis(parlayBuilder);
        }
    }

    buildAnalysisPrompt(parlayBuilder, userPreferences) {
        const parlay = parlayBuilder.toJSON();

        return `
Analyze this sports betting parlay for expected value, risk, and correlations:

PARLAY DETAILS:
- Legs: ${parlay.legCount}
- Combined Odds: ${parlay.combinedOdds.american > 0 ? '+' : ''}${parlay.combinedOdds.american}
- Implied Probability: ${(parlay.combinedOdds.impliedProbability * 100).toFixed(1)}%

LEGS:
${parlay.legs.map((leg, i) =>
            `${i + 1}. ${leg.selection} (${leg.market})
   - Odds: ${leg.odds > 0 ? '+' : ''}${leg.odds}
   - Sportsbook: ${leg.sportsbook}
   - Sport: ${leg.sport}`
        ).join('\n')}

USER PREFERENCES:
- Risk Tolerance: ${userPreferences.riskTolerance || 'moderate'}
- Bankroll: ${userPreferences.bankroll || 'not specified'}

Provide analysis in this JSON format:
{
  "recommendation": "BET|PASS|REDUCE_STAKE|SPLIT",
  "confidence": 0.0-1.0,
  "expectedValue": number,
  "trueProbability": 0.0-1.0,
  "correlationRisk": 0.0-1.0,
  "kellyFraction": 0.0-1.0,
  "riskFactors": ["list of risks"],
  "valueLegs": ["legs offering value"],
  "reasoning": "brief explanation"
}`;
    }

    fallbackAnalysis(parlayBuilder) {
        const parlay = parlayBuilder.toJSON();
        const correlation = parlay.correlationRisk;

        // Simple heuristic analysis
        const trueProbability = Math.max(0.1, parlay.combinedOdds.impliedProbability * 0.9); // Assume 10% house edge
        const expectedValue = (trueProbability - parlay.combinedOdds.impliedProbability) * 100;

        let recommendation = 'PASS';
        if (expectedValue > 2 && correlation.risk < 0.5) recommendation = 'BET';
        else if (expectedValue > 0 && correlation.risk < 0.7) recommendation = 'REDUCE_STAKE';
        else if (parlay.legCount > 4 && correlation.risk > 0.6) recommendation = 'SPLIT';

        return {
            recommendation,
            confidence: 0.3, // Low confidence for fallback
            expectedValue,
            trueProbability,
            correlationRisk: correlation.risk,
            kellyFraction: Math.max(0, Math.min(0.1, expectedValue / 100)),
            riskFactors: ['LLM analysis unavailable', 'Using heuristic fallback'],
            valueLegs: [],
            reasoning: 'Fallback analysis due to LLM service unavailability'
        };
    }

    async checkRateLimits() {
        const now = Date.now();

        if (now > this.rateLimiter.resetTime) {
            this.rateLimiter.requests = 0;
            this.rateLimiter.tokens = 0;
            this.rateLimiter.resetTime = now + 60000;
        }

        if (this.rateLimiter.requests >= 50) {
            throw new Error('OpenAI request rate limit exceeded');
        }

        if (this.rateLimiter.tokens >= 40000) {
            throw new Error('OpenAI token rate limit exceeded');
        }

        this.rateLimiter.requests++;
    }

    updateTokenUsage(usage) {
        this.rateLimiter.tokens += usage.total_tokens;
    }
}

// Initialize betting analysis engine
const analysisEngine = new BettingAnalysisEngine(config.openai.apiKey);

// API Routes

// Health check endpoint
app.get('/api/health', async (req, res) => {
    const health = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '2.1.0',
        services: {
            redis: redisConnected,
            openai: !!config.openai.apiKey,
            responsibleGaming: config.responsibleGaming.enableProtections
        },
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        activeConnections: io.engine.clientsCount
    };

    logger.info('Health check requested', {
        requestId: req.requestId,
        services: health.services
    });

    res.json(health);
});

// Get current odds
app.get('/api/odds', async (req, res) => {
    try {
        const { sport, sportsbook, limit = 50 } = req.query;

        const odds = Array.from(dataManager.oddsCache.values())
            .filter(odd => {
                if (sport && odd.sport !== sport) return false;
                if (sportsbook && odd.sportsbook !== sportsbook) return false;
                return true;
            })
            .slice(0, parseInt(limit));

        logger.info('Odds data requested', {
            requestId: req.requestId,
            filters: { sport, sportsbook },
            resultCount: odds.length
        });

        res.json({
            odds,
            count: odds.length,
            lastUpdate: new Date().toISOString()
        });

    } catch (error) {
        logger.error('Failed to fetch odds', {
            requestId: req.requestId,
            error: error.message
        });

        res.status(500).json({
            error: 'Failed to fetch odds',
            requestId: req.requestId
        });
    }
});

// Create new parlay
app.post('/api/parlay', async (req, res) => {
    try {
        const { userId, legs = [] } = req.body;

        if (!userId) {
            return res.status(400).json({ error: 'User ID required' });
        }

        const builder = dataManager.createParlayBuilder(userId);

        // Add legs if provided
        for (const legData of legs) {
            const odds = new BettingOdds(legData);
            builder.addLeg(odds);
        }

        logger.info('Parlay created', {
            requestId: req.requestId,
            parlayId: builder.id,
            userId: dataManager.hashUserId(userId),
            legCount: builder.legs.length
        });

        res.json({
            parlayId: builder.id,
            parlay: builder.toJSON(),
            message: 'Parlay created successfully'
        });

    } catch (error) {
        logger.error('Failed to create parlay', {
            requestId: req.requestId,
            error: error.message
        });

        res.status(500).json({
            error: 'Failed to create parlay',
            requestId: req.requestId
        });
    }
});

// Add leg to parlay
app.post('/api/parlay/:parlayId/legs', async (req, res) => {
    try {
        const { parlayId } = req.params;
        const legData = req.body;

        const builder = dataManager.getParlayBuilder(parlayId);
        if (!builder) {
            return res.status(404).json({ error: 'Parlay not found' });
        }

        const odds = new BettingOdds(legData);
        builder.addLeg(odds);

        logger.info('Leg added to parlay', {
            requestId: req.requestId,
            parlayId,
            legCount: builder.legs.length,
            selection: odds.selection
        });

        res.json({
            parlay: builder.toJSON(),
            message: 'Leg added successfully'
        });

    } catch (error) {
        logger.error('Failed to add leg to parlay', {
            requestId: req.requestId,
            error: error.message
        });

        res.status(500).json({
            error: 'Failed to add leg',
            requestId: req.requestId
        });
    }
});

// Analyze parlay with AI
app.post('/api/parlay/:parlayId/analyze', async (req, res) => {
    try {
        const { parlayId } = req.params;
        const { userId, stake = 100, userPreferences = {} } = req.body;

        const builder = dataManager.getParlayBuilder(parlayId);
        if (!builder) {
            return res.status(404).json({ error: 'Parlay not found' });
        }

        if (builder.legs.length === 0) {
            return res.status(400).json({ error: 'Parlay must have at least one leg' });
        }

        // Responsible gaming check
        const rgCheck = await rgManager.checkBettingLimits(userId, stake, 'parlay');

        if (!rgCheck.allowed) {
            logger.warn('Bet blocked by responsible gaming protections', {
                requestId: req.requestId,
                userId: rgManager.hashUserId(userId),
                riskLevel: rgCheck.riskLevel,
                interventions: rgCheck.interventions
            });

            return res.status(403).json({
                error: 'Bet not allowed',
                responsibleGaming: rgCheck,
                message: 'This bet has been blocked for your protection'
            });
        }

        // Get LLM analysis
        const llmAnalysis = await analysisEngine.analyzeParlayWithLLM(builder, userPreferences);

        // Calculate Kelly criterion
        const parlay = builder.toJSON();
        const kelly = parlay.legs[0]?.calculateKellyFraction(llmAnalysis.trueProbability, userPreferences.bankroll || 1000);

        const analysis = {
            parlayId,
            parlay: parlay,
            stake,
            llmAnalysis,
            kellyAnalysis: kelly,
            responsibleGaming: rgCheck,
            payout: parlay.combinedOdds.payout(stake),
            recommendations: {
                action: llmAnalysis.recommendation,
                optimalStake: kelly?.recommendedBet || null,
                reasoning: llmAnalysis.reasoning
            },
            timestamp: new Date().toISOString()
        };

        logger.info('Parlay analysis completed', {
            requestId: req.requestId,
            parlayId,
            recommendation: llmAnalysis.recommendation,
            confidence: llmAnalysis.confidence,
            stake,
            payout: analysis.payout
        });

        res.json(analysis);

    } catch (error) {
        logger.error('Parlay analysis failed', {
            requestId: req.requestId,
            parlayId,
            error: error.message
        });

        res.status(500).json({
            error: 'Analysis failed',
            requestId: req.requestId
        });
    }
});

// Get responsible gaming status
app.get('/api/responsible-gaming/:userId', async (req, res) => {
    try {
        const { userId } = req.params;
        const userIdHash = rgManager.hashUserId(userId);

        const session = rgManager.getUserSession(userIdHash);
        const dailyStats = await rgManager.getDailyStats(userIdHash);

        const status = {
            session: rgManager.sanitizeSessionData(session),
            dailyStats,
            limits: config.responsibleGaming,
            recommendations: []
        };

        if (session.duration > config.responsibleGaming.maxSessionTime * 60000 * 0.8) {
            status.recommendations.push('Consider taking a break soon');
        }

        if (dailyStats.totalBets > config.responsibleGaming.maxDailyBets * 0.8) {
            status.recommendations.push('Approaching daily bet limit');
        }

        res.json(status);

    } catch (error) {
        logger.error('Failed to get responsible gaming status', {
            requestId: req.requestId,
            error: error.message
        });

        res.status(500).json({
            error: 'Failed to get status',
            requestId: req.requestId
        });
    }
});

// Serve dashboard UI
app.get('/dashboard', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 Sports Betting Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="/socket.io/socket.io.js"></script>
    <style>
        .fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .pulse-green { animation: pulse-green 2s infinite; }
        @keyframes pulse-green {
            0%, 100% { background-color: rgb(34, 197, 94); }
            50% { background-color: rgb(22, 163, 74); }
        }
    </style>
</head>
<body class="bg-gray-900 text-white min-h-screen">
    <div id="app" class="container mx-auto px-4 py-8">
        <header class="mb-8">
            <h1 class="text-4xl font-bold text-center mb-2">🎯 EQ12 Sports Betting Analytics</h1>
            <p class="text-gray-400 text-center">Real-time odds, Kelly criterion, and responsible gaming</p>
            <div id="connection-status" class="text-center mt-4">
                <span class="bg-red-500 px-3 py-1 rounded-full text-sm">Connecting...</span>
            </div>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Live Odds Feed -->
            <div class="lg:col-span-2">
                <div class="bg-gray-800 rounded-lg p-6">
                    <h2 class="text-2xl font-semibold mb-4">📊 Live Odds Feed</h2>
                    <div id="odds-container" class="space-y-3 max-h-96 overflow-y-auto">
                        <div class="text-gray-400 text-center py-8">Connecting to live feed...</div>
                    </div>
                </div>
            </div>

            <!-- Parlay Builder -->
            <div>
                <div class="bg-gray-800 rounded-lg p-6 mb-6">
                    <h2 class="text-xl font-semibold mb-4">🎲 Parlay Builder</h2>
                    <div id="parlay-legs" class="space-y-2 mb-4">
                        <div class="text-gray-400 text-sm">Add legs to build your parlay</div>
                    </div>
                    <div id="parlay-summary" class="bg-gray-700 rounded p-3 mb-4 hidden">
                        <div class="text-sm text-gray-300">Combined Odds:</div>
                        <div id="combined-odds" class="text-lg font-bold">-</div>
                        <div class="text-sm text-gray-300 mt-2">Potential Payout ($100):</div>
                        <div id="potential-payout" class="text-lg font-bold text-green-400">-</div>
                    </div>
                    <button id="analyze-parlay" class="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded font-semibold disabled:opacity-50" disabled>
                        Analyze Parlay
                    </button>
                </div>

                <!-- Responsible Gaming -->
                <div class="bg-gray-800 rounded-lg p-6">
                    <h2 class="text-xl font-semibold mb-4">🛡️ Responsible Gaming</h2>
                    <div id="rg-status" class="space-y-2">
                        <div class="flex justify-between">
                            <span class="text-gray-400">Session Time:</span>
                            <span id="session-time">0m</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">Daily Bets:</span>
                            <span id="daily-bets">0</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-400">Status:</span>
                            <span id="rg-level" class="text-green-400">NORMAL</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analysis Results -->
        <div id="analysis-results" class="mt-8 hidden">
            <div class="bg-gray-800 rounded-lg p-6">
                <h2 class="text-2xl font-semibold mb-4">🤖 AI Analysis Results</h2>
                <div id="analysis-content" class="space-y-4">
                    <!-- Analysis content will be populated here -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // Dashboard JavaScript
        const socket = io();
        let currentParlay = null;
        let sessionStartTime = Date.now();

        // Connection handling
        socket.on('connect', () => {
            document.getElementById('connection-status').innerHTML =
                '<span class="bg-green-500 px-3 py-1 rounded-full text-sm pulse-green">Connected</span>';
            socket.emit('subscribe', ['odds', 'NFL', 'NBA']);
        });

        socket.on('disconnect', () => {
            document.getElementById('connection-status').innerHTML =
                '<span class="bg-red-500 px-3 py-1 rounded-full text-sm">Disconnected</span>';
        });

        // Live odds updates
        socket.on('odds_update', (odds) => {
            addOddsToFeed(odds);
        });

        function addOddsToFeed(odds) {
            const container = document.getElementById('odds-container');

            // Remove "connecting" message
            if (container.children.length === 1 && container.children[0].textContent.includes('Connecting')) {
                container.innerHTML = '';
            }

            const oddsElement = document.createElement('div');
            oddsElement.className = 'bg-gray-700 rounded p-3 fade-in cursor-pointer hover:bg-gray-600';
            oddsElement.innerHTML = \`
                <div class="flex justify-between items-center">
                    <div>
                        <div class="font-semibold">\${odds.selection}</div>
                        <div class="text-sm text-gray-400">\${odds.sport} • \${odds.market}</div>
                        <div class="text-xs text-gray-500">\${odds.sportsbook}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-lg font-bold \${odds.odds > 0 ? 'text-green-400' : 'text-red-400'}">
                            \${odds.odds > 0 ? '+' : ''}\${odds.odds}
                        </div>
                        <div class="text-sm text-gray-400">\${(odds.impliedProbability * 100).toFixed(1)}%</div>
                    </div>
                </div>
            \`;

            oddsElement.onclick = () => addToParlayBuilder(odds);

            container.insertBefore(oddsElement, container.firstChild);

            // Keep only last 20 odds
            while (container.children.length > 20) {
                container.removeChild(container.lastChild);
            }
        }

        // Parlay builder functions
        async function addToParlayBuilder(odds) {
            if (!currentParlay) {
                // Create new parlay
                const response = await fetch('/api/parlay', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userId: 'demo_user', legs: [odds] })
                });
                const result = await response.json();
                currentParlay = result.parlayId;
            } else {
                // Add to existing parlay
                await fetch(\`/api/parlay/\${currentParlay}/legs\`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(odds)
                });
            }

            updateParlayDisplay();
        }

        async function updateParlayDisplay() {
            if (!currentParlay) return;

            try {
                const response = await fetch(\`/api/parlay/\${currentParlay}/legs\`, {
                    method: 'GET'
                });
                const parlay = await response.json();

                const legsContainer = document.getElementById('parlay-legs');
                const summary = document.getElementById('parlay-summary');

                if (parlay.legs && parlay.legs.length > 0) {
                    legsContainer.innerHTML = parlay.legs.map((leg, i) => \`
                        <div class="bg-gray-700 rounded p-2 text-sm">
                            <div class="font-semibold">\${leg.selection}</div>
                            <div class="text-gray-400">\${leg.odds > 0 ? '+' : ''}\${leg.odds}</div>
                        </div>
                    \`).join('');

                    document.getElementById('combined-odds').textContent =
                        \`\${parlay.combinedOdds.american > 0 ? '+' : ''}\${parlay.combinedOdds.american}\`;
                    document.getElementById('potential-payout').textContent =
                        \`$\${parlay.combinedOdds.payout(100).toFixed(2)}\`;

                    summary.classList.remove('hidden');
                    document.getElementById('analyze-parlay').disabled = false;
                }
            } catch (error) {
                console.error('Failed to update parlay display:', error);
            }
        }

        // Analysis
        document.getElementById('analyze-parlay').onclick = async () => {
            if (!currentParlay) return;

            const button = document.getElementById('analyze-parlay');
            button.disabled = true;
            button.textContent = 'Analyzing...';

            try {
                const response = await fetch(\`/api/parlay/\${currentParlay}/analyze\`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        userId: 'demo_user',
                        stake: 100,
                        userPreferences: { riskTolerance: 'moderate', bankroll: 1000 }
                    })
                });

                const analysis = await response.json();
                displayAnalysisResults(analysis);

            } catch (error) {
                console.error('Analysis failed:', error);
                alert('Analysis failed. Please try again.');
            } finally {
                button.disabled = false;
                button.textContent = 'Analyze Parlay';
            }
        };

        function displayAnalysisResults(analysis) {
            const container = document.getElementById('analysis-results');
            const content = document.getElementById('analysis-content');

            const recommendation = analysis.llmAnalysis.recommendation;
            const confidence = analysis.llmAnalysis.confidence;

            content.innerHTML = \`
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <h3 class="text-lg font-semibold mb-3">🎯 Recommendation</h3>
                        <div class="bg-gray-700 rounded p-4">
                            <div class="text-2xl font-bold mb-2 \${
                                recommendation === 'BET' ? 'text-green-400' :
                                recommendation === 'PASS' ? 'text-red-400' : 'text-yellow-400'
                            }">\${recommendation}</div>
                            <div class="text-sm text-gray-300">Confidence: \${(confidence * 100).toFixed(1)}%</div>
                            <div class="text-sm text-gray-400 mt-2">\${analysis.llmAnalysis.reasoning}</div>
                        </div>
                    </div>

                    <div>
                        <h3 class="text-lg font-semibold mb-3">📊 Analysis Metrics</h3>
                        <div class="bg-gray-700 rounded p-4 space-y-2">
                            <div class="flex justify-between">
                                <span>Expected Value:</span>
                                <span class="\${analysis.llmAnalysis.expectedValue > 0 ? 'text-green-400' : 'text-red-400'}">
                                    \${analysis.llmAnalysis.expectedValue.toFixed(2)}%
                                </span>
                            </div>
                            <div class="flex justify-between">
                                <span>True Probability:</span>
                                <span>\${(analysis.llmAnalysis.trueProbability * 100).toFixed(1)}%</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Correlation Risk:</span>
                                <span class="\${analysis.llmAnalysis.correlationRisk > 0.7 ? 'text-red-400' :
                                    analysis.llmAnalysis.correlationRisk > 0.4 ? 'text-yellow-400' : 'text-green-400'}">
                                    \${(analysis.llmAnalysis.correlationRisk * 100).toFixed(1)}%
                                </span>
                            </div>
                            <div class="flex justify-between">
                                <span>Kelly Fraction:</span>
                                <span>\${(analysis.llmAnalysis.kellyFraction * 100).toFixed(1)}%</span>
                            </div>
                        </div>
                    </div>
                </div>

                \${analysis.llmAnalysis.riskFactors.length > 0 ? \`
                <div class="mt-4">
                    <h3 class="text-lg font-semibold mb-3">⚠️ Risk Factors</h3>
                    <div class="bg-gray-700 rounded p-4">
                        <ul class="space-y-1">
                            \${analysis.llmAnalysis.riskFactors.map(risk => \`<li class="text-yellow-400">• \${risk}</li>\`).join('')}
                        </ul>
                    </div>
                </div>
                \` : ''}

                \${analysis.responsibleGaming.interventions.length > 0 ? \`
                <div class="mt-4">
                    <h3 class="text-lg font-semibold mb-3">🛡️ Responsible Gaming</h3>
                    <div class="bg-yellow-900 border border-yellow-600 rounded p-4">
                        <div class="text-yellow-200">Risk Level: \${analysis.responsibleGaming.riskLevel}</div>
                        \${analysis.responsibleGaming.recommendations.map(rec => \`
                            <div class="text-yellow-300 text-sm mt-1">• \${rec}</div>
                        \`).join('')}
                    </div>
                </div>
                \` : ''}
            \`;

            container.classList.remove('hidden');
            container.scrollIntoView({ behavior: 'smooth' });
        }

        // Responsible gaming status updates
        function updateRGStatus() {
            const sessionTime = Math.floor((Date.now() - sessionStartTime) / 60000);
            document.getElementById('session-time').textContent = \`\${sessionTime}m\`;

            // Simulated daily bets (in real app, fetch from API)
            const dailyBets = Math.floor(Math.random() * 10);
            document.getElementById('daily-bets').textContent = dailyBets;

            // Update status based on session time
            const rgLevel = document.getElementById('rg-level');
            if (sessionTime > 180) {
                rgLevel.textContent = 'EXTENDED SESSION';
                rgLevel.className = 'text-red-400';
            } else if (sessionTime > 120) {
                rgLevel.textContent = 'LONG SESSION';
                rgLevel.className = 'text-yellow-400';
            } else {
                rgLevel.textContent = 'NORMAL';
                rgLevel.className = 'text-green-400';
            }
        }

        // Update RG status every minute
        setInterval(updateRGStatus, 60000);
        updateRGStatus();

        // Initial load
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🎯 EQ12 Sports Betting Dashboard loaded');
        });
    </script>
</body>
</html>
    `);
});

// Socket.IO connection handling
io.on('connection', (socket) => {
    logger.info('Client connected', {
        socketId: socket.id,
        userAgent: socket.handshake.headers['user-agent'],
        ip: socket.handshake.address
    });

    socket.on('subscribe', (topics) => {
        dataManager.subscribe(socket.id, topics);
        dataManager.subscribers.get(socket.id).socket = socket;
    });

    socket.on('unsubscribe', () => {
        dataManager.unsubscribe(socket.id);
    });

    socket.on('disconnect', (reason) => {
        logger.info('Client disconnected', {
            socketId: socket.id,
            reason
        });
        dataManager.unsubscribe(socket.id);
    });
});

// Initialize Redis connection
async function initializeRedis() {
    try {
        redisClient = redis.createClient({
            url: config.redis.url,
            database: config.redis.db
        });

        redisClient.on('error', (err) => {
            logger.error('Redis connection error', { error: err.message });
            redisConnected = false;
        });

        redisClient.on('connect', () => {
            logger.info('Redis connected successfully');
            redisConnected = true;
        });

        redisClient.on('ready', () => {
            logger.info('Redis ready for operations');
        });

        await redisClient.connect();

    } catch (error) {
        logger.warn('Failed to connect to Redis, running without caching', {
            error: error.message
        });
        redisConnected = false;
    }
}

// Graceful shutdown
process.on('SIGINT', async () => {
    logger.info('Received SIGINT, shutting down gracefully');

    dataManager.stopRealTimeUpdates();

    if (redisClient) {
        await redisClient.quit();
    }

    server.close(() => {
        logger.info('Server shut down complete');
        process.exit(0);
    });
});

process.on('SIGTERM', async () => {
    logger.info('Received SIGTERM, shutting down gracefully');

    dataManager.stopRealTimeUpdates();

    if (redisClient) {
        await redisClient.quit();
    }

    server.close(() => {
        logger.info('Server shut down complete');
        process.exit(0);
    });
});

// Error handling
process.on('uncaughtException', (error) => {
    logger.error('Uncaught Exception', {
        error: error.message,
        stack: error.stack
    });
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    logger.error('Unhandled Rejection', {
        reason: reason,
        promise: promise
    });
});

// Start server
async function startServer() {
    try {
        // Initialize Redis
        await initializeRedis();

        // Start real-time data updates
        dataManager.startRealTimeUpdates();

        // Start HTTP server
        server.listen(config.port, () => {
            logger.info('EQ12 Sports Betting Dashboard Server started', {
                port: config.port,
                environment: process.env.NODE_ENV || 'development',
                features: {
                    redis: redisConnected,
                    openai: !!config.openai.apiKey,
                    responsibleGaming: config.responsibleGaming.enableProtections
                }
            });

            console.log(`
🎯 EQ12 SPORTS BETTING DASHBOARD READY
=====================================
🌐 Dashboard: http://localhost:${config.port}/dashboard
🔥 Health Check: http://localhost:${config.port}/api/health
📊 API Docs: http://localhost:${config.port}/api/odds
🛡️ Responsible Gaming: ${config.responsibleGaming.enableProtections ? 'ENABLED' : 'DISABLED'}
🔗 Redis: ${redisConnected ? 'CONNECTED' : 'OFFLINE'}
🤖 OpenAI: ${config.openai.apiKey ? 'CONFIGURED' : 'NOT CONFIGURED'}
=====================================
            `);
        });

    } catch (error) {
        logger.error('Failed to start server', { error: error.message });
        process.exit(1);
    }
}

// Start the server
startServer();
