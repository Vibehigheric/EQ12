// eq12_enterprise_server.js
/**
 * EQ12 Enterprise Node.js Server with Express 5.x
 * Advanced socket.io streaming, helmet security, compression optimization
 */

import compression from 'compression';
import cors from 'cors';
import dotenv from 'dotenv';
import express from 'express';
import rateLimit from 'express-rate-limit';
import slowDown from 'express-slow-down';
import { body, validationResult } from 'express-validator';
import fs from 'fs/promises';
import helmet from 'helmet';
import { createServer } from 'http';
import { createProxyMiddleware } from 'http-proxy-middleware';
import Redis from 'ioredis';
import jwt from 'jsonwebtoken';
import multer from 'multer';
import path from 'path';
import { collectDefaultMetrics, Counter, Gauge, Histogram, register as promRegister } from 'prom-client';
import sharp from 'sharp';
import { Server } from 'socket.io';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';
import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';

// Load environment variables
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Prometheus metrics
collectDefaultMetrics();
const httpRequestDuration = new Histogram({
    name: 'http_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route', 'status_code']
});

const httpRequestTotal = new Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'route', 'status_code']
});

const activeConnections = new Gauge({
    name: 'websocket_active_connections',
    help: 'Number of active WebSocket connections'
});

const redisOperations = new Counter({
    name: 'redis_operations_total',
    help: 'Total Redis operations',
    labelNames: ['operation', 'status']
});

// Advanced logging setup
const logger = winston.createLogger({
    level: process.env.LOG_LEVEL || 'info',
    format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.errors({ stack: true }),
        winston.format.json()
    ),
    defaultMeta: { service: 'eq12-enterprise-server' },
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize(),
                winston.format.simple()
            )
        }),
        new DailyRotateFile({
            filename: 'C:/EQ12/logs/application-%DATE%.log',
            datePattern: 'YYYY-MM-DD',
            zippedArchive: true,
            maxSize: '20m',
            maxFiles: '14d'
        }),
        new DailyRotateFile({
            filename: 'C:/EQ12/logs/error-%DATE%.log',
            datePattern: 'YYYY-MM-DD',
            level: 'error',
            zippedArchive: true,
            maxSize: '20m',
            maxFiles: '30d'
        })
    ]
});

// Redis client with advanced configuration
const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    retryDelayOnFailover: 100,
    enableReadyCheck: false,
    maxRetriesPerRequest: 3,
    lazyConnect: true,
    keepAlive: 30000,
    family: 4,
    keyPrefix: 'eq12:',
    db: 0
});

// Redis event handlers
redis.on('connect', () => {
    logger.info('Redis client connected');
    redisOperations.inc({ operation: 'connect', status: 'success' });
});

redis.on('error', (err) => {
    logger.error('Redis error:', err);
    redisOperations.inc({ operation: 'connect', status: 'error' });
});

// Express app initialization
const app = express();
const server = createServer(app);

// Advanced Socket.IO configuration
const io = new Server(server, {
    cors: {
        origin: process.env.CORS_ORIGIN || "*",
        methods: ["GET", "POST"],
        credentials: true
    },
    transports: ['websocket', 'polling'],
    pingTimeout: 60000,
    pingInterval: 25000,
    upgradeTimeout: 10000,
    maxHttpBufferSize: 1e6,
    allowEIO3: true,
    compression: true,
    perMessageDeflate: {
        threshold: 1024,
        concurrencyLimit: 10,
        memLevel: 7
    }
});

// Security middleware with Helmet
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https:"],
            scriptSrc: ["'self'", "https:"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "https:", "wss:", "ws:"],
            fontSrc: ["'self'", "https:", "data:"],
            objectSrc: ["'none'"],
            mediaSrc: ["'self'", "https:"],
            frameSrc: ["'none'"]
        }
    },
    crossOriginEmbedderPolicy: false,
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    },
    noSniff: true,
    xssFilter: true,
    referrerPolicy: { policy: "same-origin" }
}));

// Advanced rate limiting
const globalRateLimit = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: process.env.RATE_LIMIT_MAX || 1000,
    message: {
        error: 'Too many requests from this IP',
        retryAfter: '15 minutes'
    },
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req) => {
        return req.ip || req.connection.remoteAddress;
    },
    skip: (req) => {
        // Skip rate limiting for health checks
        return req.path === '/healthz' || req.path === '/metrics';
    }
});

// API-specific rate limiting
const apiRateLimit = rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: process.env.API_RATE_LIMIT_MAX || 100,
    message: {
        error: 'API rate limit exceeded',
        retryAfter: '1 minute'
    }
});

// Slow down middleware for additional protection
const speedLimiter = slowDown({
    windowMs: 15 * 60 * 1000, // 15 minutes
    delayAfter: 100, // allow 100 requests per 15 minutes at full speed
    delayMs: 500, // slow down subsequent requests by 500ms per request
    maxDelayMs: 20000 // maximum delay of 20 seconds
});

// Apply middleware
app.use(compression({
    level: 6,
    threshold: 1000,
    filter: (req, res) => {
        if (req.headers['x-no-compression']) {
            return false;
        }
        return compression.filter(req, res);
    }
}));

app.use(cors({
    origin: process.env.CORS_ORIGIN || true,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));

app.use(express.json({
    limit: process.env.JSON_LIMIT || '10mb',
    strict: true
}));
app.use(express.urlencoded({
    extended: true,
    limit: process.env.URL_ENCODED_LIMIT || '10mb'
}));

// Request logging middleware
app.use((req, res, next) => {
    const start = Date.now();
    const requestId = uuidv4();

    req.requestId = requestId;
    req.startTime = start;

    logger.info('HTTP Request', {
        requestId,
        method: req.method,
        url: req.url,
        ip: req.ip,
        userAgent: req.get('User-Agent')
    });

    res.on('finish', () => {
        const duration = (Date.now() - start) / 1000;

        httpRequestDuration
            .labels(req.method, req.route?.path || req.path, res.statusCode)
            .observe(duration);

        httpRequestTotal
            .labels(req.method, req.route?.path || req.path, res.statusCode)
            .inc();

        logger.info('HTTP Response', {
            requestId,
            method: req.method,
            url: req.url,
            statusCode: res.statusCode,
            duration: `${duration}s`
        });
    });

    next();
});

// Apply rate limiting
app.use(globalRateLimit);
app.use(speedLimiter);

// Swagger documentation
const swaggerOptions = {
    definition: {
        openapi: '3.0.0',
        info: {
            title: 'EQ12 Enterprise API',
            version: '2.1.0',
            description: 'Advanced sports betting and content monetization API'
        },
        servers: [
            {
                url: `http://localhost:${process.env.PORT || 3000}`,
                description: 'Development server'
            }
        ]
    },
    apis: ['./eq12_enterprise_server.js', './routes/*.js']
};

const specs = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs));

// File upload configuration
const storage = multer.memoryStorage();
const upload = multer({
    storage,
    limits: {
        fileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB
        files: 5
    },
    fileFilter: (req, file, cb) => {
        const allowedTypes = /jpeg|jpg|png|gif|pdf|doc|docx/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);

        if (mimetype && extname) {
            return cb(null, true);
        }
        cb(new Error('Invalid file type'));
    }
});

// Authentication middleware
const authenticateToken = async (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET || 'fallback-secret');
        req.user = decoded;
        next();
    } catch (error) {
        logger.warn('Invalid token attempt', { error: error.message, ip: req.ip });
        return res.status(403).json({ error: 'Invalid or expired token' });
    }
};

// Cache middleware
const cacheMiddleware = (duration = 300) => {
    return async (req, res, next) => {
        if (req.method !== 'GET') {
            return next();
        }

        const key = `cache:${req.originalUrl}`;

        try {
            const cached = await redis.get(key);
            if (cached) {
                logger.debug('Cache hit', { key, requestId: req.requestId });
                redisOperations.inc({ operation: 'get', status: 'hit' });
                return res.json(JSON.parse(cached));
            }

            redisOperations.inc({ operation: 'get', status: 'miss' });

            // Store original res.json
            const originalJson = res.json;

            res.json = function (data) {
                // Cache the response
                redis.setex(key, duration, JSON.stringify(data)).catch(err => {
                    logger.error('Cache storage error', { error: err.message, key });
                });

                // Send response
                return originalJson.call(this, data);
            };

            next();
        } catch (error) {
            logger.error('Cache middleware error', { error: error.message });
            redisOperations.inc({ operation: 'get', status: 'error' });
            next();
        }
    };
};

// Health check endpoint
/**
 * @swagger
 * /healthz:
 *   get:
 *     summary: Health check endpoint
 *     tags: [Health]
 *     responses:
 *       200:
 *         description: Service is healthy
 */
app.get('/healthz', async (req, res) => {
    const health = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '2.1.0',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        services: {}
    };

    // Check Redis connection
    try {
        await redis.ping();
        health.services.redis = 'connected';
    } catch (error) {
        health.services.redis = 'disconnected';
        health.status = 'degraded';
    }

    // Check disk space
    try {
        const stats = await fs.stat('C:/EQ12/logs');
        health.services.filesystem = 'accessible';
    } catch (error) {
        health.services.filesystem = 'error';
        health.status = 'degraded';
    }

    const statusCode = health.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(health);
});

// Metrics endpoint for Prometheus
app.get('/metrics', async (req, res) => {
    try {
        res.set('Content-Type', promRegister.contentType);
        res.end(await promRegister.metrics());
    } catch (error) {
        res.status(500).end(error.message);
    }
});

// Root redirect endpoint
app.get('/', (req, res) => {
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
    res.redirect(302, '/dashboard');
});

// API Routes

/**
 * @swagger
 * /api/auth/login:
 *   post:
 *     summary: User login
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               username:
 *                 type: string
 *               password:
 *                 type: string
 *     responses:
 *       200:
 *         description: Login successful
 */
app.post('/api/auth/login',
    apiRateLimit,
    [
        body('username').isLength({ min: 3 }).trim().escape(),
        body('password').isLength({ min: 6 })
    ],
    async (req, res) => {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({ errors: errors.array() });
            }

            const { username, password } = req.body;

            // In production, check against database
            const user = { id: 1, username, role: 'user' };
            const token = jwt.sign(user, process.env.JWT_SECRET || 'fallback-secret', { expiresIn: '24h' });

            // Store session in Redis
            await redis.setex(`session:${user.id}`, 86400, JSON.stringify(user));

            logger.info('User login', { username, requestId: req.requestId });

            res.json({
                success: true,
                token,
                user: { id: user.id, username: user.username, role: user.role }
            });

        } catch (error) {
            logger.error('Login error', { error: error.message, requestId: req.requestId });
            res.status(500).json({ error: 'Login failed' });
        }
    }
);

/**
 * @swagger
 * /api/sports/odds:
 *   get:
 *     summary: Get current sports odds
 *     tags: [Sports]
 *     responses:
 *       200:
 *         description: Current odds data
 */
app.get('/api/sports/odds', cacheMiddleware(60), async (req, res) => {
    try {
        // Simulate odds data
        const odds = {
            timestamp: new Date().toISOString(),
            games: [
                {
                    id: '1',
                    teams: ['Lakers', 'Warriors'],
                    odds: { home: 1.85, away: 1.95 },
                    spread: { home: -2.5, away: 2.5 }
                },
                {
                    id: '2',
                    teams: ['Celtics', 'Heat'],
                    odds: { home: 2.10, away: 1.75 },
                    spread: { home: 1.5, away: -1.5 }
                }
            ]
        };

        logger.info('Odds requested', { requestId: req.requestId });
        res.json(odds);

    } catch (error) {
        logger.error('Odds fetch error', { error: error.message, requestId: req.requestId });
        res.status(500).json({ error: 'Failed to fetch odds' });
    }
});

/**
 * @swagger
 * /api/analysis/parlay:
 *   post:
 *     summary: Analyze parlay combinations
 *     tags: [Analysis]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               games:
 *                 type: array
 *                 items:
 *                   type: object
 *     responses:
 *       200:
 *         description: Parlay analysis results
 */
app.post('/api/analysis/parlay',
    authenticateToken,
    apiRateLimit,
    [body('games').isArray().isLength({ min: 2, max: 10 })],
    async (req, res) => {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({ errors: errors.array() });
            }

            const { games } = req.body;

            // Simulate parlay analysis
            const analysis = {
                id: uuidv4(),
                timestamp: new Date().toISOString(),
                games: games.length,
                recommendedParlays: [
                    {
                        games: games.slice(0, 3),
                        odds: 5.25,
                        confidence: 0.78,
                        expectedValue: 0.12
                    }
                ],
                riskAssessment: {
                    level: 'moderate',
                    factors: ['injury_report', 'weather', 'public_betting']
                }
            };

            logger.info('Parlay analysis', {
                userId: req.user.id,
                games: games.length,
                requestId: req.requestId
            });

            res.json(analysis);

        } catch (error) {
            logger.error('Parlay analysis error', {
                error: error.message,
                requestId: req.requestId
            });
            res.status(500).json({ error: 'Analysis failed' });
        }
    }
);

// File upload endpoint
app.post('/api/upload',
    authenticateToken,
    upload.array('files', 5),
    async (req, res) => {
        try {
            const processedFiles = [];

            for (const file of req.files) {
                if (file.mimetype.startsWith('image/')) {
                    // Process image with Sharp
                    const processed = await sharp(file.buffer)
                        .resize(800, 600, { fit: 'inside', withoutEnlargement: true })
                        .jpeg({ quality: 85 })
                        .toBuffer();

                    const filename = `${uuidv4()}.jpg`;
                    await fs.writeFile(`C:/EQ12/data/uploads/${filename}`, processed);

                    processedFiles.push({
                        originalName: file.originalname,
                        filename,
                        size: processed.length,
                        type: 'image'
                    });
                } else {
                    // Store other files as-is
                    const filename = `${uuidv4()}_${file.originalname}`;
                    await fs.writeFile(`C:/EQ12/data/uploads/${filename}`, file.buffer);

                    processedFiles.push({
                        originalName: file.originalname,
                        filename,
                        size: file.size,
                        type: 'document'
                    });
                }
            }

            logger.info('Files uploaded', {
                userId: req.user.id,
                files: processedFiles.length,
                requestId: req.requestId
            });

            res.json({
                success: true,
                files: processedFiles
            });

        } catch (error) {
            logger.error('Upload error', { error: error.message, requestId: req.requestId });
            res.status(500).json({ error: 'Upload failed' });
        }
    }
);

// Proxy for external APIs
app.use('/api/proxy', createProxyMiddleware({
    target: 'https://api.example.com',
    changeOrigin: true,
    pathRewrite: {
        '^/api/proxy': ''
    },
    onProxyReq: (proxyReq, req, res) => {
        logger.debug('Proxy request', {
            target: proxyReq.path,
            requestId: req.requestId
        });
    },
    onError: (err, req, res) => {
        logger.error('Proxy error', {
            error: err.message,
            requestId: req.requestId
        });
        res.status(502).json({ error: 'Proxy error' });
    }
}));

// WebSocket handling
io.on('connection', (socket) => {
    activeConnections.inc();

    logger.info('WebSocket connected', {
        socketId: socket.id,
        ip: socket.handshake.address
    });

    // Join rooms based on interests
    socket.on('join-room', (room) => {
        if (['odds', 'analysis', 'notifications'].includes(room)) {
            socket.join(room);
            logger.debug('Socket joined room', { socketId: socket.id, room });
        }
    });

    // Handle real-time odds subscription
    socket.on('subscribe-odds', (sports) => {
        logger.debug('Odds subscription', { socketId: socket.id, sports });

        // Simulate real-time odds updates
        const interval = setInterval(() => {
            socket.emit('odds-update', {
                timestamp: new Date().toISOString(),
                sport: sports[0] || 'basketball',
                odds: {
                    home: (1.5 + Math.random()).toFixed(2),
                    away: (1.5 + Math.random()).toFixed(2)
                }
            });
        }, 5000);

        socket.on('disconnect', () => {
            clearInterval(interval);
        });
    });

    // Handle analysis requests
    socket.on('request-analysis', async (data) => {
        try {
            logger.info('Real-time analysis request', {
                socketId: socket.id,
                type: data.type
            });

            // Simulate analysis processing
            socket.emit('analysis-progress', { progress: 25 });
            await new Promise(resolve => setTimeout(resolve, 500));

            socket.emit('analysis-progress', { progress: 50 });
            await new Promise(resolve => setTimeout(resolve, 500));

            socket.emit('analysis-progress', { progress: 75 });
            await new Promise(resolve => setTimeout(resolve, 500));

            socket.emit('analysis-complete', {
                id: uuidv4(),
                result: {
                    confidence: 0.85,
                    recommendation: 'STRONG_BUY',
                    factors: ['momentum', 'value', 'trend']
                }
            });

        } catch (error) {
            logger.error('Real-time analysis error', {
                error: error.message,
                socketId: socket.id
            });

            socket.emit('analysis-error', {
                error: 'Analysis failed'
            });
        }
    });

    socket.on('disconnect', () => {
        activeConnections.dec();
        logger.info('WebSocket disconnected', { socketId: socket.id });
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    logger.error('Unhandled error', {
        error: err.message,
        stack: err.stack,
        requestId: req.requestId,
        url: req.url,
        method: req.method
    });

    if (err.type === 'entity.parse.failed') {
        return res.status(400).json({ error: 'Invalid JSON' });
    }

    if (err.code === 'LIMIT_FILE_SIZE') {
        return res.status(413).json({ error: 'File too large' });
    }

    res.status(500).json({
        error: 'Internal server error',
        requestId: req.requestId
    });
});

// 404 handler
app.use((req, res) => {
    logger.warn('404 Not Found', {
        url: req.url,
        method: req.method,
        ip: req.ip,
        requestId: req.requestId
    });

    res.status(404).json({
        error: 'Endpoint not found',
        requestId: req.requestId
    });
});

// Graceful shutdown
const gracefulShutdown = (signal) => {
    logger.info(`Received ${signal}, shutting down gracefully`);

    server.close(() => {
        logger.info('HTTP server closed');

        redis.disconnect();
        logger.info('Redis connection closed');

        process.exit(0);
    });

    // Force close after 10 seconds
    setTimeout(() => {
        logger.error('Could not close connections in time, forcefully shutting down');
        process.exit(1);
    }, 10000);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start server
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

server.listen(PORT, HOST, () => {
    logger.info(`🚀 EQ12 Enterprise Server running on ${HOST}:${PORT}`);
    logger.info(`📚 API Documentation: http://${HOST}:${PORT}/api-docs`);
    logger.info(`📊 Metrics: http://${HOST}:${PORT}/metrics`);
    logger.info(`🏥 Health Check: http://${HOST}:${PORT}/healthz`);
});

export default app;
