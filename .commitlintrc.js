module.exports = {
    extends: ["@commitlint/config-conventional"],
    rules: {
        "type-enum": [
            2,
            "always",
            [
                // Standard conventional commit types
                "feat",      // new feature
                "fix",       // bug fix
                "chore",     // tooling/infra updates
                "docs",      // documentation changes
                "refactor",  // code refactoring
                "style",     // formatting only
                "test",      // adding or fixing tests
                "perf",      // performance improvements
                "ci",        // CI/CD changes
                "build",     // build system changes
                "revert",    // reverting previous commits

                // Custom EQ12 commit types
                "bet",       // betting logic and algorithms
                "agent",     // multi-agent orchestration
                "ext",       // browser extension (Firefox/Chromium)
                "infra",     // VPN, infrastructure, pipelines
                "audit",     // compliance & logging changes
                "parlay",    // parlay generation specific
                "ev",        // expected value calculations
                "risk",      // risk management and bankroll
                "telegram",  // Telegram bot functionality
                "vpn"        // VPN guard and networking
            ]
        ],
        "scope-enum": [
            2,
            "always",
            [
                // Browser extension components
                "extension",  // General extension code
                "popup",      // Extension popup interface
                "options",    // Extension settings page
                "content",    // Content scripts for sportsbooks
                "background", // Service worker/background scripts

                // Backend API components
                "api",        // EQ12 FastAPI backend
                "endpoints",  // Specific API endpoints
                "auth",       // Authentication and security
                "cors",       // CORS configuration
                "middleware", // API middleware

                // EQ12 agents and modules
                "telegram",   // Telegram bot logic
                "audit",      // Compliance and audit agent
                "vpn",        // VPN guard and scripts
                "pipeline",   // Betting pipeline orchestration
                "parlay",     // Parlay builder agent
                "ev",         // EV/probability calculations
                "props",      // Player props agent
                "risk",       // Bankroll/risk management
                "odds",       // Odds parsing and normalization

                // Infrastructure and tooling
                "ci",         // GitHub Actions workflows
                "build",      // Build scripts and tools
                "docker",     // Docker configuration
                "nginx",      // Nginx/reverse proxy
                "database",   // SQLite/database operations

                // Documentation and configuration
                "docs",       // Documentation files
                "config",     // Configuration files
                "manifest",   // Extension manifests
                "deps",       // Dependency management
                "scripts",    // Utility scripts

                // Testing and quality
                "tests",      // Test files and configuration
                "lint",       // Linting configuration
                "format",     // Code formatting

                // Specific sportsbooks (for content script work)
                "draftkings", // DraftKings integration
                "fanduel",    // FanDuel integration
                "betmgm",     // BetMGM integration
                "caesars",    // Caesars integration
                "barstool"    // Barstool integration
            ]
        ],
        "subject-case": [2, "always", ["sentence-case"]],
        "subject-min-length": [2, "always", 10],
        "subject-max-length": [2, "always", 72],
        "body-leading-blank": [2, "always"],
        "footer-leading-blank": [2, "always"]
    }
};
