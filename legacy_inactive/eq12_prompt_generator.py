#!/usr/bin/env python3
"""
EQ12 Intelligent Prompt Generator
Generates new prompts based on learned patterns from executed prompt database
Uses ML to identify successful patterns and create variations
"""

import sqlite3
import argparse
import logging
from datetime import datetime
from typing import List, Dict, Tuple
import json
import random
from collections import Counter, defaultdict
import re

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class PromptGenerator:
    """Generate new prompts based on learned patterns"""
    
    # Prompt templates extracted from analysis
    TEMPLATES = [
        "How to {verb} {topic} for {audience}",
        "What are {number} tips for mastering {topic}?",
        "Explain {topic} to a {level}",
        "Create a comprehensive strategy for {topic}",
        "How can businesses leverage {topic}?",
        "Write a persuasive essay about {topic}",
        "What are the pros and cons of {topic}?",
        "How to overcome challenges in {topic}",
        "What tools are best for {topic}?",
        "Compare and contrast {topic1} with {topic2}",
        "What are the latest trends in {topic}?",
        "How does {topic} impact {domain}?",
        "Create a step-by-step guide for {topic}",
        "What certifications exist for {topic}?",
        "How to build a career in {topic}",
        "Write a market analysis of {topic}",
        "What role does {topic} play in innovation?",
        "How to monetize {topic}",
        "What are common mistakes in {topic}?",
        "Analyze the impact of {topic} on society",
        "How to teach {topic} to {audience}",
        "What are the cost considerations of {topic}?",
        "Create a weekly plan for {topic}",
        "How to measure success in {topic}",
        "What are the legal aspects of {topic}?",
        "Write a troubleshooting guide for {topic}",
        "How to automate {topic}",
        "What are the psychological benefits of {topic}?",
        "Create a beginner to advanced roadmap for {topic}",
        "How does {topic} affect different age groups?",
        "How to stay updated on {topic}",
        "What are the environmental impacts of {topic}?",
        "Create a resource list for {topic}",
        "Write interview questions about {topic}",
        "How does {topic} compare globally?",
        "How to design {topic} for {context}",
        "How to implement {topic} for {audience}",
        "How to optimize {topic} for {goal}",
        "How to troubleshoot {topic} for {audience}",
        "How to develop {topic} for {context}",
        "How to improve {topic} for {audience}",
        "How to master {topic} for {level}",
        "How to understand {topic} for {audience}",
        "How to leverage {topic} for {goal}",
    ]
    
    VERBS = [
        "analyze", "review", "compare", "optimize", "troubleshoot",
        "implement", "design", "create", "build", "develop",
        "improve", "master", "understand", "leverage", "explain"
    ]
    
    AUDIENCES = [
        "beginners", "experts", "businesses", "students", "professionals",
        "developers", "entrepreneurs", "remote workers", "investors",
        "content creators", "marketers", "passive income seekers"
    ]
    
    CONTEXTS = [
        "2026", "with AI", "on a budget", "for passive income",
        "in business", "for education", "for innovation"
    ]
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.learned_topics = set()
        self.learned_patterns = defaultdict(list)
        self.topic_categories = defaultdict(list)
        self.analyze_existing_prompts()
        
    def analyze_existing_prompts(self):
        """Analyze existing prompts to learn patterns"""
        logger.info("Analyzing existing prompt patterns...")
        
        self.cursor.execute('''
            SELECT prompt_text, category, response 
            FROM prompts_executed 
            WHERE success = 1
            LIMIT 10000
        ''')
        
        prompts = self.cursor.fetchall()
        logger.info(f"Analyzing {len(prompts)} successful prompts")
        
        for prompt_text, category, response in prompts:
            # Extract topics (words after "about", "for", "in", "of")
            topics = self.extract_topics(prompt_text)
            self.learned_topics.update(topics)
            
            # Categorize topics
            if category:
                self.topic_categories[category].extend(topics)
            
            # Extract patterns
            pattern = self.extract_pattern(prompt_text)
            if pattern:
                self.learned_patterns[pattern].append(prompt_text)
        
        logger.info(f"Learned {len(self.learned_topics)} unique topics")
        logger.info(f"Identified {len(self.learned_patterns)} patterns")
        logger.info(f"Categories: {len(self.topic_categories)}")
        
    def extract_topics(self, text: str) -> List[str]:
        """Extract topics from prompt text"""
        topics = []
        
        # Match patterns like "... about X", "... for X", "... in X"
        patterns = [
            r'about (.+?)(?:\?|$|\s+for|\s+in|\s+with)',
            r'for (.+?)(?:\?|$|\s+in|\s+with)',
            r'in (.+?)(?:\?|$)',
            r'of (.+?)(?:\?|$)',
            r'(?:How|What|Why|When|Where) (?:to|does|are|is) (.+?)(?:\?|$| for| in| with)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            topics.extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        return topics[:3]  # Return top 3 topics
        
    def extract_pattern(self, text: str) -> str:
        """Extract structural pattern from prompt"""
        # Normalize to pattern template
        text_lower = text.lower()
        
        if text_lower.startswith("how to"):
            return "how_to"
        elif text_lower.startswith("what are"):
            return "what_are"
        elif text_lower.startswith("explain"):
            return "explain"
        elif text_lower.startswith("create"):
            return "create"
        elif text_lower.startswith("write"):
            return "write"
        elif text_lower.startswith("compare"):
            return "compare"
        elif text_lower.startswith("analyze"):
            return "analyze"
        else:
            return "general"
            
    def generate_prompts(self, count: int = 100, category: str = None) -> List[str]:
        """Generate new prompts based on learned patterns"""
        logger.info(f"Generating {count} new prompts...")
        
        generated = []
        topics_list = list(self.learned_topics)
        
        # Get category-specific topics if requested
        if category and category in self.topic_categories:
            topics_list = list(set(self.topic_categories[category]))
            logger.info(f"Using {len(topics_list)} topics from category: {category}")
        
        if not topics_list:
            topics_list = list(self.learned_topics)
        
        for _ in range(count):
            template = random.choice(self.TEMPLATES)
            
            # Fill template variables
            prompt = template
            
            if "{verb}" in prompt:
                prompt = prompt.replace("{verb}", random.choice(self.VERBS))
            
            if "{topic}" in prompt:
                topic = random.choice(topics_list) if topics_list else "innovation"
                prompt = prompt.replace("{topic}", topic)
                
            if "{topic1}" in prompt:
                topic1 = random.choice(topics_list) if topics_list else "AI"
                prompt = prompt.replace("{topic1}", topic1)
                
            if "{topic2}" in prompt:
                remaining_topics = [t for t in topics_list if t != topic1] if topics_list else ["blockchain"]
                topic2 = random.choice(remaining_topics) if remaining_topics else "cloud computing"
                prompt = prompt.replace("{topic2}", topic2)
            
            if "{audience}" in prompt:
                prompt = prompt.replace("{audience}", random.choice(self.AUDIENCES))
            
            if "{level}" in prompt:
                prompt = prompt.replace("{level}", random.choice(["beginner", "expert", "intermediate"]))
                
            if "{number}" in prompt:
                prompt = prompt.replace("{number}", str(random.choice([3, 5, 7, 10, 15, 20])))
                
            if "{context}" in prompt:
                prompt = prompt.replace("{context}", random.choice(self.CONTEXTS))
                
            if "{domain}" in prompt:
                prompt = prompt.replace("{domain}", random.choice([
                    "business", "education", "healthcare", "technology",
                    "entertainment", "finance", "sustainability"
                ]))
                
            if "{goal}" in prompt:
                prompt = prompt.replace("{goal}", random.choice([
                    "productivity", "growth", "efficiency", "innovation",
                    "scalability", "performance", "security"
                ]))
            
            # Ensure prompt ends with question mark if appropriate
            if prompt.startswith(("How", "What", "Why", "When", "Where")) and not prompt.endswith("?"):
                prompt += "?"
            
            generated.append(prompt)
        
        # Remove duplicates while preserving order
        generated = list(dict.fromkeys(generated))
        
        logger.info(f"Generated {len(generated)} unique prompts")
        return generated
        
    def save_generated_prompts(self, prompts: List[str], output_file: str):
        """Save generated prompts to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# EQ12 Generated Prompts - {timestamp}\n")
            f.write(f"# Total: {len(prompts)} prompts\n")
            f.write(f"# Generated from learned patterns in prompt execution database\n\n")
            
            for i, prompt in enumerate(prompts, 1):
                f.write(f"{i}. {prompt}\n")
        
        logger.info(f"Saved {len(prompts)} prompts to {output_file}")
        
    def analyze_prompt_quality(self) -> Dict:
        """Analyze quality metrics from executed prompts"""
        self.cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                AVG(execution_time) as avg_time,
                SUM(tokens_used) as total_tokens,
                COUNT(DISTINCT category) as categories
            FROM prompts_executed
        ''')
        
        row = self.cursor.fetchone()
        
        metrics = {
            'total_prompts': row[0],
            'successful': row[1],
            'success_rate': (row[1] / row[0] * 100) if row[0] > 0 else 0,
            'avg_execution_time': row[2] or 0,
            'total_tokens': row[3] or 0,
            'unique_categories': row[4]
        }
        
        return metrics
        
    def get_top_topics(self, limit: int = 20) -> List[Tuple[str, int]]:
        """Get most frequently occurring topics"""
        topic_counter = Counter()
        
        for topics in self.topic_categories.values():
            topic_counter.update(topics)
        
        return topic_counter.most_common(limit)
        
    def close(self):
        """Close database connection"""
        self.conn.close()


def main():
    parser = argparse.ArgumentParser(description='EQ12 Prompt Generator')
    parser.add_argument('--db', default='C:\\EQ12_BROKEN_20251122_210342\\logs\\prompt_execution.db',
                       help='Path to prompt execution database')
    parser.add_argument('--count', type=int, default=100,
                       help='Number of prompts to generate')
    parser.add_argument('--category', help='Generate prompts for specific category')
    parser.add_argument('--output', default='C:\\EQ12_BROKEN_20251122_210342\\prompts\\generated_prompts.txt',
                       help='Output file for generated prompts')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze prompt quality metrics')
    parser.add_argument('--top-topics', type=int, help='Show top N topics')
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = PromptGenerator(args.db)
    
    if args.analyze:
        print("\n=== Prompt Quality Analysis ===\n")
        metrics = generator.analyze_prompt_quality()
        print(f"Total Prompts Executed: {metrics['total_prompts']:,}")
        print(f"Successful Executions: {metrics['successful']:,}")
        print(f"Success Rate: {metrics['success_rate']:.1f}%")
        print(f"Avg Execution Time: {metrics['avg_execution_time']:.2f}s")
        print(f"Total Tokens Used: {metrics['total_tokens']:,}")
        print(f"Unique Categories: {metrics['unique_categories']}")
        print()
        
    if args.top_topics:
        print(f"\n=== Top {args.top_topics} Topics ===\n")
        top_topics = generator.get_top_topics(args.top_topics)
        for i, (topic, count) in enumerate(top_topics, 1):
            print(f"{i:2d}. {topic:30s} ({count:,} occurrences)")
        print()
        
    # Generate prompts
    prompts = generator.generate_prompts(args.count, args.category)
    
    # Preview
    print(f"\n=== Generated {len(prompts)} Prompts ===\n")
    print("Preview (first 10):")
    for i, prompt in enumerate(prompts[:10], 1):
        print(f"{i}. {prompt}")
    print()
    
    # Save
    generator.save_generated_prompts(prompts, args.output)
    print(f"\nSaved to: {args.output}")
    
    # Cleanup
    generator.close()
    
    print(f"\n✅ Generation complete!")
    print(f"   - {len(prompts)} unique prompts")
    print(f"   - Based on {len(generator.learned_topics)} learned topics")
    print(f"   - Using {len(generator.learned_patterns)} patterns")


if __name__ == '__main__':
    main()
