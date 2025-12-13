#!/usr/bin/env python3
"""
EQ12 Multi-Provider AI Router
Intelligent routing between OpenAI, Claude, Groq based on prompt characteristics
Optimizes for cost, speed, and quality based on prompt type
"""

import os
import logging
from typing import Dict, Optional, Tuple
from enum import Enum
import re
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class Provider(Enum):
    """AI provider options"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GROQ = "groq"
    OPENROUTER = "openrouter"


@dataclass
class ProviderConfig:
    """Provider configuration"""
    name: str
    cost_per_1k_tokens: float
    speed_score: int  # 1-10, higher is faster
    quality_score: int  # 1-10, higher is better
    max_tokens: int
    best_for: list


class AIRouter:
    """Route prompts to optimal AI provider"""
    
    PROVIDERS = {
        Provider.GROQ: ProviderConfig(
            name="Groq (LLaMA3-70B)",
            cost_per_1k_tokens=0.0005,  # Very cheap
            speed_score=10,  # Extremely fast
            quality_score=7,  # Good quality
            max_tokens=8000,
            best_for=["simple", "fast", "batch", "classification"]
        ),
        Provider.OPENAI: ProviderConfig(
            name="OpenAI (GPT-4o-mini)",
            cost_per_1k_tokens=0.002,  # Moderate
            speed_score=8,  # Fast
            quality_score=9,  # Excellent
            max_tokens=16000,
            best_for=["analysis", "coding", "structured", "reasoning"]
        ),
        Provider.CLAUDE: ProviderConfig(
            name="Claude (Sonnet 3.5)",
            cost_per_1k_tokens=0.003,  # Higher cost
            speed_score=7,  # Good speed
            quality_score=10,  # Best quality
            max_tokens=200000,  # Huge context
            best_for=["complex", "creative", "long_context", "expert"]
        ),
        Provider.OPENROUTER: ProviderConfig(
            name="OpenRouter (Multiple models)",
            cost_per_1k_tokens=0.001,  # Variable
            speed_score=8,
            quality_score=8,
            max_tokens=32000,
            best_for=["fallback", "diverse", "experimental"]
        )
    }
    
    def __init__(self, prefer_speed: bool = False, prefer_cost: bool = False):
        self.prefer_speed = prefer_speed
        self.prefer_cost = prefer_cost
        self.stats = {
            'total_routed': 0,
            'by_provider': {p.value: 0 for p in Provider}
        }
        
    def classify_prompt(self, prompt: str) -> Dict[str, any]:
        """Classify prompt characteristics"""
        prompt_lower = prompt.lower()
        
        # Estimate complexity
        word_count = len(prompt.split())
        has_code = any(word in prompt_lower for word in ['code', 'function', 'class', 'script', 'program'])
        has_analysis = any(word in prompt_lower for word in ['analyze', 'compare', 'evaluate', 'assess'])
        has_creative = any(word in prompt_lower for word in ['write', 'create', 'design', 'generate', 'compose'])
        is_simple = any(word in prompt_lower for word in ['what is', 'define', 'list', 'name'])
        needs_reasoning = any(word in prompt_lower for word in ['why', 'how does', 'explain', 'reasoning'])
        
        # Classify
        if is_simple and word_count < 20:
            complexity = "simple"
        elif has_code or has_analysis or needs_reasoning:
            complexity = "complex"
        elif has_creative and word_count > 30:
            complexity = "creative"
        else:
            complexity = "moderate"
        
        # Estimate required tokens
        estimated_tokens = word_count * 1.5  # Rough estimate
        
        return {
            'complexity': complexity,
            'word_count': word_count,
            'estimated_tokens': estimated_tokens,
            'has_code': has_code,
            'has_analysis': has_analysis,
            'has_creative': has_creative,
            'is_simple': is_simple,
            'needs_reasoning': needs_reasoning
        }
        
    def route_prompt(self, prompt: str, category: str = None) -> Tuple[Provider, str]:
        """Route prompt to optimal provider"""
        classification = self.classify_prompt(prompt)
        
        # Default routing logic
        provider = self._select_provider(classification, category)
        
        self.stats['total_routed'] += 1
        self.stats['by_provider'][provider.value] += 1
        
        reasoning = self._explain_routing(provider, classification)
        
        logger.info(f"Routed to {provider.value}: {reasoning}")
        
        return provider, reasoning
        
    def _select_provider(self, classification: Dict, category: str = None) -> Provider:
        """Select best provider based on classification"""
        
        # Speed priority
        if self.prefer_speed:
            if classification['complexity'] == "simple":
                return Provider.GROQ
            else:
                return Provider.OPENAI
        
        # Cost priority
        if self.prefer_cost:
            if classification['complexity'] in ["simple", "moderate"]:
                return Provider.GROQ
            else:
                return Provider.OPENROUTER
        
        # Quality-optimized routing (default)
        if classification['complexity'] == "simple":
            return Provider.GROQ  # Fast and cheap for simple
            
        elif classification['has_code']:
            return Provider.OPENAI  # Best for code
            
        elif classification['complexity'] == "creative":
            return Provider.CLAUDE  # Best for creative
            
        elif classification['needs_reasoning'] or classification['has_analysis']:
            if classification['word_count'] > 100:
                return Provider.CLAUDE  # Long reasoning
            else:
                return Provider.OPENAI  # Short reasoning
                
        elif classification['estimated_tokens'] > 10000:
            return Provider.CLAUDE  # Large context
            
        else:
            return Provider.OPENAI  # Default balanced choice
            
    def _explain_routing(self, provider: Provider, classification: Dict) -> str:
        """Explain why provider was selected"""
        config = self.PROVIDERS[provider]
        reasons = []
        
        if classification['complexity'] == "simple" and provider == Provider.GROQ:
            reasons.append("simple prompt → fast/cheap Groq")
        elif classification['has_code'] and provider == Provider.OPENAI:
            reasons.append("code task → OpenAI GPT-4")
        elif classification['complexity'] == "creative" and provider == Provider.CLAUDE:
            reasons.append("creative task → Claude")
        elif classification['needs_reasoning'] and provider == Provider.CLAUDE:
            reasons.append("complex reasoning → Claude")
        elif classification['estimated_tokens'] > 10000 and provider == Provider.CLAUDE:
            reasons.append("large context → Claude")
        else:
            reasons.append(f"balanced choice → {config.name}")
        
        return "; ".join(reasons)
        
    def get_provider_stats(self) -> Dict:
        """Get routing statistics"""
        stats = self.stats.copy()
        
        if stats['total_routed'] > 0:
            stats['distribution'] = {
                p: (count / stats['total_routed'] * 100)
                for p, count in stats['by_provider'].items()
            }
        else:
            stats['distribution'] = {}
        
        return stats
        
    def estimate_cost(self, provider: Provider, tokens: int) -> float:
        """Estimate cost for provider and token count"""
        config = self.PROVIDERS[provider]
        return (tokens / 1000) * config.cost_per_1k_tokens


# Example usage
if __name__ == '__main__':
    router = AIRouter()
    
    test_prompts = [
        "What is Python?",
        "Write a comprehensive analysis of machine learning trends in 2026",
        "Create a Python function to calculate Fibonacci numbers",
        "Explain quantum computing to a beginner",
        "Write a creative story about AI and humanity",
        "How to optimize database queries for performance"
    ]
    
    print("\n=== AI Router Test ===\n")
    
    for prompt in test_prompts:
        provider, reasoning = router.route_prompt(prompt)
        print(f"Prompt: {prompt[:60]}...")
        print(f"→ {provider.value.upper()}: {reasoning}\n")
    
    print("\n=== Routing Statistics ===\n")
    stats = router.get_provider_stats()
    print(f"Total Prompts Routed: {stats['total_routed']}")
    print("\nDistribution:")
    for provider, percentage in stats['distribution'].items():
        print(f"  {provider}: {percentage:.1f}%")
