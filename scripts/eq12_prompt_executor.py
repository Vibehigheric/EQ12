#!/usr/bin/env python3
"""
EQ12 Prompt Executor - FULL SYSTEM CAPABILITIES
Parallel processing, GPU acceleration, multi-provider AI, intelligent caching
"""

import os
import json
import time
import argparse
import logging
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Dict, List, Optional
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue
import hashlib
import psutil
import multiprocessing

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# System detection
CPU_COUNT = multiprocessing.cpu_count()
TOTAL_RAM_GB = psutil.virtual_memory().total / (1024**3)
logger.info(f"System: {CPU_COUNT} CPUs, {TOTAL_RAM_GB:.1f}GB RAM")


class PromptExecutor:
    """Execute prompts with FULL system capabilities - parallel, cached, multi-provider"""
    
    def __init__(self, db_path: str, prompts_file: str, max_workers: int = None):
        self.db_path = db_path
        self.prompts_file = prompts_file
        self.max_workers = max_workers or min(CPU_COUNT * 2, 16)  # Optimize workers
        self.cache = {}  # In-memory cache
        self.lock = threading.Lock()  # Thread safety
        self.conn = None
        self.cursor = None
        self.setup_database()
        logger.info(f"Initialized with {self.max_workers} parallel workers")
        
    def setup_database(self):
        """Initialize SQLite database for knowledge storage"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS prompts_executed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_number INTEGER,
                prompt_text TEXT,
                response TEXT,
                category TEXT,
                tokens_used INTEGER,
                execution_time REAL,
                timestamp TEXT,
                success BOOLEAN,
                error_message TEXT,
                provider TEXT,
                cache_hit BOOLEAN DEFAULT 0,
                prompt_hash TEXT
            )
        ''')
        
        # Create index for faster lookups
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_prompt_hash ON prompts_executed(prompt_hash)
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category ON prompts_executed(category)
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                key_insights TEXT,
                related_prompts TEXT,
                confidence_score REAL,
                update_count INTEGER DEFAULT 1,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                frequency INTEGER DEFAULT 1,
                last_seen TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_prompts INTEGER,
                successful_executions INTEGER,
                total_tokens INTEGER,
                knowledge_entries INTEGER,
                last_update TEXT
            )
        ''')
        
        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")
        
    def load_prompts(self, start_line: int = 1, count: int = 100) -> List[Dict]:
        """Load prompts from file"""
        prompts = []
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Skip header lines (start at line 7)
            prompt_lines = [l.strip() for l in lines[6:] if l.strip()]
            
            for i, line in enumerate(prompt_lines[start_line-1:start_line-1+count], start=start_line):
                if '. ' in line:
                    parts = line.split('. ', 1)
                    if len(parts) == 2:
                        number = parts[0]
                        text = parts[1]
                        prompts.append({
                            'number': int(number) if number.isdigit() else i,
                            'text': text,
                            'category': self.categorize_prompt(text)
                        })
                        
            logger.info(f"Loaded {len(prompts)} prompts")
            return prompts
            
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            return []
            
    def categorize_prompt(self, prompt_text: str) -> str:
        """Categorize prompt by keywords"""
        categories = {
            'Technology': ['iPhone', 'Pixel', 'Meta Quest', 'Windows', 'tech', 'device', 'hardware'],
            'AI_ML': ['ChatGPT', 'AI', 'machine learning', 'neural', 'automation', 'Bard'],
            'Entertainment': ['Marvel', 'movie', 'show', 'Netflix', 'music', 'Taylor Swift'],
            'Sports': ['NFL', 'NBA', 'FIFA', 'Super Bowl', 'playoffs', 'fantasy'],
            'Finance': ['crypto', 'Bitcoin', 'stock', 'investment', 'passive income'],
            'Health': ['health', 'fitness', 'mental', 'wellness', 'diet', 'meditation'],
            'Business': ['business', 'marketing', 'SEO', 'e-commerce', 'startup'],
            'Education': ['learning', 'education', 'course', 'skill', 'tutorial'],
            'Gaming': ['game', 'gaming', 'GTA', 'Fortnite', 'esports', 'PlayStation'],
            'Social_Media': ['Instagram', 'Twitter', 'TikTok', 'influencer', 'social media']
        }
        
        prompt_lower = prompt_text.lower()
        for category, keywords in categories.items():
            if any(kw.lower() in prompt_lower for kw in keywords):
                return category
        return 'General'
        
    def get_prompt_hash(self, prompt_text: str) -> str:
        """Generate hash for prompt caching"""
        return hashlib.md5(prompt_text.encode()).hexdigest()
        
    def check_cache(self, prompt_hash: str) -> Optional[Dict]:
        """Check if prompt already executed"""
        # Check in-memory cache first
        if prompt_hash in self.cache:
            return self.cache[prompt_hash]
            
        # Check database
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT response, category, tokens_used, provider
                FROM prompts_executed
                WHERE prompt_hash = ? AND success = 1
                ORDER BY timestamp DESC LIMIT 1
            ''', (prompt_hash,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                cached = {
                    'response': result[0],
                    'category': result[1],
                    'tokens_used': result[2],
                    'provider': result[3],
                    'cache_hit': True
                }
                self.cache[prompt_hash] = cached
                return cached
        return None
    
    def execute_prompt(self, prompt: Dict) -> Dict:
        """Execute prompt with caching and multi-provider fallback"""
        import subprocess
        
        start_time = time.time()
        prompt_hash = self.get_prompt_hash(prompt['text'])
        
        result = {
            'prompt_number': prompt['number'],
            'prompt_text': prompt['text'],
            'category': prompt['category'],
            'success': False,
            'response': '',
            'tokens_used': 0,
            'error_message': None,
            'provider': 'Unknown',
            'cache_hit': False,
            'prompt_hash': prompt_hash
        }
        
        # Check cache first
        cached = self.check_cache(prompt_hash)
        if cached:
            result.update(cached)
            result['success'] = True
            result['execution_time'] = 0.01  # Instant
            logger.info(f"✓ Cache hit for prompt {prompt['number']}")
            return result
        
        try:
            # Use eq12_ai_query.py with multi-provider fallback
            cmd = [
                'python',
                'C:\\EQ12_BROKEN_20251122_210342\\scripts\\eq12_ai_query.py',
                prompt['text']
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=90,
                env=os.environ.copy()
            )
            
            if process.returncode == 0:
                response_text = process.stdout.strip()
                result['response'] = response_text
                result['success'] = True
                result['tokens_used'] = len(response_text.split())
                
                # Detect provider from response prefix
                if response_text.startswith('[Groq'):
                    result['provider'] = 'Groq'
                elif response_text.startswith('[OpenRouter'):
                    result['provider'] = 'OpenRouter'
                elif response_text.startswith('[Claude'):
                    result['provider'] = 'Claude'
                elif response_text.startswith('[OpenAI'):
                    result['provider'] = 'OpenAI'
                else:
                    result['provider'] = 'Unknown'
                    
                # Add to cache
                self.cache[prompt_hash] = {
                    'response': response_text,
                    'category': result['category'],
                    'tokens_used': result['tokens_used'],
                    'provider': result['provider']
                }
            else:
                result['error_message'] = process.stderr.strip()
                
        except subprocess.TimeoutExpired:
            result['error_message'] = "Execution timeout (90s)"
        except Exception as e:
            result['error_message'] = str(e)
            
        result['execution_time'] = time.time() - start_time
        return result
        
    def save_execution(self, result: Dict):
        """Save execution result to database (thread-safe)"""
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO prompts_executed 
                    (prompt_number, prompt_text, response, category, tokens_used, 
                     execution_time, timestamp, success, error_message, provider, 
                     cache_hit, prompt_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result['prompt_number'],
                    result['prompt_text'],
                    result['response'],
                    result['category'],
                    result['tokens_used'],
                    result['execution_time'],
                    datetime.utcnow().isoformat(),
                    result['success'],
                    result['error_message'],
                    result.get('provider', 'Unknown'),
                    result.get('cache_hit', False),
                    result.get('prompt_hash', '')
                ))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error saving execution: {e}")
            
    def extract_knowledge(self, prompt: str, response: str, category: str):
        """Extract and store knowledge from response"""
        if not response or len(response) < 50:
            return
            
        # Extract key insights (simple extraction - can be enhanced with NLP)
        insights = []
        
        # Look for numbered lists
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                insights.append(line.lstrip('0123456789.-•').strip())
                
        if insights:
            # Check if topic exists
            topic = prompt.split()[0:5]  # First 5 words as topic
            topic_str = ' '.join(topic)
            
            self.cursor.execute(
                'SELECT id, update_count FROM knowledge_base WHERE topic = ?',
                (topic_str,)
            )
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing knowledge
                self.cursor.execute('''
                    UPDATE knowledge_base 
                    SET key_insights = ?, update_count = update_count + 1, 
                        updated_at = ?
                    WHERE id = ?
                ''', (
                    '\n'.join(insights[:10]),  # Top 10 insights
                    datetime.utcnow().isoformat(),
                    existing[0]
                ))
            else:
                # Create new knowledge entry
                self.cursor.execute('''
                    INSERT INTO knowledge_base 
                    (topic, key_insights, related_prompts, confidence_score, 
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    topic_str,
                    '\n'.join(insights[:10]),
                    prompt,
                    0.7,  # Initial confidence
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                ))
                
            self.conn.commit()
            
    def analyze_patterns(self):
        """Analyze execution patterns for learning"""
        try:
            # Most successful categories
            self.cursor.execute('''
                SELECT category, COUNT(*) as count, AVG(tokens_used) as avg_tokens
                FROM prompts_executed 
                WHERE success = 1
                GROUP BY category
                ORDER BY count DESC
            ''')
            patterns = self.cursor.fetchall()
            
            for category, count, avg_tokens in patterns:
                pattern_data = json.dumps({
                    'category': category,
                    'success_count': count,
                    'avg_tokens': avg_tokens
                })
                
                # Store or update pattern
                self.cursor.execute('''
                    INSERT OR REPLACE INTO learning_patterns 
                    (pattern_type, pattern_data, frequency, last_seen)
                    VALUES (?, ?, ?, ?)
                ''', (
                    'category_success',
                    pattern_data,
                    count,
                    datetime.utcnow().isoformat()
                ))
                
            self.conn.commit()
            logger.info("Pattern analysis complete")
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            
    def generate_report(self) -> str:
        """Generate execution report"""
        try:
            # Get metrics
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(tokens_used) as total_tokens,
                    AVG(execution_time) as avg_time
                FROM prompts_executed
            ''')
            total, successful, total_tokens, avg_time = self.cursor.fetchone()
            
            # Get category breakdown
            self.cursor.execute('''
                SELECT category, COUNT(*) as count
                FROM prompts_executed
                WHERE success = 1
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            ''')
            categories = self.cursor.fetchall()
            
            # Get knowledge entries
            self.cursor.execute('SELECT COUNT(*) FROM knowledge_base')
            knowledge_count = self.cursor.fetchone()[0]
            
            report = f"""
=== EQ12 Prompt Execution Report ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTION METRICS:
- Total Prompts Executed: {total or 0}
- Successful: {successful or 0} ({(successful/total*100 if total else 0):.1f}%)
- Failed: {(total or 0) - (successful or 0)}
- Total Tokens Used: {total_tokens or 0:,}
- Average Execution Time: {avg_time or 0:.2f}s

KNOWLEDGE BASE:
- Total Knowledge Entries: {knowledge_count}

TOP CATEGORIES:
"""
            for category, count in categories:
                report += f"- {category}: {count} prompts\n"
                
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return "Error generating report"
            
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='EQ12 Prompt Executor - FULL SYSTEM CAPABILITIES')
    parser.add_argument('--prompts', default='C:\\EQ12_BROKEN_20251122_210342\\prompts\\chatgpt_prompts_20000_nov2025.txt')
    parser.add_argument('--db', default='C:\\EQ12_BROKEN_20251122_210342\\logs\\prompt_execution.db')
    parser.add_argument('--start', type=int, default=1, help='Start prompt number')
    parser.add_argument('--count', type=int, default=100, help='Number of prompts to execute')
    parser.add_argument('--batch-size', type=int, default=10, help='Batch size before analysis')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between prompts (seconds)')
    parser.add_argument('--parallel', action='store_true', help='Enable parallel processing')
    parser.add_argument('--workers', type=int, default=0, help='Number of parallel workers (0=auto)')
    parser.add_argument('--report-only', action='store_true', help='Generate report only')
    
    args = parser.parse_args()
    
    max_workers = args.workers if args.workers > 0 else min(CPU_COUNT * 2, 16)
    executor = PromptExecutor(args.db, args.prompts, max_workers=max_workers)
    
    if args.report_only:
        print(executor.generate_report())
        executor.close()
        return
        
    # Load prompts
    prompts = executor.load_prompts(args.start, args.count)
    
    if not prompts:
        logger.error("No prompts loaded. Exiting.")
        executor.close()
        return
        
    logger.info(f"Starting execution of {len(prompts)} prompts...")
    logger.info(f"Mode: {'PARALLEL' if args.parallel else 'SEQUENTIAL'}")
    
    if args.parallel:
        # PARALLEL EXECUTION - Full system utilization
        logger.info(f"Using {executor.max_workers} parallel workers")
        
        with ThreadPoolExecutor(max_workers=executor.max_workers) as pool:
            futures = {pool.submit(executor.execute_prompt, prompt): prompt for prompt in prompts}
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                prompt = futures[future]
                try:
                    result = future.result()
                    executor.save_execution(result)
                    
                    if result['success']:
                        executor.extract_knowledge(
                            result['prompt_text'],
                            result['response'],
                            result['category']
                        )
                        cache_status = " [CACHED]" if result.get('cache_hit') else ""
                        logger.info(f"[{completed}/{len(prompts)}] ✓ {prompt['number']}: {result.get('provider', 'Unknown')}{cache_status} ({result['tokens_used']} tokens, {result['execution_time']:.2f}s)")
                    else:
                        logger.warning(f"[{completed}/{len(prompts)}] ✗ {prompt['number']}: {result['error_message']}")
                        
                    # Analyze patterns periodically
                    if completed % args.batch_size == 0:
                        executor.analyze_patterns()
                        logger.info(f"--- Batch {completed//args.batch_size} complete ({completed}/{len(prompts)}) ---")
                        
                except Exception as e:
                    logger.error(f"Error processing prompt {prompt['number']}: {e}")
                    
    else:
        # SEQUENTIAL EXECUTION - With caching
        for i, prompt in enumerate(prompts, start=1):
            logger.info(f"[{i}/{len(prompts)}] Executing: {prompt['text'][:60]}...")
            
            result = executor.execute_prompt(prompt)
            executor.save_execution(result)
            
            if result['success']:
                executor.extract_knowledge(
                    result['prompt_text'],
                    result['response'],
                    result['category']
                )
                cache_status = " [CACHED]" if result.get('cache_hit') else ""
                logger.info(f"✓ {result.get('provider', 'Unknown')}{cache_status} ({result['tokens_used']} tokens, {result['execution_time']:.2f}s)")
            else:
                logger.warning(f"✗ Failed: {result['error_message']}")
                
            # Analyze patterns every batch
            if i % args.batch_size == 0:
                executor.analyze_patterns()
                logger.info(f"--- Batch {i//args.batch_size} complete ---")
                
            # Rate limiting (skip if cached)
            if i < len(prompts) and not result.get('cache_hit'):
                time.sleep(args.delay)
            
    # Final analysis and report
    executor.analyze_patterns()
    print("\n" + executor.generate_report())
    
    # Show cache statistics
    cache_hits = sum(1 for r in executor.cache.values())
    logger.info(f"Cache statistics: {cache_hits} entries in memory")
    
    executor.close()
    logger.info("Execution complete!")


if __name__ == '__main__':
    main()
