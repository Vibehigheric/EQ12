# EQ12 Complete Search Ecosystem Documentation

## Overview

The EQ12 Search Ecosystem is a comprehensive intelligence platform that integrates multiple search sources, AI-powered analysis, and stack-specific routing to provide unified, intelligent search capabilities across all EQ12 business domains.

## Architecture

### Core Components

1. **EQ12 Master Ecosystem Controller** (`eq12_master_ecosystem.py`)
   - Central orchestration for all search operations
   - Parallel execution across multiple intelligence modules
   - Comprehensive result aggregation and analysis
   - Stack routing and query optimization

2. **Intelligence Modules**
   - **Unified Search** (`eq12_unified_search.py`) - Core meta-search with Google + Bing
   - **Intelligent Router** (`eq12_intelligent_router.py`) - Stack detection and routing
   - **News Intelligence** (`news_intelligence.py`) - Real-time news with sentiment analysis
   - **Swagbucks Intelligence** (`swagbucks_intelligence.py`) - Cashback offers with stack categorization
   - **Autosuggest Intelligence** (`autosuggest_intelligence.py`) - Query expansion and SEO keywords

3. **Enhanced Database** (`enhanced_db.py`)
   - SQLite-based storage with intelligence metadata
   - Separate tables for results, news, offers, autosuggest, and analytics
   - Performance metrics and caching system

4. **Godstack2 Integration**
   - Existing multi-source aggregation system
   - News aggregation (Bing News + Google News RSS)
   - Swagbucks scraping with Playwright
   - Autosuggest merging (Bing + Google)

## Stack Categories

The system supports five core business stacks:

- **Betting** - Sports betting, injury reports, odds analysis
- **Travel** - Flight deals, hotel bookings, destination info
- **Cannabis** - Dispensaries, products, legal news, regulations
- **Finance** - Stocks, crypto, market analysis, investment news
- **Fleet** - Auto industry, vehicle deals, maintenance, insurance

## Quick Start

### Basic Usage

```python
from eq12_master_ecosystem import EQ12MasterController

# Initialize the ecosystem
controller = EQ12MasterController(verbose=True)

# Comprehensive search across all systems
results = controller.comprehensive_search(
    query="NFL injury report",
    mode="unified",
    count=20,
    include_news=True,
    include_offers=True,
    include_expansion=True
)

# Results contain unified search, news, offers, and query expansions
print(f"Found {results['metadata']['total_results']} results")
print(f"Detected stack: {results['detected_stack']}")
print(f"Processing time: {results['metadata']['processing_time_ms']}ms")

# Access specific result types
unified_results = results['unified_results']
news_results = results['news_results'] 
offers_results = results['offers_results']
expansion_results = results['expansion_results']
```

### Stack-Specific Search

```python
# Quick stack-focused search
betting_results = controller.quick_stack_search(
    query="Lakers vs Warriors injury report",
    stack="betting",
    mode="focused"
)

# News-only search for travel alerts
travel_news = controller.comprehensive_search(
    query="flight delays buffalo airport",
    mode="news",
    stack="travel",
    time_window_hours=6
)
```

### Multi-Query Analysis

```python
# Analyze multiple related queries for patterns
queries = [
    "Josh Allen injury status",
    "Bills quarterback news", 
    "Buffalo Bills depth chart"
]

analysis = controller.multi_query_analysis(queries, stack="betting")
print(f"Cross-query patterns: {analysis['cross_query_patterns']}")
print(f"Sentiment trends: {analysis['sentiment_trends']}")
```

## Individual Module Usage

### News Intelligence

```python
from news_intelligence import NewsIntelligence

intel = NewsIntelligence(verbose=True)

# Stack-specific news with sentiment analysis
results = intel.aggregate_news_with_analysis(
    query="Lakers injury report",
    stack="betting",
    count=15,
    hours=12
)

# Results include sentiment analysis, urgency scoring, and action recommendations
for article in results['results']:
    print(f"Title: {article['title']}")
    print(f"Sentiment: {article['sentiment_analysis']['overall_sentiment']}")
    print(f"Urgency: {article['time_sensitivity']}")
    if article['action_required']:
        print("🚨 ACTION REQUIRED")
```

### Swagbucks Intelligence

```python
from swagbucks_intelligence import SwagbucksIntelligence

intel = SwagbucksIntelligence(verbose=True)

# Find stack-specific cashback offers
results = intel.analyze_offers_for_query(
    query="travel booking",
    stack="travel",
    limit=10
)

# Results include offer quality assessment and stack relevance
for offer in results['results']:
    print(f"Offer: {offer['title']}")
    print(f"Cashback: {offer['cashback_amount']} {offer['cashback_type']}")
    print(f"Quality Score: {offer['offer_quality']['overall_score']:.2f}")
    print(f"Stack Relevance: {offer['confidence_score']:.2f}")
```

### Autosuggest Intelligence

```python
from autosuggest_intelligence import AutosuggestIntelligence

intel = AutosuggestIntelligence(verbose=True)

# Generate query expansions with SEO analysis
results = intel.comprehensive_query_expansion(
    query="dispensary near me",
    stack="cannabis",
    count=20,
    include_seo=True
)

# Results include quality metrics and SEO potential
for suggestion in results['suggestions']:
    print(f"Suggestion: {suggestion['suggestion']}")
    print(f"Search Intent: {suggestion['search_intent']}")
    print(f"Long-tail Score: {suggestion['long_tail_score']:.2f}")
    print(f"SEO Potential: {suggestion['seo_potential']['overall_seo_score']:.2f}")

# SEO keywords by intent type
seo_keywords = results['seo_keywords']
for intent, keywords in seo_keywords.items():
    print(f"{intent.title()} Keywords: {', '.join(keywords[:3])}")
```

## CLI Usage

### Master Controller CLI

```bash
# Comprehensive search
python eq12_master_ecosystem.py --query "NFL injury report" --mode unified --verbose

# Stack-specific search
python eq12_master_ecosystem.py --query "flight deals buffalo" --stack travel --count 15

# Multi-query analysis
python eq12_master_ecosystem.py --multi-query "Lakers injury" "Warriors injury" "NBA news" --stack betting

# System health check
python eq12_master_ecosystem.py --status --verbose
```

### Individual Module CLIs

```bash
# News intelligence
python news_intelligence.py --query "crypto news" --stack finance --hours 6 --verbose

# Swagbucks intelligence
python swagbucks_intelligence.py --query "hotel booking" --stack travel --limit 10 --json

# Autosuggest intelligence
python autosuggest_intelligence.py --query "dispensary" --stack cannabis --seo --verbose
```

## Configuration

### Environment Variables

```bash
# Database configuration
export META_DB_PATH="meta_search_enhanced.sqlite3"
export LEGACY_META_DB_PATH="meta_search.sqlite3"

# Bing Search API (required)
export BING_SEARCH_KEY="your_bing_api_key"
export BING_NEWS_KEY="your_bing_news_key"

# Optional: Custom endpoints
export BING_SEARCH_ENDPOINT="https://api.bing.microsoft.com/v7.0/search"
export BING_NEWS_ENDPOINT="https://api.bing.microsoft.com/v7.0/news/search"
```

### Database Setup

```python
from enhanced_db import create_tables, init_enhanced_db

# Initialize all tables
create_tables()

# Or initialize with custom path
init_enhanced_db("/path/to/custom/database.sqlite3")
```

## Integration Patterns

### Telegram Integration

```python
# Example: Send high-priority news alerts
def check_and_alert_critical_news(stack: str):
    controller = EQ12MasterController()
    
    results = controller.comprehensive_search(
        query=f"{stack} breaking news",
        mode="news",
        stack=stack,
        time_window_hours=1
    )
    
    critical_news = [
        article for article in results['news_results']
        if article.get('action_required', False) or 
           article.get('time_sensitivity') == 'critical'
    ]
    
    for article in critical_news:
        emoji = article.get('telegram_emoji', '📰')
        send_telegram_alert(f"{emoji} URGENT: {article['title']}")
```

### Automation Bridge Integration

```python
from eq12_automation_bridge import EQ12AutomationBridge

# Integration with existing EQ12 systems
bridge = EQ12AutomationBridge()

# Search for automation opportunities
automation_results = bridge.search_for_automation(
    query="travel deals automation",
    stack="travel"
)

# Trigger godmode runner based on search results
if automation_results.get('godmode_opportunities'):
    bridge.trigger_godmode_runner("travel_deal_hunter")
```

### Custom Intelligence Modules

```python
# Template for creating new intelligence modules
class CustomIntelligence:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.setup_logging()
    
    def analyze_query(self, query: str, stack: Optional[str] = None) -> Dict[str, Any]:
        # Implement custom analysis logic
        pass
    
    def enhance_results(self, results: List[Dict]) -> List[Dict]:
        # Add custom enhancement metadata
        pass
```

## Performance Optimization

### Caching Strategy

The system uses multi-level caching:

1. **Stack Analysis Cache** - Cache stack detection results (24h TTL)
2. **Performance Metrics** - Track response times and API usage
3. **Database Indexing** - Optimized indexes for common query patterns

### Parallel Execution

```python
# The master controller uses ThreadPoolExecutor for parallel operations
# Configure worker threads based on your system:

controller = EQ12MasterController()
# Default: 8 worker threads

# For high-volume usage, increase worker count:
controller.executor._max_workers = 16
```

### Rate Limiting

- Bing Search API: 3 calls/second, 1000 calls/month (free tier)
- Google News RSS: No official limits, but recommend 1 call/second
- Swagbucks scraping: 1 request/2 seconds to avoid blocks

## Troubleshooting

### Common Issues

1. **"Core modules not available"**
   - Check that all required files are in the correct directories
   - Verify Python path includes both base directory and godstack2

2. **Bing API errors**
   - Verify API keys are set correctly in environment variables
   - Check API quotas and rate limits

3. **Database errors**
   - Ensure SQLite database is writable
   - Run `create_tables()` to initialize schema

4. **Import errors**
   - Check that godstack2 directory exists and contains required files
   - Verify all dependencies are installed

### Debug Mode

```python
# Enable verbose logging for debugging
controller = EQ12MasterController(verbose=True)

# Check system status
status = controller.get_system_status()
print(f"Overall health: {status['overall_health']}")

for component, health in status['components'].items():
    if health != "healthy":
        print(f"⚠️ {component}: {health}")
```

### Performance Monitoring

```python
from enhanced_db import record_performance_metric, get_performance_stats

# Record custom metrics
record_performance_metric(
    "custom_operation_time", 
    processing_time_ms,
    stack="betting",
    source="custom_module"
)

# Analyze performance trends
stats = get_performance_stats("api_response_time", days=7)
```

## API Reference

### EQ12MasterController

#### `comprehensive_search(query, mode="unified", stack=None, count=20, **kwargs)`

Performs comprehensive search across all EQ12 systems.

**Parameters:**
- `query` (str): Search query
- `mode` (str): Search mode - "unified", "intelligence", "news", "offers", "expansion", "automation"
- `stack` (str, optional): Target stack - "betting", "travel", "cannabis", "finance", "fleet"
- `count` (int): Number of results per source
- `include_news` (bool): Include news intelligence (default: True)
- `include_offers` (bool): Include Swagbucks offers (default: True)
- `include_expansion` (bool): Include query expansion (default: True)
- `time_window_hours` (int): News time window in hours (default: 24)

**Returns:**
Dictionary with comprehensive search results and analysis.

#### `quick_stack_search(query, stack, mode="focused")`

Optimized search focused on a specific stack.

**Parameters:**
- `query` (str): Search query
- `stack` (str): Target stack
- `mode` (str): Search focus - "focused", "comprehensive", "news-only", "offers-only"

**Returns:**
Stack-focused search results.

#### `multi_query_analysis(queries, stack=None)`

Analyze multiple related queries for comprehensive insights.

**Parameters:**
- `queries` (List[str]): List of search queries
- `stack` (str, optional): Target stack

**Returns:**
Multi-query analysis with cross-pattern detection.

#### `get_system_status()`

Get comprehensive status of all EQ12 ecosystem components.

**Returns:**
System health status and component diagnostics.

## Advanced Usage

### Custom Result Processing

```python
def process_search_results(results):
    """Custom processing pipeline for search results"""
    
    # Extract high-confidence results
    high_confidence = [
        result for result in results['unified_results']
        if result.get('confidence_score', 0) >= 0.8
    ]
    
    # Filter urgent news
    urgent_news = [
        article for article in results['news_results']
        if article.get('time_sensitivity') in ['critical', 'high']
    ]
    
    # Find relevant offers
    relevant_offers = [
        offer for offer in results['offers_results']
        if offer.get('offer_quality', {}).get('overall_score', 0) >= 0.7
    ]
    
    return {
        'high_confidence_results': high_confidence,
        'urgent_news': urgent_news,
        'relevant_offers': relevant_offers,
        'processing_summary': {
            'total_processed': len(results['unified_results']),
            'high_confidence_count': len(high_confidence),
            'urgent_news_count': len(urgent_news),
            'relevant_offers_count': len(relevant_offers)
        }
    }
```

### Batch Processing

```python
def batch_process_queries(queries, stack=None, max_parallel=5):
    """Process multiple queries in batches"""
    import concurrent.futures
    
    controller = EQ12MasterController()
    results = {}
    
    # Process in batches to avoid overwhelming APIs
    for i in range(0, len(queries), max_parallel):
        batch = queries[i:i + max_parallel]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
            future_to_query = {
                executor.submit(
                    controller.comprehensive_search, 
                    query, 
                    stack=stack,
                    count=10
                ): query for query in batch
            }
            
            for future in concurrent.futures.as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    result = future.result(timeout=60)
                    results[query] = result
                except Exception as e:
                    results[query] = {'error': str(e)}
    
    return results
```

### Real-time Monitoring

```python
def setup_real_time_monitoring():
    """Setup real-time monitoring and alerting"""
    
    def monitor_stack_news(stack: str, keywords: List[str]):
        """Monitor specific stack for breaking news"""
        while True:
            for keyword in keywords:
                try:
                    results = controller.comprehensive_search(
                        query=f"{stack} {keyword}",
                        mode="news",
                        stack=stack,
                        time_window_hours=1
                    )
                    
                    critical_articles = [
                        article for article in results['news_results']
                        if article.get('action_required', False)
                    ]
                    
                    for article in critical_articles:
                        send_alert(f"🚨 {stack.upper()}: {article['title']}")
                
                except Exception as e:
                    logger.error(f"Monitoring error for {stack}/{keyword}: {e}")
                
                time.sleep(300)  # Check every 5 minutes
    
    # Monitor different stacks
    monitor_threads = [
        threading.Thread(target=monitor_stack_news, args=("betting", ["injury", "trade", "suspended"])),
        threading.Thread(target=monitor_stack_news, args=("travel", ["delay", "cancellation", "alert"])),
        threading.Thread(target=monitor_stack_news, args=("finance", ["crash", "rally", "breaking"]))
    ]
    
    for thread in monitor_threads:
        thread.daemon = True
        thread.start()
```

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Query classification models
   - Result relevance scoring
   - Personalized recommendations

2. **Enhanced Analytics**
   - Real-time dashboards
   - Performance trending
   - User behavior analysis

3. **Additional Data Sources**
   - Social media monitoring
   - Forum sentiment tracking
   - RSS feed aggregation

4. **Advanced Caching**
   - Redis integration
   - Distributed caching
   - Smart cache invalidation

### Contributing

To add new intelligence modules:

1. Follow the existing module pattern (see `news_intelligence.py`)
2. Implement stack detection and confidence scoring
3. Add comprehensive error handling and logging
4. Include CLI interface and documentation
5. Update master controller integration
6. Add database schema extensions if needed

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review component logs with verbose=True
3. Use the system status check for diagnostics
4. Verify API keys and database permissions

The EQ12 Search Ecosystem provides a powerful, extensible platform for intelligent search across all business domains. Its modular architecture allows for easy customization and extension while maintaining high performance and reliability.