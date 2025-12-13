// EQ12 Dashboard Server - Production-safe SPA server
const express = require("express");
const path = require("path");
const app = express();

// Static file serving - adjust path based on your build folder
const dashboardPath = path.join(__dirname, "dashboard");
let staticDir;

// Auto-detect build directory
if (require("fs").existsSync(path.join(dashboardPath, "dist"))) {
    staticDir = path.join(dashboardPath, "dist");
    console.log("[EQ12] Using dashboard/dist as static directory");
} else if (require("fs").existsSync(path.join(dashboardPath, "build"))) {
    staticDir = path.join(dashboardPath, "build");
    console.log("[EQ12] Using dashboard/build as static directory");
} else {
    // Fallback to dashboard root
    staticDir = dashboardPath;
    console.log("[EQ12] Using dashboard root as static directory");
}

// Serve static files
app.use(express.static(staticDir));

// Health endpoint for monitoring
app.get("/health", (_, res) => {
    res.status(200).json({
        status: "OK",
        service: "EQ12 Dashboard",
        timestamp: new Date().toISOString()
    });
});

// API health endpoint (legacy compatibility)
app.get("/api/health", (_, res) => {
    res.status(200).json({
        status: "healthy",
        service: "EQ12 Dashboard API",
        timestamp: new Date().toISOString()
    });
});

// 1) Handle HEAD requests to root (some clients probe with HEAD)
app.head("/", (_, res) => res.status(200).end());

// 2) Redirect root to /dashboard with clean 302
app.get("/", (_, res) => {
    res.redirect(302, "/dashboard");
});

// 3) Dashboard route - serve the main app
app.get("/dashboard", (_, res) => {
    res.sendFile(path.join(staticDir, "index.html"));
});

// 4) SPA fallback - handle all other routes
app.use((req, res, next) => {
    // Skip if already handled or is a file request
    if (res.headersSent || req.path.includes('.')) {
        return next();
    }

    console.log(`[EQ12] SPA fallback for route: ${req.path}`);

    // Check if index.html exists
    const indexPath = path.join(staticDir, "index.html");
    if (require("fs").existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(404).json({
            error: "Dashboard not found",
            message: "Please build the frontend first",
            path: req.path
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error("[EQ12] Server error:", err);
    res.status(500).json({
        error: "Internal Server Error",
        message: "EQ12 Dashboard encountered an error"
    });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`[EQ12] Dashboard server listening on port ${port}`);
    console.log(`[EQ12] Access dashboard at: http://localhost:${port}/dashboard`);
    console.log(`[EQ12] Health check at: http://localhost:${port}/health`);
    console.log(`[EQ12] Static files from: ${staticDir}`);
});
