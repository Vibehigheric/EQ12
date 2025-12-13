const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const helmet = require('helmet');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.NODE_PORT || 3000;

// Security and middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
    const healthData = {
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: Math.floor(process.uptime()),
        memory: process.memoryUsage(),
        version: process.version,
        platform: process.platform,
        pid: process.pid,
        environment: process.env.NODE_ENV || 'development'
    };

    res.json({
        status: 'success',
        data: healthData
    });
});

// API status endpoint
app.get('/api/status', (req, res) => {
    // Check if EQ12 logs directory exists and count files
    const logsDir = path.join(__dirname, '..', 'logs');
    let logStats = { exists: false, files: 0 };

    try {
        if (fs.existsSync(logsDir)) {
            const files = fs.readdirSync(logsDir);
            logStats = {
                exists: true,
                files: files.length,
                recent_files: files.filter(f => {
                    const stats = fs.statSync(path.join(logsDir, f));
                    const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
                    return stats.mtime > dayAgo;
                }).length
            };
        }
    } catch (error) {
        console.error('Error reading logs:', error);
    }

    res.json({
        status: 'success',
        data: {
            service: 'EQ12 Node.js API',
            version: '1.0.0',
            timestamp: new Date().toISOString(),
            logs: logStats,
            cache_status: 'active',
            queue_status: 'processing'
        }
    });
});

// Metrics endpoint
app.get('/api/metrics', (req, res) => {
    const metrics = {
        timestamp: new Date().toISOString(),
        process: {
            uptime: Math.floor(process.uptime()),
            memory: process.memoryUsage(),
            cpu_usage: process.cpuUsage(),
            pid: process.pid
        },
        system: {
            platform: process.platform,
            node_version: process.version,
            arch: process.arch
        },
        performance: {
            event_loop_lag: '< 1ms',
            active_handles: process._getActiveHandles().length,
            active_requests: process._getActiveRequests().length
        }
    };

    res.json({
        status: 'success',
        data: metrics
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('API Error:', error);
    res.status(500).json({
        status: 'error',
        data: {
            error: 'Internal server error',
            timestamp: new Date().toISOString()
        }
    });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        status: 'error',
        data: {
            error: 'Endpoint not found',
            path: req.originalUrl,
            timestamp: new Date().toISOString()
        }
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 EQ12 Node.js API server running on port ${PORT}`);
    console.log(`📊 Health check: http://localhost:${PORT}/health`);
    console.log(`📈 Metrics: http://localhost:${PORT}/api/metrics`);
    console.log(`⏰ Started at: ${new Date().toISOString()}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 Received SIGTERM, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('🛑 Received SIGINT, shutting down gracefully');
    process.exit(0);
});

module.exports = app;
