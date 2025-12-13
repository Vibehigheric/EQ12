#!/usr/bin/env python3
"""
EQ12 Knowledge Synthesizer
Analyzes knowledge base across categories to generate expert insights
Automatically synthesizes learnings and identifies patterns
"""

import sqlite3
import argparse
import logging
from datetime import datetime
from typing import List, Dict
import json
from collections import defaultdict
import re

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class KnowledgeSynthesizer:
    """Synthesize insights from knowledge base"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def get_knowledge_stats(self) -> Dict:
        """Get overall knowledge base statistics"""
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total_entries,
                AVG(confidence_score) as avg_confidence,
                COUNT(DISTINCT topic) as unique_topics,
                SUM(update_count) as total_updates
            FROM knowledge_base
        ''')
        
        row = self.cursor.fetchone()
        return {
            'total_entries': row[0],
            'avg_confidence': row[1] or 0,
            'unique_topics': row[2],
            'total_updates': row[3] or 0
        }
        
    def synthesize_by_category(self) -> Dict[str, List[Dict]]:
        """Synthesize insights grouped by category"""
        self.cursor.execute('''
            SELECT 
                pe.category,
                kb.topic,
                kb.key_insights,
                kb.confidence_score,
                COUNT(DISTINCT pe.prompt_number) as prompt_count,
                AVG(pe.execution_time) as avg_exec_time,
                SUM(pe.tokens_used) as total_tokens
            FROM knowledge_base kb
            JOIN prompts_executed pe ON kb.related_prompts LIKE '%' || pe.prompt_number || '%'
            WHERE pe.category IS NOT NULL
            GROUP BY pe.category, kb.topic
            ORDER BY pe.category, kb.confidence_score DESC
        ''')
        
        synthesis = defaultdict(list)
        
        for row in self.cursor.fetchall():
            category, topic, insights, confidence, prompt_count, avg_time, tokens = row
            
            synthesis[category].append({
                'topic': topic,
                'insights': insights,
                'confidence': confidence,
                'prompt_count': prompt_count,
                'avg_execution_time': avg_time,
                'total_tokens': tokens
            })
        
        return dict(synthesis)
        
    def identify_high_confidence_insights(self, min_confidence: float = 0.80) -> List[Dict]:
        """Get high-confidence knowledge entries"""
        self.cursor.execute('''
            SELECT topic, key_insights, confidence_score, update_count, created_at
            FROM knowledge_base
            WHERE confidence_score >= ?
            ORDER BY confidence_score DESC, update_count DESC
        ''', (min_confidence,))
        
        insights = []
        for row in self.cursor.fetchall():
            insights.append({
                'topic': row[0],
                'insights': row[1],
                'confidence': row[2],
                'updates': row[3],
                'created': row[4]
            })
        
        return insights
        
    def cross_reference_topics(self) -> List[Dict]:
        """Find topics that appear across multiple categories"""
        self.cursor.execute('''
            SELECT 
                kb.topic,
                GROUP_CONCAT(DISTINCT pe.category) as categories,
                COUNT(DISTINCT pe.category) as category_count,
                AVG(kb.confidence_score) as avg_confidence
            FROM knowledge_base kb
            JOIN prompts_executed pe ON kb.related_prompts LIKE '%' || pe.prompt_number || '%'
            WHERE pe.category IS NOT NULL
            GROUP BY kb.topic
            HAVING category_count > 1
            ORDER BY category_count DESC, avg_confidence DESC
        ''')
        
        cross_refs = []
        for row in self.cursor.fetchall():
            cross_refs.append({
                'topic': row[0],
                'categories': row[1].split(',') if row[1] else [],
                'category_count': row[2],
                'avg_confidence': row[3]
            })
        
        return cross_refs
        
    def generate_synthesis_report(self) -> str:
        """Generate comprehensive synthesis report"""
        report = []
        report.append("=" * 70)
        report.append("EQ12 Knowledge Synthesis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")
        
        # Overall stats
        stats = self.get_knowledge_stats()
        report.append("OVERALL STATISTICS")
        report.append("-" * 70)
        report.append(f"Total Knowledge Entries: {stats['total_entries']:,}")
        report.append(f"Average Confidence: {stats['avg_confidence']:.2%}")
        report.append(f"Unique Topics: {stats['unique_topics']:,}")
        report.append(f"Total Updates: {stats['total_updates']:,}")
        report.append("")
        
        # High-confidence insights
        high_conf = self.identify_high_confidence_insights(0.75)
        report.append(f"HIGH-CONFIDENCE INSIGHTS (>75%)")
        report.append("-" * 70)
        for i, insight in enumerate(high_conf[:10], 1):
            report.append(f"{i}. {insight['topic']} (Confidence: {insight['confidence']:.2%})")
            report.append(f"   {insight['insights'][:150]}...")
            report.append(f"   Updates: {insight['updates']}")
            report.append("")
        
        # Category synthesis
        by_category = self.synthesize_by_category()
        report.append("INSIGHTS BY CATEGORY")
        report.append("-" * 70)
        for category, insights in sorted(by_category.items()):
            report.append(f"\n{category.upper()}")
            report.append(f"  Insights: {len(insights)}")
            
            if insights:
                top_insight = insights[0]
                report.append(f"  Top Topic: {top_insight['topic']}")
                report.append(f"  Confidence: {top_insight['confidence']:.2%}")
                report.append(f"  Prompts: {top_insight['prompt_count']}")
        
        report.append("")
        
        # Cross-references
        cross_refs = self.cross_reference_topics()
        if cross_refs:
            report.append("CROSS-CATEGORY TOPICS")
            report.append("-" * 70)
            for ref in cross_refs[:10]:
                report.append(f"{ref['topic']}")
                report.append(f"  Categories: {', '.join(ref['categories'])}")
                report.append(f"  Confidence: {ref['avg_confidence']:.2%}")
                report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)
        
    def export_synthesis_json(self) -> Dict:
        """Export synthesis as structured JSON"""
        return {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'database': self.db_path
            },
            'statistics': self.get_knowledge_stats(),
            'high_confidence_insights': self.identify_high_confidence_insights(0.75),
            'category_synthesis': self.synthesize_by_category(),
            'cross_references': self.cross_reference_topics()
        }
        
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='EQ12 Knowledge Synthesizer')
    parser.add_argument('--db', default='C:\\EQ12_BROKEN_20251122_210342\\logs\\prompt_execution.db',
                       help='Path to prompt execution database')
    parser.add_argument('--output', help='Output file for synthesis report')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    parser.add_argument('--min-confidence', type=float, default=0.75,
                       help='Minimum confidence for high-confidence insights')
    
    args = parser.parse_args()
    
    synthesizer = KnowledgeSynthesizer(args.db)
    
    if args.format == 'json':
        synthesis = synthesizer.export_synthesis_json()
        output = json.dumps(synthesis, indent=2)
    else:
        output = synthesizer.generate_synthesis_report()
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Synthesis report saved to: {args.output}")
    else:
        print(output)
    
    synthesizer.close()


if __name__ == '__main__':
    main()
