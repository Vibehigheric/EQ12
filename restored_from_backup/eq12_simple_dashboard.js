// Simple EQ12 Dashboard Server - No complex routing
const express = require("express");
const path = require("path");
const fs = require("fs");
const app = express();

// Find the dashboard directory
const dashboardPath = path.join(__dirname, "dashboard");
let staticDir = dashboardPath;

if (fs.existsSync(path.join(dashboardPath, "dist"))) {
    staticDir = path.join(dashboardPath, "dist");
    console.log("[EQ12] Using dashboard/dist");
} else if (fs.existsSync(path.join(dashboardPath, "build"))) {
    staticDir = path.join(dashboardPath, "build");
    console.log("[EQ12] Using dashboard/build");
} else {
    console.log("[EQ12] Using dashboard root");
}

// Serve static files
app.use(express.static(staticDir));

// Health endpoints
app.get("/health", (req, res) => {
    res.status(200).json({
        status: "OK",
        service: "EQ12 Dashboard",
        timestamp: new Date().toISOString(),
        path: req.path
    });
});

app.get("/api/health", (req, res) => {
    res.status(200).json({
        status: "healthy",
        service: "EQ12 Dashboard API",
        timestamp: new Date().toISOString()
    });
});

// Root redirect
app.get("/", (req, res) => {
    res.redirect("/dashboard");
});

// Dashboard route
app.get("/dashboard", (req, res) => {
    const indexPath = path.join(staticDir, "index.html");
    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(404).send(`
            <h1>EQ12 Dashboard Not Built</h1>
            <p>Please build the dashboard first:</p>
            <pre>cd dashboard && npm run build</pre>
            <p>Looking for: ${indexPath}</p>
        `);
    }
});

// Simple catch-all without complex patterns
app.use((req, res) => {
    console.log(`[EQ12] Fallback route: ${req.path}`);
    const indexPath = path.join(staticDir, "index.html");

    if (fs.existsSync(indexPath)) {
        res.sendFile(indexPath);
    } else {
        res.status(404).send("Dashboard not found");
    }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`[EQ12] Dashboard server running on port ${port}`);
    console.log(`[EQ12] Dashboard: http://localhost:${port}/dashboard`);
    console.log(`[EQ12] Health: http://localhost:${port}/health`);
    console.log(`[EQ12] Static files: ${staticDir}`);
});
