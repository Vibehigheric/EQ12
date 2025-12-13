#!/usr/bin/env python3
"""
EQ12 Automated Learning Pipeline
Continuous learning system that auto-generates new prompts from successful patterns
Closes the feedback loop: Execute → Learn → Generate → Optimize
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import json
import os
from collections import Counter
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class LearningPipeline:
    """Automated continuous learning pipeline"""
    
    def __init__(self, db_path: str, output_dir: str):
        self.db_path = db_path
        self.output_dir = output_dir
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
    def analyze_recent_success_patterns(self, hours: int = 24) -> Dict:
        """Analyze patterns from recent successful executions"""
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')
        
        self.cursor.execute('''
            SELECT 
                category,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence,
                AVG(execution_time) as avg_time,
                SUM(tokens_used) as total_tokens
            FROM prompts_executed pe
            LEFT JOIN knowledge_base kb ON pe.prompt_number IN (
                SELECT CAST(value AS INTEGER) 
                FROM knowledge_base, json_each(related_prompts)
            )
            WHERE pe.success = 1 
            AND pe.timestamp >= ?
            GROUP BY category
            HAVING count >= 3
            ORDER BY avg_confidence DESC, count DESC
        ''', (cutoff_str,))
        
        patterns = {}
        for row in self.cursor.fetchall():
            category, count, avg_conf, avg_time, tokens = row
            if category:
                patterns[category] = {
                    'count': count,
                    'avg_confidence': avg_conf or 0,
                    'avg_execution_time': avg_time or 0,
                    'total_tokens': tokens or 0,
                    'success_rate': 100.0  # Already filtered for success=1
                }
        
        return patterns
        
    def identify_knowledge_gaps(self) -> List[str]:
        """Identify topics with low knowledge coverage"""
        self.cursor.execute('''
            SELECT DISTINCT category
            FROM prompts_executed
            WHERE category IS NOT NULL
        ''')
        
        all_categories = {row[0] for row in self.cursor.fetchall()}
        
        self.cursor.execute('''
            SELECT DISTINCT pe.category
            FROM knowledge_base kb
            JOIN prompts_executed pe ON kb.related_prompts LIKE '%' || pe.prompt_number || '%'
            WHERE kb.confidence_score >= 0.7
        ''')
        
        covered_categories = {row[0] for row in self.cursor.fetchall()}
        
        gaps = list(all_categories - covered_categories)
        
        logger.info(f"Identified {len(gaps)} knowledge gaps: {gaps}")
        return gaps
        
    def generate_prompts_for_gaps(self, gaps: List[str], count_per_gap: int = 20) -> Dict[str, List[str]]:
        """Generate new prompts targeting knowledge gaps"""
        generated = {}
        
        for gap in gaps:
            logger.info(f"Generating {count_per_gap} prompts for gap: {gap}")
            
            # Call prompt generator for this category
            cmd = [
                'python',
                'scripts/eq12_prompt_generator.py',
                '--db', self.db_path,
                '--count', str(count_per_gap),
                '--category', gap,
                '--output', os.path.join(self.output_dir, f'gap_prompts_{gap}.txt')
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(f"Generated prompts for {gap}")
                
                # Read generated prompts
                output_file = os.path.join(self.output_dir, f'gap_prompts_{gap}.txt')
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        prompts = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    generated[gap] = prompts
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to generate prompts for {gap}: {e}")
        
        return generated
        
    def optimize_successful_prompts(self) -> List[Dict]:
        """Find and optimize highly successful prompts for variations"""
        self.cursor.execute('''
            SELECT 
                pe.prompt_text,
                pe.category,
                kb.confidence_score,
                kb.key_insights
            FROM prompts_executed pe
            JOIN knowledge_base kb ON kb.related_prompts LIKE '%' || pe.prompt_number || '%'
            WHERE pe.success = 1
            AND kb.confidence_score >= 0.85
            ORDER BY kb.confidence_score DESC
            LIMIT 20
        ''')
        
        successful_prompts = []
        for row in self.cursor.fetchall():
            successful_prompts.append({
                'prompt': row[0],
                'category': row[1],
                'confidence': row[2],
                'insights': row[3]
            })
        
        logger.info(f"Identified {len(successful_prompts)} highly successful prompts for optimization")
        return successful_prompts
        
    def run_learning_cycle(self) -> Dict:
        """Execute complete learning cycle"""
        logger.info("=== Starting Learning Cycle ===")
        
        cycle_report = {
            'timestamp': datetime.now().isoformat(),
            'steps': {}
        }
        
        # Step 1: Analyze recent patterns
        logger.info("Step 1: Analyzing recent success patterns...")
        patterns = self.analyze_recent_success_patterns(hours=24)
        cycle_report['steps']['patterns_analyzed'] = len(patterns)
        cycle_report['patterns'] = patterns
        
        # Step 2: Identify knowledge gaps
        logger.info("Step 2: Identifying knowledge gaps...")
        gaps = self.identify_knowledge_gaps()
        cycle_report['steps']['gaps_identified'] = len(gaps)
        cycle_report['gaps'] = gaps
        
        # Step 3: Generate prompts for gaps
        logger.info("Step 3: Generating prompts for knowledge gaps...")
        if gaps:
            generated = self.generate_prompts_for_gaps(gaps[:5], count_per_gap=15)  # Top 5 gaps
            cycle_report['steps']['prompts_generated'] = sum(len(p) for p in generated.values())
            cycle_report['generated_prompts'] = {k: len(v) for k, v in generated.items()}
        else:
            cycle_report['steps']['prompts_generated'] = 0
            logger.info("No knowledge gaps to fill")
        
        # Step 4: Optimize successful prompts
        logger.info("Step 4: Optimizing successful prompts...")
        successful = self.optimize_successful_prompts()
        cycle_report['steps']['successful_prompts_found'] = len(successful)
        cycle_report['top_successful'] = [
            {'prompt': s['prompt'][:80] + '...', 'confidence': s['confidence']}
            for s in successful[:5]
        ]
        
        # Save cycle report
        report_file = os.path.join(
            self.output_dir,
            f'learning_cycle_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(cycle_report, f, indent=2)
        
        logger.info(f"Learning cycle report saved to: {report_file}")
        logger.info("=== Learning Cycle Complete ===")
        
        return cycle_report
        
    def print_cycle_summary(self, report: Dict):
        """Print human-readable cycle summary"""
        print("\n" + "=" * 70)
        print("EQ12 Learning Cycle Summary")
        print("=" * 70)
        print(f"Timestamp: {report['timestamp']}")
        print()
        
        print("Steps Completed:")
        for step, value in report['steps'].items():
            print(f"  • {step.replace('_', ' ').title()}: {value}")
        print()
        
        if report.get('patterns'):
            print("Top Success Patterns:")
            for category, data in sorted(report['patterns'].items(), 
                                        key=lambda x: x[1]['avg_confidence'], 
                                        reverse=True)[:5]:
                print(f"  • {category}: {data['count']} prompts, "
                      f"{data['avg_confidence']:.2%} confidence")
            print()
        
        if report.get('gaps'):
            print(f"Knowledge Gaps Identified: {len(report['gaps'])}")
            for gap in report['gaps'][:5]:
                print(f"  • {gap}")
            print()
        
        if report.get('top_successful'):
            print("Top Performing Prompts:")
            for i, prompt_data in enumerate(report['top_successful'], 1):
                print(f"  {i}. {prompt_data['prompt']}")
                print(f"     Confidence: {prompt_data['confidence']:.2%}")
            print()
        
        print("=" * 70)
        
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='EQ12 Automated Learning Pipeline')
    parser.add_argument('--db', default='C:\\EQ12_BROKEN_20251122_210342\\logs\\prompt_execution.db',
                       help='Path to prompt execution database')
    parser.add_argument('--output-dir', default='C:\\EQ12_BROKEN_20251122_210342\\logs\\learning_cycles',
                       help='Output directory for learning cycle reports')
    parser.add_argument('--continuous', action='store_true',
                       help='Run in continuous mode (loop every N hours)')
    parser.add_argument('--interval', type=int, default=6,
                       help='Hours between learning cycles in continuous mode')
    
    args = parser.parse_args()
    
    pipeline = LearningPipeline(args.db, args.output_dir)
    
    if args.continuous:
        import time
        
        logger.info(f"Starting continuous learning mode (interval: {args.interval} hours)")
        
        while True:
            try:
                report = pipeline.run_learning_cycle()
                pipeline.print_cycle_summary(report)
                
                logger.info(f"Sleeping for {args.interval} hours...")
                time.sleep(args.interval * 3600)
                
            except KeyboardInterrupt:
                logger.info("Continuous mode interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in learning cycle: {e}")
                time.sleep(300)  # Sleep 5 minutes on error
    else:
        report = pipeline.run_learning_cycle()
        pipeline.print_cycle_summary(report)
    
    pipeline.close()


if __name__ == '__main__':
    main()
