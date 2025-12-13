#!/usr/bin/env python3
"""
EQ12 Knowledge Query Tool
Query the learned knowledge base from prompt executions
"""

import sqlite3
import argparse
from datetime import datetime


def query_knowledge(db_path: str, topic: str = None, category: str = None, limit: int = 10):
    """Query knowledge base"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if topic:
        cursor.execute('''
            SELECT topic, key_insights, confidence_score, update_count, updated_at
            FROM knowledge_base
            WHERE topic LIKE ?
            ORDER BY confidence_score DESC, update_count DESC
            LIMIT ?
        ''', (f'%{topic}%', limit))
    elif category:
        cursor.execute('''
            SELECT pe.category, kb.topic, kb.key_insights, kb.confidence_score
            FROM knowledge_base kb
            JOIN prompts_executed pe ON kb.topic LIKE '%' || pe.prompt_text || '%'
            WHERE pe.category = ?
            GROUP BY kb.topic
            LIMIT ?
        ''', (category, limit))
    else:
        cursor.execute('''
            SELECT topic, key_insights, confidence_score, update_count
            FROM knowledge_base
            ORDER BY update_count DESC, confidence_score DESC
            LIMIT ?
        ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def search_responses(db_path: str, keyword: str, limit: int = 10):
    """Search executed prompt responses"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT prompt_text, response, category, timestamp
        FROM prompts_executed
        WHERE response LIKE ? AND success = 1
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (f'%{keyword}%', limit))
    
    results = cursor.fetchall()
    conn.close()
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Query EQ12 Knowledge Base')
    parser.add_argument('--db', default='C:\\EQ12_BROKEN_20251122_210342\\logs\\prompt_execution.db')
    parser.add_argument('--topic', help='Search by topic')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--search', help='Search responses by keyword')
    parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    args = parser.parse_args()
    
    if args.search:
        print(f"\n=== Search Results for '{args.search}' ===\n")
        results = search_responses(args.db, args.search, args.limit)
        
        for i, (prompt, response, category, timestamp) in enumerate(results, 1):
            print(f"{i}. [{category}] {prompt}")
            print(f"   Response: {response[:200]}...")
            print(f"   Time: {timestamp}\n")
            
    else:
        print(f"\n=== Knowledge Base Query ===\n")
        results = query_knowledge(args.db, args.topic, args.category, args.limit)
        
        for i, row in enumerate(results, 1):
            if len(row) >= 4:
                topic, insights, score = row[0], row[1], row[2]
                print(f"{i}. Topic: {topic}")
                try:
                    print(f"   Confidence: {float(score):.2f}")
                except (ValueError, TypeError):
                    print(f"   Confidence: {score}")
                print(f"   Insights:\n   {insights[:300]}...")
                print()


if __name__ == '__main__':
    main()
