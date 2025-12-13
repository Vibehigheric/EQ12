#!/usr/bin/env python3
"""
EQ12 Revenue Analytics Dashboard - Real-time monetization tracking
Comprehensive analytics for all revenue streams with AI insights
"""

import asyncio
import json
import logging
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import HTMLResponse

from eq12_openai_security import EQ12OpenAISecurityManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RevenueMetrics:
    """Revenue tracking metrics"""

    github_actions: float = 0.0
    chrome_extension: float = 0.0
    slack_bots: float = 0.0
    marketplace_actions: float = 0.0
    license_server: float = 0.0
    saas_subscriptions: float = 0.0
    enterprise_deals: float = 0.0
    openai_cost_savings: float = 0.0

    @property
    def total_revenue(self) -> float:
        return (
            self.github_actions
            + self.chrome_extension
            + self.slack_bots
            + self.marketplace_actions
            + self.license_server
            + self.saas_subscriptions
            + self.enterprise_deals
        )

    @property
    def net_revenue(self) -> float:
        return self.total_revenue - self.openai_cost_savings


@dataclass
class UserMetrics:
    """User engagement and conversion metrics"""

    total_users: int = 0
    free_users: int = 0
    pro_users: int = 0
    enterprise_users: int = 0
    monthly_active_users: int = 0
    conversion_rate: float = 0.0
    churn_rate: float = 0.0

    @property
    def paying_users(self) -> int:
        return self.pro_users + self.enterprise_users


class EQ12RevenueAnalytics:
    """Comprehensive revenue analytics and tracking system"""

    def __init__(self):
        self.app = FastAPI(title="EQ12 Revenue Analytics", version="2.0.0")
        self.db_path = "C:/EQ12/logs/revenue_analytics.db"

        # OpenAI integration for AI insights
        self.openai_manager = EQ12OpenAISecurityManager("analytics")

        # Revenue tracking
        self.current_metrics = RevenueMetrics()
        self.user_metrics = UserMetrics()

        # Goals and targets
        self.monthly_target = 10000.0  # $10k/month target
        self.annual_target = 120000.0  # $120k/year target

        self.setup_database()
        self.setup_routes()

    def setup_database(self):
        """Initialize SQLite database for revenue tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Revenue events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS revenue_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                event_type TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                user_id TEXT,
                subscription_plan TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # User events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                plan TEXT,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Daily metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_metrics (
                date TEXT PRIMARY KEY,
                revenue_data TEXT NOT NULL,
                user_data TEXT NOT NULL,
                ai_insights TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")

    def setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self.get_dashboard_html()

        @self.app.get("/api/metrics")
        async def get_current_metrics():
            return {
                "revenue": asdict(self.current_metrics),
                "users": asdict(self.user_metrics),
                "targets": {"monthly": self.monthly_target, "annual": self.annual_target},
                "progress": {
                    "monthly_progress": (self.current_metrics.total_revenue / self.monthly_target)
                    * 100,
                    "annual_progress": (
                        self.current_metrics.total_revenue * 12 / self.annual_target
                    )
                    * 100,
                },
            }

        @self.app.post("/api/revenue/track")
        async def track_revenue(event: dict, background_tasks: BackgroundTasks):
            background_tasks.add_task(self.record_revenue_event, event)
            return {"status": "recorded"}

        @self.app.post("/api/users/track")
        async def track_user_event(event: dict, background_tasks: BackgroundTasks):
            background_tasks.add_task(self.record_user_event, event)
            return {"status": "recorded"}

        @self.app.get("/api/analytics/ai-insights")
        async def get_ai_insights():
            return await self.generate_ai_insights()

        @self.app.get("/api/analytics/forecasting")
        async def get_revenue_forecast():
            return await self.generate_revenue_forecast()

        @self.app.get("/api/analytics/optimization")
        async def get_optimization_suggestions():
            return await self.generate_optimization_suggestions()

    async def record_revenue_event(self, event: dict):
        """Record a revenue event in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO revenue_events
                (timestamp, source, event_type, amount, user_id, subscription_plan, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    event.get("timestamp", datetime.now().isoformat()),
                    event["source"],
                    event["event_type"],
                    event["amount"],
                    event.get("user_id"),
                    event.get("subscription_plan"),
                    json.dumps(event.get("metadata", {})),
                ),
            )

            conn.commit()
            conn.close()

            # Update current metrics
            await self.update_current_metrics()

            logger.info(f"Revenue event recorded: {event['source']} - ${event['amount']}")

        except Exception as e:
            logger.error(f"Failed to record revenue event: {e}")

    async def record_user_event(self, event: dict):
        """Record a user event in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO user_events
                (timestamp, user_id, event_type, source, plan, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    event.get("timestamp", datetime.now().isoformat()),
                    event["user_id"],
                    event["event_type"],
                    event["source"],
                    event.get("plan"),
                    json.dumps(event.get("metadata", {})),
                ),
            )

            conn.commit()
            conn.close()

            # Update user metrics
            await self.update_user_metrics()

            logger.info(f"User event recorded: {event['user_id']} - {event['event_type']}")

        except Exception as e:
            logger.error(f"Failed to record user event: {e}")

    async def update_current_metrics(self):
        """Update current revenue metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get revenue by source for current month
            current_month = datetime.now().replace(day=1).isoformat()

            cursor.execute(
                """
                SELECT source, SUM(amount)
                FROM revenue_events
                WHERE timestamp >= ?
                GROUP BY source
            """,
                (current_month,),
            )

            revenue_by_source = dict(cursor.fetchall())

            # Update metrics
            self.current_metrics.github_actions = revenue_by_source.get("github_actions", 0.0)
            self.current_metrics.chrome_extension = revenue_by_source.get("chrome_extension", 0.0)
            self.current_metrics.slack_bots = revenue_by_source.get("slack_bots", 0.0)
            self.current_metrics.marketplace_actions = revenue_by_source.get(
                "marketplace_actions", 0.0
            )
            self.current_metrics.license_server = revenue_by_source.get("license_server", 0.0)
            self.current_metrics.saas_subscriptions = revenue_by_source.get(
                "saas_subscriptions", 0.0
            )
            self.current_metrics.enterprise_deals = revenue_by_source.get("enterprise_deals", 0.0)

            conn.close()

        except Exception as e:
            logger.error(f"Failed to update current metrics: {e}")

    async def update_user_metrics(self):
        """Update user metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count users by plan
            cursor.execute(
                """
                SELECT plan, COUNT(DISTINCT user_id)
                FROM user_events
                WHERE event_type = 'subscription_created' OR event_type = 'plan_upgraded'
                GROUP BY plan
            """
            )

            users_by_plan = dict(cursor.fetchall())

            self.user_metrics.free_users = users_by_plan.get("free", 0)
            self.user_metrics.pro_users = users_by_plan.get("pro", 0)
            self.user_metrics.enterprise_users = users_by_plan.get("enterprise", 0)
            self.user_metrics.total_users = sum(users_by_plan.values())

            # Calculate conversion rate
            if self.user_metrics.total_users > 0:
                self.user_metrics.conversion_rate = (
                    self.user_metrics.paying_users / self.user_metrics.total_users
                ) * 100

            conn.close()

        except Exception as e:
            logger.error(f"Failed to update user metrics: {e}")

    async def generate_ai_insights(self) -> dict:
        """Generate AI-powered business insights"""
        try:
            # Prepare data for AI analysis
            analytics_prompt = f"""
            Analyze the following EQ12 revenue data and provide strategic business insights:

            Current Monthly Revenue: ${self.current_metrics.total_revenue:.2f}
            Monthly Target: ${self.monthly_target:.2f}

            Revenue Breakdown:
            - GitHub Actions: ${self.current_metrics.github_actions:.2f}
            - Chrome Extension: ${self.current_metrics.chrome_extension:.2f}
            - Slack Bots: ${self.current_metrics.slack_bots:.2f}
            - Marketplace Actions: ${self.current_metrics.marketplace_actions:.2f}
            - License Server: ${self.current_metrics.license_server:.2f}
            - SaaS Subscriptions: ${self.current_metrics.saas_subscriptions:.2f}
            - Enterprise Deals: ${self.current_metrics.enterprise_deals:.2f}

            User Metrics:
            - Total Users: {self.user_metrics.total_users}
            - Free Users: {self.user_metrics.free_users}
            - Pro Users: {self.user_metrics.pro_users}
            - Enterprise Users: {self.user_metrics.enterprise_users}
            - Conversion Rate: {self.user_metrics.conversion_rate:.1f}%

            Provide:
            1. Top 3 revenue optimization opportunities
            2. User acquisition and retention strategies
            3. Product development priorities
            4. Pricing optimization suggestions
            5. Market expansion opportunities
            """

            response = await self.openai_manager.secure_openai_request(
                "gpt-4o-mini",
                [
                    {
                        "role": "system",
                        "content": "You are a strategic business analyst specializing in SaaS and developer tools monetization. Provide actionable, data-driven insights.",
                    },
                    {"role": "user", "content": analytics_prompt},
                ],
                {"max_tokens": 1000, "temperature": 0.3},
            )

            insights = response["response"]["choices"][0]["message"]["content"]

            return {
                "insights": insights,
                "model": "gpt-4o-mini",
                "generated_at": datetime.now().isoformat(),
                "cost": response.get("cost_check", {}).get("estimated_cost", 0),
            }

        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            return {"error": str(e)}

    async def generate_revenue_forecast(self) -> dict:
        """Generate revenue forecasting with AI"""
        try:
            # Get historical revenue data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DATE(timestamp) as date, SUM(amount) as revenue
                FROM revenue_events
                WHERE timestamp >= date('now', '-30 days')
                GROUP BY DATE(timestamp)
                ORDER BY date
            """
            )

            historical_data = cursor.fetchall()
            conn.close()

            # Simple forecasting (in production, would use more sophisticated models)
            if len(historical_data) >= 7:
                recent_avg = sum(row[1] for row in historical_data[-7:]) / 7
                growth_rate = self.calculate_growth_rate(historical_data)

                # Forecast next 30 days
                forecast = []
                for i in range(1, 31):
                    projected_revenue = recent_avg * (1 + growth_rate) ** i
                    forecast_date = datetime.now() + timedelta(days=i)
                    forecast.append(
                        {
                            "date": forecast_date.strftime("%Y-%m-%d"),
                            "projected_revenue": round(projected_revenue, 2),
                        }
                    )

                return {
                    "forecast": forecast,
                    "monthly_projection": sum(day["projected_revenue"] for day in forecast),
                    "confidence": self.calculate_forecast_confidence(historical_data),
                    "generated_at": datetime.now().isoformat(),
                }

            return {"error": "Insufficient data for forecasting"}

        except Exception as e:
            logger.error(f"Failed to generate forecast: {e}")
            return {"error": str(e)}

    def calculate_growth_rate(self, data: list) -> float:
        """Calculate growth rate from historical data"""
        if len(data) < 2:
            return 0.0

        # Simple linear growth calculation
        recent_period = data[-7:] if len(data) >= 7 else data
        early_avg = sum(row[1] for row in recent_period[: len(recent_period) // 2]) / (
            len(recent_period) // 2
        )
        late_avg = sum(row[1] for row in recent_period[len(recent_period) // 2 :]) / (
            len(recent_period) - len(recent_period) // 2
        )

        if early_avg > 0:
            return (late_avg - early_avg) / early_avg / len(recent_period)
        return 0.0

    def calculate_forecast_confidence(self, data: list) -> float:
        """Calculate confidence score for forecast"""
        # More data = higher confidence
        data_score = min(len(data) / 30, 1.0) * 0.5

        # Consistency in revenue = higher confidence
        revenues = [row[1] for row in data]
        if revenues:
            avg_revenue = sum(revenues) / len(revenues)
            variance = sum((r - avg_revenue) ** 2 for r in revenues) / len(revenues)
            consistency_score = (
                max(0, 1 - (variance / (avg_revenue**2))) * 0.3 if avg_revenue > 0 else 0
            )
        else:
            consistency_score = 0

        # Recent growth = higher confidence
        growth_rate = abs(self.calculate_growth_rate(data))
        growth_score = min(growth_rate * 100, 1.0) * 0.2

        return min(data_score + consistency_score + growth_score, 0.95)

    async def generate_optimization_suggestions(self) -> dict:
        """Generate revenue optimization suggestions"""
        suggestions = []

        # Analyze revenue streams
        total_revenue = self.current_metrics.total_revenue

        if total_revenue == 0:
            return {
                "suggestions": [
                    {
                        "category": "Getting Started",
                        "title": "Launch first revenue stream",
                        "description": "Start with GitHub Actions marketplace - lowest barrier to entry",
                        "priority": "high",
                        "estimated_impact": "$1000-5000/month",
                    }
                ]
            }

        # Identify underperforming streams
        revenue_streams = {
            "GitHub Actions": self.current_metrics.github_actions,
            "Chrome Extension": self.current_metrics.chrome_extension,
            "Slack Bots": self.current_metrics.slack_bots,
            "Marketplace": self.current_metrics.marketplace_actions,
            "License Server": self.current_metrics.license_server,
            "SaaS": self.current_metrics.saas_subscriptions,
            "Enterprise": self.current_metrics.enterprise_deals,
        }

        # Find top and bottom performers
        sorted_streams = sorted(revenue_streams.items(), key=lambda x: x[1], reverse=True)
        top_performer = sorted_streams[0]
        underperformers = [stream for stream in sorted_streams if stream[1] < total_revenue * 0.1]

        # Generate suggestions based on analysis
        if top_performer[1] > total_revenue * 0.5:
            suggestions.append(
                {
                    "category": "Diversification",
                    "title": f"Reduce dependency on {top_performer[0]}",
                    "description": f"{top_performer[0]} generates {(top_performer[1] / total_revenue * 100):.1f}% of revenue. Diversify to reduce risk.",
                    "priority": "medium",
                    "estimated_impact": "$500-2000/month",
                }
            )

        for stream_name, revenue in underperformers:
            if revenue == 0:
                suggestions.append(
                    {
                        "category": "New Revenue Stream",
                        "title": f"Launch {stream_name}",
                        "description": f"Untapped revenue opportunity in {stream_name}",
                        "priority": "high",
                        "estimated_impact": "$1000-3000/month",
                    }
                )
            else:
                suggestions.append(
                    {
                        "category": "Optimization",
                        "title": f"Optimize {stream_name}",
                        "description": f"{stream_name} underperforming at ${revenue:.2f}/month",
                        "priority": "medium",
                        "estimated_impact": f"${revenue * 2:.0f}-{revenue * 5:.0f}/month",
                    }
                )

        # Conversion rate optimization
        if self.user_metrics.conversion_rate < 10:
            suggestions.append(
                {
                    "category": "Conversion",
                    "title": "Improve conversion rate",
                    "description": f"Current rate {self.user_metrics.conversion_rate:.1f}% is below industry average (15%)",
                    "priority": "high",
                    "estimated_impact": f"${total_revenue * 0.5:.0f}-{total_revenue * 1.5:.0f}/month",
                }
            )

        return {"suggestions": suggestions, "generated_at": datetime.now().isoformat()}

    def get_dashboard_html(self) -> str:
        """Generate revenue dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EQ12 Revenue Analytics Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }
                .dashboard {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                .header {
                    text-align: center;
                    color: white;
                    margin-bottom: 30px;
                }
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .metric-card {
                    background: rgba(255,255,255,0.95);
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .metric-card:hover { transform: translateY(-5px); }
                .metric-value {
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #4CAF50;
                    margin-bottom: 10px;
                }
                .metric-label {
                    font-size: 1.1em;
                    color: #666;
                    font-weight: 500;
                }
                .chart-container {
                    background: rgba(255,255,255,0.95);
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }
                .insights {
                    background: rgba(255,255,255,0.95);
                    border-radius: 12px;
                    padding: 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }
                .refresh-btn {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin: 10px 5px;
                }
            </style>
        </head>
        <body>
            <div class="dashboard">
                <div class="header">
                    <h1>💰 EQ12 Revenue Analytics Dashboard</h1>
                    <p>Real-time monetization tracking and AI insights</p>
                </div>

                <div class="metrics-grid" id="metricsGrid">
                    <!-- Metrics will be loaded here -->
                </div>

                <div class="chart-container">
                    <h3>Revenue Streams</h3>
                    <canvas id="revenueChart" width="400" height="200"></canvas>
                </div>

                <div class="insights" id="aiInsights">
                    <h3>🧠 AI Business Insights</h3>
                    <button class="refresh-btn" onclick="loadAIInsights()">Generate AI Insights</button>
                    <div id="insightsContent">Click to generate AI-powered business insights...</div>
                </div>
            </div>

            <script>
                let revenueChart = null;

                async function loadMetrics() {
                    try {
                        const response = await fetch('/api/metrics');
                        const data = await response.json();

                        // Update metrics display
                        const metricsGrid = document.getElementById('metricsGrid');
                        metricsGrid.innerHTML = `
                            <div class="metric-card">
                                <div class="metric-value">$$${data.revenue.total_revenue.toLocaleString()}</div>
                                <div class="metric-label">Total Revenue</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${data.users.total_users}</div>
                                <div class="metric-label">Total Users</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${data.users.conversion_rate.toFixed(1)}%</div>
                                <div class="metric-label">Conversion Rate</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value">${data.progress.monthly_progress.toFixed(1)}%</div>
                                <div class="metric-label">Monthly Target</div>
                            </div>
                        `;

                        // Update chart
                        updateRevenueChart(data.revenue);

                    } catch (error) {
                        console.error('Failed to load metrics:', error);
                    }
                }

                function updateRevenueChart(revenue) {
                    const ctx = document.getElementById('revenueChart').getContext('2d');

                    if (revenueChart) {
                        revenueChart.destroy();
                    }

                    revenueChart = new Chart(ctx, {
                        type: 'doughnut',
                        data: {
                            labels: ['GitHub Actions', 'Chrome Extension', 'Slack Bots', 'Marketplace', 'License Server', 'SaaS', 'Enterprise'],
                            datasets: [{
                                data: [
                                    revenue.github_actions,
                                    revenue.chrome_extension,
                                    revenue.slack_bots,
                                    revenue.marketplace_actions,
                                    revenue.license_server,
                                    revenue.saas_subscriptions,
                                    revenue.enterprise_deals
                                ],
                                backgroundColor: [
                                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                                    '#9966FF', '#FF9F40', '#FF6384'
                                ]
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: {
                                legend: {
                                    position: 'right'
                                }
                            }
                        }
                    });
                }

                async function loadAIInsights() {
                    const button = event.target;
                    const content = document.getElementById('insightsContent');

                    button.textContent = 'Generating...';
                    button.disabled = true;

                    try {
                        const response = await fetch('/api/analytics/ai-insights');
                        const data = await response.json();

                        if (data.insights) {
                            content.innerHTML = `
                                <div style="white-space: pre-wrap; line-height: 1.6;">
                                    ${data.insights}
                                </div>
                                <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
                                    Generated by ${data.model} at ${new Date(data.generated_at).toLocaleString()}
                                </p>
                            `;
                        } else if (data.error) {
                            content.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                        }

                    } catch (error) {
                        content.innerHTML = `<p style="color: red;">Failed to generate insights: ${error.message}</p>`;
                    }

                    button.textContent = 'Refresh Insights';
                    button.disabled = false;
                }

                // Auto-refresh metrics every 30 seconds
                setInterval(loadMetrics, 30000);

                // Initial load
                loadMetrics();
            </script>
        </body>
        </html>
        """

    async def start_server(self, host="0.0.0.0", port=8001):
        """Start the revenue analytics server"""
        import uvicorn

        logger.info(f"🚀 Starting EQ12 Revenue Analytics Dashboard on {host}:{port}")
        logger.info(f"💰 Monthly target: ${self.monthly_target:,.2f}")
        logger.info(f"🎯 Annual target: ${self.annual_target:,.2f}")

        # Initialize with some demo data
        await self.seed_demo_data()

        uvicorn.run(self.app, host=host, port=port)

    async def seed_demo_data(self):
        """Seed with demo revenue data"""
        demo_events = [
            {
                "source": "github_actions",
                "event_type": "subscription",
                "amount": 299.99,
                "user_id": "demo1",
                "subscription_plan": "pro",
            },
            {
                "source": "chrome_extension",
                "event_type": "subscription",
                "amount": 299.99,
                "user_id": "demo2",
                "subscription_plan": "pro",
            },
            {
                "source": "license_server",
                "event_type": "api_usage",
                "amount": 150.00,
                "user_id": "demo3",
                "subscription_plan": "enterprise",
            },
            {
                "source": "saas_subscriptions",
                "event_type": "monthly_billing",
                "amount": 999.99,
                "user_id": "demo4",
                "subscription_plan": "enterprise",
            },
        ]

        for event in demo_events:
            await self.record_revenue_event(event)

        # Demo user events
        user_events = [
            {
                "user_id": "demo1",
                "event_type": "subscription_created",
                "source": "github_actions",
                "plan": "pro",
            },
            {
                "user_id": "demo2",
                "event_type": "subscription_created",
                "source": "chrome_extension",
                "plan": "pro",
            },
            {
                "user_id": "demo3",
                "event_type": "subscription_created",
                "source": "license_server",
                "plan": "enterprise",
            },
            {
                "user_id": "demo4",
                "event_type": "subscription_created",
                "source": "saas_subscriptions",
                "plan": "enterprise",
            },
        ]

        for event in user_events:
            await self.record_user_event(event)

        logger.info("✅ Demo data seeded successfully")


if __name__ == "__main__":
    # Run the revenue analytics dashboard
    analytics = EQ12RevenueAnalytics()
    asyncio.run(analytics.start_server())
