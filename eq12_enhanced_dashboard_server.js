// eq12_enhanced_dashboard_server.js
/**
 * EQ12 Enhanced Dashboard Server with Health Monitoring and Intelligent Redirects
 * Provides robust health endpoints, circuit breakers, and seamless user experience
 */

import express from 'express';
import http from 'http';
import { Server as SocketIO } from 'socket.io';
import path from 'path';
const fs = require('fs').promises;
const { createWriteStream } = require('fs');
const redis = require('redis');
const { promisify } = require('util');

// Enhanced logging with UTF-8 support
const logStream = createWriteStream('C:/EQ12/logs/dashboard_server.log', {
    flags: 'a',
    encoding: 'utf8'
});

function logMessage(level, message, data = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = JSON.stringify({
        timestamp,
        level,
        service: 'dashboard_server',
        message,
        data,
        pid: process.pid
    });

    console.log(`[${level}] ${message}`);
    logStream.write(logEntry + '\n');
}

// Service status tracking
class ServiceStatus {
    constructor() {
        this.services = {
            express: { status: 'starting', lastCheck: null, errors: 0 },
            redis: { status: 'unknown', lastCheck: null, errors: 0 },
            socketio: { status: 'starting', lastCheck: null, errors: 0 },
            llm: { status: 'unknown', lastCheck: null, errors: 0 },
            filesystem: { status: 'unknown', lastCheck: null, errors: 0 }
        };
        this.startTime = Date.now();
    }

    updateService(name, status, error = null) {
        if (this.services[name]) {
            this.services[name].status = status;
            this.services[name].lastCheck = Date.now();
            if (error) {
                this.services[name].errors++;
                this.services[name].lastError = error;
            }
        }
    }

    getOverallHealth() {
        const statuses = Object.values(this.services);
        const healthy = statuses.filter(s => s.status === 'healthy').length;
        const total = statuses.length;

        if (healthy === total) return 'healthy';
        if (healthy >= total * 0.75) return 'degraded';
        return 'failing';
    }

    getStatus() {
        return {
            timestamp: new Date().toISOString(),
            uptime: Date.now() - this.startTime,
            overall: this.getOverallHealth(),
            services: this.services,
            memory: process.memoryUsage(),
            node_version: process.version
        };
    }
}

// Circuit breaker for external services
class CircuitBreaker {
    constructor(threshold = 5, timeout = 60000, monitoringPeriod = 60000) {
        this.threshold = threshold;
        this.timeout = timeout;
        this.monitoringPeriod = monitoringPeriod;
        this.failures = 0;
        this.lastFailureTime = null;
        this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
        this.nextAttempt = 0;
    }

    async execute(operation, fallback) {
        if (this.state === 'OPEN') {
            if (Date.now() > this.nextAttempt) {
                this.state = 'HALF_OPEN';
            } else {
                logMessage('WARN', 'Circuit breaker is OPEN, using fallback');
                return fallback();
            }
        }

        try {
            const result = await operation();
            this.onSuccess();
            return result;
        } catch (error) {
            this.onFailure();
            throw error;
        }
    }

    onSuccess() {
        this.failures = 0;
        this.state = 'CLOSED';
    }

    onFailure() {
        this.failures++;
        this.lastFailureTime = Date.now();

        if (this.failures >= this.threshold) {
            this.state = 'OPEN';
            this.nextAttempt = Date.now() + this.timeout;
            logMessage('ERROR', `Circuit breaker opened after ${this.failures} failures`);
        }
    }
}

// Rate limiter for API endpoints
class RateLimiter {
    constructor(maxRequests = 100, windowMs = 60000) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
        this.requests = new Map();
    }

    isAllowed(identifier) {
        const now = Date.now();
        const windowStart = now - this.windowMs;

        // Clean old requests
        for (const [id, timestamps] of this.requests.entries()) {
            const validTimestamps = timestamps.filter(t => t > windowStart);
            if (validTimestamps.length === 0) {
                this.requests.delete(id);
            } else {
                this.requests.set(id, validTimestamps);
            }
        }

        // Check current requests
        const currentRequests = this.requests.get(identifier) || [];
        if (currentRequests.length >= this.maxRequests) {
            return false;
        }

        // Add current request
        currentRequests.push(now);
        this.requests.set(identifier, currentRequests);
        return true;
    }
}

// Initialize services
const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

const serviceStatus = new ServiceStatus();
const circuitBreaker = new CircuitBreaker();
const rateLimiter = new RateLimiter(200, 60000); // 200 requests per minute

// Redis client with error handling
let redisClient = null;
async function initializeRedis() {
    try {
        redisClient = redis.createClient({
            url: process.env.REDIS_URL || 'redis://localhost:6379/0',
            retry_strategy: (options) => {
                if (options.error && options.error.code === 'ECONNREFUSED') {
                    return new Error('Redis server connection refused');
                }
                if (options.total_retry_time > 1000 * 60 * 60) {
                    return new Error('Retry time exhausted');
                }
                return Math.min(options.attempt * 100, 3000);
            }
        });

        redisClient.on('error', (err) => {
            logMessage('ERROR', 'Redis error', { error: err.message });
            serviceStatus.updateService('redis', 'failing', err.message);
        });

        redisClient.on('connect', () => {
            logMessage('INFO', 'Redis connected');
            serviceStatus.updateService('redis', 'healthy');
        });

        await redisClient.connect();
    } catch (error) {
        logMessage('WARN', 'Redis initialization failed', { error: error.message });
        serviceStatus.updateService('redis', 'failing', error.message);
    }
}

// Middleware setup
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting middleware
app.use((req, res, next) => {
    const identifier = req.ip || req.connection.remoteAddress;
    if (!rateLimiter.isAllowed(identifier)) {
        return res.status(429).json({
            error: 'Too many requests',
            retryAfter: 60
        });
    }
    next();
});

// Request logging middleware
app.use((req, res, next) => {
    const startTime = Date.now();
    res.on('finish', () => {
        const duration = Date.now() - startTime;
        logMessage('INFO', 'Request completed', {
            method: req.method,
            path: req.path,
            status: res.statusCode,
            duration: `${duration}ms`,
            ip: req.ip
        });
    });
    next();
});

// Health check endpoint with comprehensive diagnostics
app.get('/health', async (req, res) => {
    try {
        const healthData = serviceStatus.getStatus();

        // Test filesystem
        try {
            await fs.access('C:/EQ12/logs', fs.constants.W_OK);
            serviceStatus.updateService('filesystem', 'healthy');
        } catch (error) {
            serviceStatus.updateService('filesystem', 'failing', error.message);
        }

        // Test Redis if available
        if (redisClient && redisClient.isReady) {
            try {
                await redisClient.ping();
                serviceStatus.updateService('redis', 'healthy');
            } catch (error) {
                serviceStatus.updateService('redis', 'failing', error.message);
            }
        }

        const status = serviceStatus.getStatus();
        const httpStatus = status.overall === 'healthy' ? 200 :
            status.overall === 'degraded' ? 200 : 503;

        res.status(httpStatus).json({
            status: status.overall,
            timestamp: status.timestamp,
            uptime: Math.floor(status.uptime / 1000),
            services: status.services,
            version: "2.0.0",
            environment: process.env.NODE_ENV || 'development'
        });

    } catch (error) {
        logMessage('ERROR', 'Health check failed', { error: error.message });
        res.status(503).json({
            status: 'error',
            message: 'Health check failed',
            timestamp: new Date().toISOString()
        });
    }
});

// Deep health check for monitoring systems
app.get('/health/deep', async (req, res) => {
    const checks = {};
    let overallHealthy = true;

    // Check database connectivity
    checks.database = await circuitBreaker.execute(
        async () => {
            // Simulate database check
            await new Promise(resolve => setTimeout(resolve, 10));
            return { status: 'healthy', responseTime: '10ms' };
        },
        () => ({ status: 'failing', error: 'Database unavailable' })
    ).catch(() => {
        overallHealthy = false;
        return { status: 'failing', error: 'Circuit breaker open' };
    });

    // Check external APIs
    checks.externalApis = await circuitBreaker.execute(
        async () => {
            // In production, test actual external API connections
            return { status: 'healthy', services: ['openai', 'sportsbooks'] };
        },
        () => ({ status: 'degraded', message: 'External APIs unavailable' })
    ).catch(() => {
        return { status: 'failing', error: 'All external APIs down' };
    });

    // Memory and performance checks
    const memory = process.memoryUsage();
    checks.performance = {
        memory: {
            used: Math.round(memory.heapUsed / 1024 / 1024),
            total: Math.round(memory.heapTotal / 1024 / 1024),
            limit: Math.round(memory.rss / 1024 / 1024)
        },
        uptime: Math.floor(process.uptime()),
        eventLoopLag: await measureEventLoopLag()
    };

    res.status(overallHealthy ? 200 : 503).json({
        status: overallHealthy ? 'healthy' : 'failing',
        timestamp: new Date().toISOString(),
        checks
    });
});

// Measure event loop lag
function measureEventLoopLag() {
    return new Promise((resolve) => {
        const start = process.hrtime.bigint();
        setImmediate(() => {
            const lag = Number(process.hrtime.bigint() - start) / 1000000; // Convert to ms
            resolve(Math.round(lag * 100) / 100);
        });
    });
}

// Root redirect with intelligent routing
app.get('/', (req, res) => {
    // Check if request is from a monitoring system
    const userAgent = req.get('User-Agent') || '';
    const isMonitoring = /ping|monitor|health|check|uptime/i.test(userAgent);

    if (isMonitoring) {
        // Redirect monitoring requests to health endpoint
        return res.redirect(302, '/health');
    }

    // Check if dashboard is available
    const dashboardStatus = serviceStatus.services.express.status;
    if (dashboardStatus === 'failing') {
        // Redirect to status page if dashboard is failing
        return res.redirect(302, '/status');
    }

    // Standard redirect to dashboard
    res.redirect(302, '/dashboard');
});

// Main dashboard endpoint
app.get('/dashboard', async (req, res) => {
    try {
        const dashboardHtml = await generateDashboard();
        res.type('html').send(dashboardHtml);
        serviceStatus.updateService('express', 'healthy');
    } catch (error) {
        logMessage('ERROR', 'Dashboard generation failed', { error: error.message });
        serviceStatus.updateService('express', 'failing', error.message);

        // Fallback to simple dashboard
        res.type('html').send(generateFallbackDashboard());
    }
});

// Status page for system information
app.get('/status', (req, res) => {
    const status = serviceStatus.getStatus();
    const statusHtml = generateStatusPage(status);
    res.type('html').send(statusHtml);
});

// API endpoint for parlay analysis
app.post('/api/parlay/analyze', async (req, res) => {
    try {
        const { legs } = req.body;
        if (!legs || !Array.isArray(legs)) {
            return res.status(400).json({ error: 'Invalid parlay legs data' });
        }

        // Use circuit breaker for external LLM analysis
        const analysis = await circuitBreaker.execute(
            async () => {
                // In production, this would call the Python LLM service
                return {
                    recommendation: 'BET',
                    confidence: 0.78,
                    expectedValue: 12.5,
                    kellyFraction: 0.08,
                    riskLevel: 'MEDIUM'
                };
            },
            () => ({
                recommendation: 'PASS',
                confidence: 0.1,
                message: 'AI analysis unavailable'
            })
        );

        res.json({
            success: true,
            analysis,
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        logMessage('ERROR', 'Parlay analysis failed', { error: error.message });
        res.status(500).json({
            success: false,
            error: 'Analysis temporarily unavailable'
        });
    }
});

// Live odds endpoint
app.get('/api/odds/live', async (req, res) => {
    try {
        const sport = req.query.sport || 'NFL';

        // Use circuit breaker for odds ingestion
        const odds = await circuitBreaker.execute(
            async () => {
                // In production, fetch from Redis cache or odds service
                return [
                    {
                        sportsbook: 'DraftKings',
                        event: 'Chiefs vs Broncos',
                        selection: 'Chiefs ML',
                        odds: -150,
                        timestamp: new Date().toISOString()
                    },
                    {
                        sportsbook: 'FanDuel',
                        event: 'Chiefs vs Broncos',
                        selection: 'Chiefs ML',
                        odds: -145,
                        timestamp: new Date().toISOString()
                    }
                ];
            },
            () => []
        );

        res.json({
            success: true,
            sport,
            odds,
            lastUpdated: new Date().toISOString()
        });

    } catch (error) {
        logMessage('ERROR', 'Odds fetch failed', { error: error.message });
        res.status(500).json({
            success: false,
            error: 'Odds temporarily unavailable'
        });
    }
});

// Graceful 404 handling with suggestions
app.use('*', (req, res) => {
    const suggestions = [
        { path: '/dashboard', description: 'Main betting dashboard' },
        { path: '/health', description: 'System health status' },
        { path: '/status', description: 'Detailed system information' },
        { path: '/api/odds/live', description: 'Live odds API' }
    ];

    res.status(404).json({
        error: 'Endpoint not found',
        path: req.originalUrl,
        suggestions,
        timestamp: new Date().toISOString()
    });
});

// Global error handler
app.use((error, req, res, next) => {
    logMessage('ERROR', 'Unhandled error', {
        error: error.message,
        stack: error.stack,
        path: req.path,
        method: req.method
    });

    res.status(500).json({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong',
        timestamp: new Date().toISOString()
    });
});

// Socket.IO connection handling
io.on('connection', (socket) => {
    logMessage('INFO', 'Client connected', { socketId: socket.id });
    serviceStatus.updateService('socketio', 'healthy');

    socket.on('subscribe_odds', (data) => {
        logMessage('INFO', 'Client subscribed to odds', { sport: data.sport });
        socket.join(`odds_${data.sport}`);

        // Send initial odds
        socket.emit('odds_update', {
            sport: data.sport,
            timestamp: new Date().toISOString(),
            odds: []  // Would fetch real odds in production
        });
    });

    socket.on('analyze_parlay', async (data) => {
        try {
            logMessage('INFO', 'Parlay analysis requested', { legs: data.legs?.length });

            // Simulate analysis with circuit breaker
            const analysis = await circuitBreaker.execute(
                async () => {
                    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate processing
                    return {
                        recommendation: 'BET',
                        confidence: 0.82,
                        expectedValue: 8.7,
                        reasoning: 'Strong value identified in leg combinations'
                    };
                },
                () => ({
                    recommendation: 'PASS',
                    confidence: 0.1,
                    message: 'Analysis service unavailable'
                })
            );

            socket.emit('analysis_result', {
                success: true,
                analysis,
                timestamp: new Date().toISOString()
            });

        } catch (error) {
            socket.emit('analysis_result', {
                success: false,
                error: 'Analysis failed',
                timestamp: new Date().toISOString()
            });
        }
    });

    socket.on('disconnect', () => {
        logMessage('INFO', 'Client disconnected', { socketId: socket.id });
    });
});

// Generate main dashboard HTML
async function generateDashboard() {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 Sports Betting Analytics</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="/socket.io/socket.io.js"></script>
    <style>
        .status-healthy { @apply bg-green-100 text-green-800; }
        .status-degraded { @apply bg-yellow-100 text-yellow-800; }
        .status-failing { @apply bg-red-100 text-red-800; }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <nav class="bg-blue-600 text-white p-4">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold">EQ12 Analytics</h1>
            <div id="connectionStatus" class="status-healthy px-3 py-1 rounded-full text-sm">
                Connected
            </div>
        </div>
    </nav>

    <div class="container mx-auto p-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Parlay Builder -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4">Parlay Builder</h2>
                <div id="parlayLegs" class="space-y-3">
                    <!-- Parlay legs will be added here -->
                </div>
                <button id="addLeg" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                    Add Leg
                </button>
                <button id="analyzeParlayBtn" class="mt-4 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 ml-2">
                    Analyze Parlay
                </button>
            </div>

            <!-- Analysis Results -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4">Analysis Results</h2>
                <div id="analysisResults" class="text-gray-500">
                    Add parlay legs and click analyze to see results
                </div>
            </div>

            <!-- Live Odds -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4">Live Odds</h2>
                <div id="liveOdds" class="space-y-2">
                    Loading odds...
                </div>
            </div>

            <!-- System Status -->
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-semibold mb-4">System Status</h2>
                <div id="systemStatus">
                    <div class="status-healthy px-3 py-1 rounded text-sm">All systems operational</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize Socket.IO
        const socket = io();
        let parlayLegs = [];

        // Connection status handling
        socket.on('connect', () => {
            document.getElementById('connectionStatus').textContent = 'Connected';
            document.getElementById('connectionStatus').className = 'status-healthy px-3 py-1 rounded-full text-sm';
        });

        socket.on('disconnect', () => {
            document.getElementById('connectionStatus').textContent = 'Disconnected';
            document.getElementById('connectionStatus').className = 'status-failing px-3 py-1 rounded-full text-sm';
        });

        // Subscribe to odds updates
        socket.emit('subscribe_odds', { sport: 'NFL' });

        // Handle odds updates
        socket.on('odds_update', (data) => {
            const oddsContainer = document.getElementById('liveOdds');
            if (data.odds && data.odds.length > 0) {
                oddsContainer.innerHTML = data.odds.map(odd =>
                    '<div class="flex justify-between p-2 border rounded">' +
                    '<span>' + odd.selection + '</span>' +
                    '<span class="font-semibold">' + odd.odds + '</span>' +
                    '</div>'
                ).join('');
            } else {
                oddsContainer.innerHTML = '<div class="text-gray-500">No odds available</div>';
            }
        });

        // Handle analysis results
        socket.on('analysis_result', (data) => {
            const resultsContainer = document.getElementById('analysisResults');
            if (data.success) {
                resultsContainer.innerHTML =
                    '<div class="space-y-2">' +
                    '<div><strong>Recommendation:</strong> ' + data.analysis.recommendation + '</div>' +
                    '<div><strong>Confidence:</strong> ' + (data.analysis.confidence * 100).toFixed(1) + '%</div>' +
                    '<div><strong>Expected Value:</strong> $' + (data.analysis.expectedValue || 0).toFixed(2) + '</div>' +
                    '<div class="text-sm text-gray-600">' + (data.analysis.reasoning || data.analysis.message || '') + '</div>' +
                    '</div>';
            } else {
                resultsContainer.innerHTML = '<div class="text-red-600">Analysis failed: ' + data.error + '</div>';
            }
        });

        // Add parlay leg functionality
        document.getElementById('addLeg').addEventListener('click', () => {
            const legId = parlayLegs.length;
            const legHtml =
                '<div class="flex space-x-2 items-center" data-leg="' + legId + '">' +
                '<input type="text" placeholder="Selection (e.g. Chiefs ML)" class="flex-1 border rounded px-2 py-1" data-field="selection">' +
                '<input type="number" placeholder="Odds" class="w-20 border rounded px-2 py-1" data-field="odds">' +
                '<button class="text-red-500 hover:text-red-700" onclick="removeLeg(' + legId + ')">Remove</button>' +
                '</div>';

            document.getElementById('parlayLegs').insertAdjacentHTML('beforeend', legHtml);
            parlayLegs.push({ selection: '', odds: null });
        });

        // Remove parlay leg
        function removeLeg(legId) {
            const legElement = document.querySelector('[data-leg="' + legId + '"]');
            if (legElement) {
                legElement.remove();
                parlayLegs.splice(legId, 1);
            }
        }

        // Analyze parlay
        document.getElementById('analyzeParlayBtn').addEventListener('click', () => {
            const legElements = document.querySelectorAll('#parlayLegs > div');
            const legs = Array.from(legElements).map(el => {
                const selection = el.querySelector('[data-field="selection"]').value;
                const odds = parseInt(el.querySelector('[data-field="odds"]').value);
                return { selection, odds };
            }).filter(leg => leg.selection && leg.odds);

            if (legs.length === 0) {
                alert('Please add at least one parlay leg');
                return;
            }

            document.getElementById('analysisResults').innerHTML = '<div class="text-blue-600">Analyzing...</div>';
            socket.emit('analyze_parlay', { legs });
        });

        // Load system status
        fetch('/health')
            .then(response => response.json())
            .then(data => {
                const statusContainer = document.getElementById('systemStatus');
                const statusClass = data.status === 'healthy' ? 'status-healthy' :
                                  data.status === 'degraded' ? 'status-degraded' : 'status-failing';
                statusContainer.innerHTML =
                    '<div class="' + statusClass + ' px-3 py-1 rounded text-sm mb-2">' +
                    'System: ' + data.status.toUpperCase() + '</div>' +
                    '<div class="text-sm text-gray-600">Uptime: ' + Math.floor(data.uptime / 60) + ' minutes</div>';
            })
            .catch(error => {
                document.getElementById('systemStatus').innerHTML =
                    '<div class="status-failing px-3 py-1 rounded text-sm">Status check failed</div>';
            });
    </script>
</body>
</html>`;
}

// Generate fallback dashboard for when main system fails
function generateFallbackDashboard() {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 - System Maintenance</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .status { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        .retry-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>EQ12 Sports Betting Analytics</h1>
        <div class="status">
            <strong>⚠️ Limited Service Mode</strong><br>
            Some features are temporarily unavailable. Basic functionality is maintained.
        </div>
        <p>We're experiencing some technical difficulties but core services remain operational.</p>
        <button class="retry-btn" onclick="location.reload()">Retry</button>
        <button class="retry-btn" onclick="location.href='/health'" style="margin-left: 10px;">System Status</button>
    </div>
</body>
</html>`;
}

// Generate status page
function generateStatusPage(status) {
    const servicesHtml = Object.entries(status.services)
        .map(([name, service]) =>
            `<tr>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">${name}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                    <span style="color: ${service.status === 'healthy' ? 'green' : service.status === 'degraded' ? 'orange' : 'red'}">
                        ${service.status.toUpperCase()}
                    </span>
                </td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">${service.errors}</td>
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">${service.lastCheck ? new Date(service.lastCheck).toLocaleString() : 'Never'}</td>
            </tr>`
        ).join('');

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EQ12 System Status</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .services { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 12px 8px; text-align: left; border-bottom: 2px solid #dee2e6; }
        .refresh-btn { background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>EQ12 System Status</h1>
            <p><strong>Overall Status:</strong>
                <span style="color: ${status.overall === 'healthy' ? 'green' : status.overall === 'degraded' ? 'orange' : 'red'}">
                    ${status.overall.toUpperCase()}
                </span>
            </p>
            <p><strong>Last Updated:</strong> ${status.timestamp}</p>
            <p><strong>Uptime:</strong> ${Math.floor(status.uptime / 1000 / 60)} minutes</p>
            <button class="refresh-btn" onclick="location.reload()">Refresh Status</button>
        </div>

        <div class="services">
            <h2>Service Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Service</th>
                        <th>Status</th>
                        <th>Errors</th>
                        <th>Last Check</th>
                    </tr>
                </thead>
                <tbody>
                    ${servicesHtml}
                </tbody>
            </table>
        </div>

        <div style="background: white; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2>System Information</h2>
            <p><strong>Node.js Version:</strong> ${status.node_version}</p>
            <p><strong>Memory Usage:</strong> ${Math.round(status.memory.heapUsed / 1024 / 1024)} MB</p>
            <p><strong>Process ID:</strong> ${process.pid}</p>
        </div>
    </div>
</body>
</html>`;
}

// Periodic health checks
setInterval(async () => {
    try {
        // Update service statuses
        serviceStatus.updateService('express', 'healthy');

        // Check Redis connectivity
        if (redisClient && redisClient.isReady) {
            await redisClient.ping();
            serviceStatus.updateService('redis', 'healthy');
        }

        // Emit status to connected clients
        io.emit('system_status', serviceStatus.getStatus());

    } catch (error) {
        logMessage('ERROR', 'Health check failed', { error: error.message });
    }
}, 30000); // Every 30 seconds

// Graceful shutdown
process.on('SIGINT', async () => {
    logMessage('INFO', 'Received SIGINT, shutting down gracefully');

    server.close(() => {
        logMessage('INFO', 'HTTP server closed');
    });

    if (redisClient) {
        await redisClient.quit();
        logMessage('INFO', 'Redis connection closed');
    }

    process.exit(0);
});

process.on('SIGTERM', async () => {
    logMessage('INFO', 'Received SIGTERM, shutting down gracefully');
    process.exit(0);
});

// Start server
async function startServer() {
    const PORT = process.env.PORT || 3000;

    try {
        await initializeRedis();

        server.listen(PORT, () => {
            logMessage('INFO', `EQ12 Enhanced Dashboard Server started on port ${PORT}`);
            serviceStatus.updateService('express', 'healthy');
        });

    } catch (error) {
        logMessage('ERROR', 'Server startup failed', { error: error.message });
        process.exit(1);
    }
}

startServer();
