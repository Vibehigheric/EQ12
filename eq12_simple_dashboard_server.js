// Simple EQ12 Dashboard Server - Express 5 Compatible
const express = require("express");
const path = require("path");

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 1) Health endpoint
app.get("/health", (req, res) => {
    res.status(200).json({
        status: "OK",
        service: "EQ12 Dashboard",
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        version: "2.0.0"
    });
});

// 2) API health (legacy)
app.get("/api/health", (req, res) => {
    res.status(200).json({
        status: "healthy",
        service: "EQ12 API",
        timestamp: new Date().toISOString()
    });
});

// 3) HEAD request support for root
app.head("/", (req, res) => {
    res.status(200).end();
});

// 4) Root redirect to dashboard
app.get("/", (req, res) => {
    console.log("[EQ12] Root access - redirecting to /dashboard");
    res.redirect(302, "/dashboard");
});

// Serve static files from dashboard directory (AFTER specific routes)
const dashboardPath = path.join(__dirname, "dashboard");
app.use(express.static(dashboardPath));

console.log(`[EQ12] Static files from: ${dashboardPath}`);

// 5) Dashboard endpoint
app.get("/dashboard", (req, res) => {
    const indexPath = path.join(dashboardPath, "index.html");

    // Check if index.html exists
    if (require("fs").existsSync(indexPath)) {
        console.log("[EQ12] Serving dashboard from", indexPath);
        res.sendFile(indexPath);
    } else {
        console.log("[EQ12] Dashboard index.html not found, serving placeholder");
        res.status(200).send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>EQ12 Dashboard</title>
            <style>
                body { font-family: Arial; margin: 40px; background: #1a1a1a; color: #fff; }
                .container { max-width: 800px; margin: 0 auto; text-align: center; }
                .status { background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .success { border-left: 4px solid #4caf50; }
                .info { border-left: 4px solid #2196f3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 EQ12 Dashboard</h1>
                <div class="status success">
                    <h3>✅ Server Status: Online</h3>
                    <p>Dashboard server is running successfully</p>
                </div>
                <div class="status info">
                    <h3>📊 System Information</h3>
                    <p><strong>Service:</strong> EQ12 Dashboard v2.0.0</p>
                    <p><strong>Timestamp:</strong> ${new Date().toISOString()}</p>
                    <p><strong>Uptime:</strong> ${Math.floor(process.uptime())} seconds</p>
                </div>
                <div class="status info">
                    <h3>🔗 API Endpoints</h3>
                    <p><a href="/health" style="color: #4caf50;">/health</a> - Health Check</p>
                    <p><a href="/api/health" style="color: #4caf50;">/api/health</a> - API Health</p>
                </div>
            </div>
        </body>
        </html>
        `);
    }
});

// 6) Error handling middleware
app.use((err, req, res, next) => {
    console.error("[EQ12] Server error:", err.message);
    res.status(500).json({
        error: "Internal Server Error",
        message: "EQ12 Dashboard encountered an error",
        timestamp: new Date().toISOString()
    });
});

// 7) 404 handler
app.use((req, res) => {
    console.log(`[EQ12] 404 for: ${req.method} ${req.path}`);
    res.status(404).json({
        error: "Not Found",
        path: req.path,
        message: "The requested resource was not found",
        timestamp: new Date().toISOString()
    });
});

const port = process.env.PORT || 3000;

app.listen(port, "127.0.0.1", () => {
    console.log(`[EQ12] Dashboard server listening on port ${port}`);
    console.log(`[EQ12] Health check: http://localhost:${port}/health`);
    console.log(`[EQ12] Dashboard: http://localhost:${port}/dashboard`);
    console.log(`[EQ12] Root redirect: http://localhost:${port}/`);
});
