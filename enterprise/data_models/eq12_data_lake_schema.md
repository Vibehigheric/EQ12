# EQ12 Enterprise Data Lake Schema Definitions
# Parquet/Delta Lake schemas for all 312 EQ12 components

## Betting Engine Data Schema

### Parlay Data (`betting/parlays/`)
```yaml
parlay_id: string (primary key)
org_id: string (tenant isolation)
user_id: string  
created_timestamp: timestamp
sport: string (nfl, nba, nhl, mlb, etc.)
league: string
strategy: string (advanced, bulletproof, simulation, conservative)
total_legs: integer
total_odds: double
expected_value: double
kelly_bet: double
confidence_score: double
risk_assessment: string
status: string (pending, won, lost, void)
payout: double (nullable)
settlement_timestamp: timestamp (nullable)
source_engine: string (references EQ12 betting engine name)
```

### Odds Data (`betting/odds/`)
```yaml
odds_id: string (primary key)
game_id: string
book: string (fanduel, draftkings, bet365, etc.)
sport: string
league: string
home_team: string
away_team: string
game_start_time: timestamp
market: string (spread, moneyline, total, props)
selection: string
price_decimal: double
price_american: integer
timestamp: timestamp
source: string (api, scraper, manual)
eq12_engine: string (source EQ12 component)
```

### Results Data (`betting/results/`)
```yaml
game_id: string (primary key)
sport: string
league: string
home_team: string
away_team: string
home_score: integer
away_score: integer
game_date: date
season: string
week: integer (nullable)
status: string (final, postponed, cancelled)
updated_timestamp: timestamp
source: string
```

### Tickets Data (`betting/tickets/`)
```yaml
ticket_id: string (primary key)
parlay_id: string (foreign key)
org_id: string
user_id: string
book: string
stake: double
potential_payout: double
ticket_timestamp: timestamp
bet_placement_method: string (api, manual)
external_bet_id: string (book's reference)
status: string (placed, won, lost, void, pending)
settlement_timestamp: timestamp (nullable)
actual_payout: double (nullable)
```

## AI Model Data Schema

### Model Predictions (`ai_models/predictions/`)
```yaml
prediction_id: string (primary key)
model_name: string (references EQ12 AI model)
model_version: string
input_features: map<string, double> (JSON)
prediction: double
confidence: double
timestamp: timestamp
game_id: string (nullable)
sport: string
market: string
actual_outcome: double (nullable, for backtesting)
prediction_accuracy: double (nullable)
latency_ms: integer
```

### Model Performance (`ai_models/performance/`)
```yaml
model_name: string
date: date
total_predictions: integer
accuracy: double
precision: double
recall: double
f1_score: double
mean_absolute_error: double
root_mean_square_error: double
sharpe_ratio: double (for betting models)
roi: double
total_profit: double
max_drawdown: double
```

## System Metrics Schema

### Component Health (`system_metrics/components/`)
```yaml
component_name: string
component_type: string (betting_engine, ai_model, automation, monitor, etc.)
timestamp: timestamp
status: string (healthy, warning, error, offline)
cpu_usage_percent: double
memory_usage_mb: double
disk_usage_mb: double
network_io_kb: double
error_count: integer
warning_count: integer
uptime_seconds: integer
response_time_ms: double (for APIs)
last_execution: timestamp
execution_count: integer
```

### System Logs (`system_metrics/logs/`)
```yaml
log_id: string (primary key)
timestamp: timestamp
level: string (info, warning, error, debug)
component: string
message: string
stack_trace: string (nullable)
context: map<string, string> (JSON)
user_id: string (nullable)
session_id: string (nullable)
correlation_id: string (nullable)
```

## Automation Data Schema

### Script Execution (`automation/execution/`)
```yaml
execution_id: string (primary key)
script_name: string
script_type: string (python, powershell)
trigger: string (scheduled, manual, api, event)
start_timestamp: timestamp
end_timestamp: timestamp (nullable)
duration_seconds: double
status: string (running, completed, failed, timeout)
exit_code: integer (nullable)
stdout: string (truncated to 10KB)
stderr: string (truncated to 10KB)
input_parameters: map<string, string> (JSON)
output_data: map<string, any> (JSON)
resource_usage: map<string, double> (JSON - cpu, memory, etc.)
```

### Workflow Data (`automation/workflows/`)
```yaml
workflow_id: string (primary key)
workflow_name: string
trigger_event: string
start_timestamp: timestamp
end_timestamp: timestamp (nullable)
status: string (running, completed, failed, paused)
steps_total: integer
steps_completed: integer
steps_failed: integer
current_step: string (nullable)
error_message: string (nullable)
retry_count: integer
```

## Data Partitioning Strategy

### Time-based Partitioning
- All tables partitioned by `date=YYYY-MM-DD`
- Hourly sub-partitioning for high-volume data: `hour=HH`
- Automatic archival after 90 days to cold storage

### Entity-based Partitioning
- `org_id` partitioning for multi-tenant isolation
- `sport` partitioning for betting data
- `component_type` partitioning for system metrics

### Example Directory Structure
```
s3://eq12-enterprise-lake/
  betting/
    parlays/date=2025-11-08/org_id=eq12_prod/sport=nfl/*.parquet
    odds/date=2025-11-08/book=fanduel/sport=nfl/*.parquet
    results/date=2025-11-08/sport=nfl/week=11/*.parquet
    tickets/date=2025-11-08/org_id=eq12_prod/book=draftkings/*.parquet
  ai_models/
    predictions/date=2025-11-08/model=eq12_nfl_predictor_v2/*.parquet
    performance/date=2025-11-08/model=eq12_nfl_predictor_v2/*.parquet
  system_metrics/
    components/date=2025-11-08/type=betting_engine/*.parquet
    logs/date=2025-11-08/level=error/*.parquet
  automation/
    execution/date=2025-11-08/script=eq12_advanced_parlay_generator/*.parquet
    workflows/date=2025-11-08/workflow=daily_parlay_generation/*.parquet
```

## Data Access Patterns

### Analytics Queries
```sql
-- Daily betting performance
SELECT 
  date,
  COUNT(*) as total_parlays,
  SUM(stake) as total_wagered,
  SUM(actual_payout) as total_payout,
  (SUM(actual_payout) - SUM(stake)) / SUM(stake) * 100 as roi_percent
FROM betting.tickets 
WHERE date >= '2025-11-01' 
GROUP BY date 
ORDER BY date;

-- AI Model Accuracy
SELECT 
  model_name,
  AVG(accuracy) as avg_accuracy,
  AVG(roi) as avg_roi,
  COUNT(*) as total_predictions
FROM ai_models.performance 
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY model_name 
ORDER BY avg_roi DESC;

-- System Health Overview
SELECT 
  component_type,
  COUNT(*) as total_components,
  SUM(CASE WHEN status = 'healthy' THEN 1 ELSE 0 END) as healthy_components,
  AVG(cpu_usage_percent) as avg_cpu,
  AVG(memory_usage_mb) as avg_memory
FROM system_metrics.components 
WHERE date = CURRENT_DATE 
GROUP BY component_type;
```

### Real-time Streaming
- Kafka Connect for real-time ingestion from EQ12 components
- Delta Lake for ACID transactions on changing data
- Structured streaming for real-time analytics

## Data Quality & Governance

### Schema Evolution
- Backward compatible schema changes only
- Version control for all schema definitions
- Automated migration scripts for breaking changes

### Data Quality Checks
- Required field validation
- Range checks for numeric fields
- Referential integrity between datasets
- Duplicate detection and deduplication

### Privacy & Security
- PII encryption at rest and in transit
- Column-level access controls
- Audit logging for all data access
- GDPR compliance for user data deletion

### Data Retention
- Hot data: 90 days (S3 Standard)
- Warm data: 1 year (S3 IA)
- Cold data: 7 years (S3 Glacier)
- Compliance data: Indefinite retention

## Integration with EQ12 Components

### Existing Data Sources
- C:\EQ12\logs\*.json  system_metrics.logs
- C:\EQ12\data\*.db  betting.* (migrated)
- EQ12 component outputs  component-specific tables

### Real-time Pipelines
- EQ12SystemManager.exe monitoring  system_metrics.components
- Betting engine execution  betting.parlays + betting.tickets
- AI model inference  ai_models.predictions
- Automation script runs  automation.execution

### API Integration
- REST APIs for data ingestion from EQ12 components
- GraphQL for flexible data queries
- WebSocket for real-time data streaming
- Batch APIs for bulk data uploads