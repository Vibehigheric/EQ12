#!/usr/bin/env python3
"""
EQ12 LEGAL PROMPT EXECUTOR
Integrates 1,000 legal/PACER prompts with OpenAI API
Powers credit dispute generation, motion templates, case analysis
Created: November 28, 2025
"""

import logging
import json
import sqlite3
import asyncio
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI library not installed. Run: pip install openai")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/EQ12/logs/legal_prompt_executor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('EQ12_LEGAL_PROMPTS')


class LegalPromptExecutor:
    """
    Legal document generation powered by 1,000 specialized PACER/legal prompts
    Integrates with OpenAI API for automated credit disputes, motions, case analysis
    """
    
    def __init__(self, workspace_path: str = "C:/EQ12"):
        self.workspace_path = Path(workspace_path)
        self.prompts_file = Path("C:/EQ12_BROKEN_20251122_210342/prompts/legal_pacer_prompts_1000.txt")
        self.db_path = self.workspace_path / "data" / "legal_documents.db"
        self.output_path = self.workspace_path / "legal_output"
        
        # Multi-provider AI configuration with fallback
        self.ai_providers = self._setup_ai_providers()
        self.primary_provider = self._select_primary_provider()
        
        if self.primary_provider:
            logger.info(f"✅ Primary AI provider: {self.primary_provider}")
        else:
            logger.warning("⚠️  No AI providers configured")
        
        # Prompt categories and ranges
        self.prompt_categories = {
            'credit_disputes': {'start': 1, 'end': 200, 'description': 'Credit Dispute & FCRA'},
            'case_analysis': {'start': 201, 'end': 400, 'description': 'PACER Case Analysis'},
            'motion_templates': {'start': 401, 'end': 550, 'description': 'Legal Motion Templates'},
            'debt_collection': {'start': 551, 'end': 700, 'description': 'Debt Collection Litigation'},
            'judge_intelligence': {'start': 701, 'end': 800, 'description': 'Judge & Attorney Intelligence'},
            'legal_research': {'start': 801, 'end': 900, 'description': 'Legal Research & Case Law'},
            'compliance': {'start': 901, 'end': 950, 'description': 'Compliance & Regulatory'},
            'business_intelligence': {'start': 951, 'end': 1000, 'description': 'Business Intelligence & Analytics'}
        }
        
        # Create directories
        self.output_path.mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "logs").mkdir(parents=True, exist_ok=True)
        (self.workspace_path / "data").mkdir(parents=True, exist_ok=True)
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        logger.info(f"✅ Legal Prompt Executor initialized with {len(self.prompts)} prompts")
    
    def _setup_ai_providers(self) -> Dict:
        """Setup multiple AI providers with priority order"""
        providers = {}
        
        # 1. OpenRouter (best for legal - access to Claude, GPT-4, etc.)
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key and OPENAI_AVAILABLE:
            try:
                providers['openrouter'] = {
                    'client': AsyncOpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=openrouter_key
                    ),
                    'model': 'anthropic/claude-3.5-sonnet',  # Best for legal writing
                    'priority': 1,
                    'cost_per_1k': 0.003
                }
                logger.info("✅ OpenRouter configured (Claude 3.5 Sonnet)")
            except Exception as e:
                logger.error(f"❌ OpenRouter setup failed: {e}")
        
        # 2. Claude Direct API
        claude_key = os.getenv('ANTHROPIC_API_KEY') or 'ANTHROPIC_API_KEY_PLACEHOLDER'
        if claude_key and ANTHROPIC_AVAILABLE:
            try:
                providers['claude'] = {
                    'client': anthropic.AsyncAnthropic(api_key=claude_key),
                    'model': 'claude-3-5-sonnet-20241022',
                    'priority': 2,
                    'cost_per_1k': 0.003
                }
                logger.info("✅ Claude Direct API configured")
            except Exception as e:
                logger.error(f"❌ Claude setup failed: {e}")
        
        # 3. Groq (fast, free tier)
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key and OPENAI_AVAILABLE:
            try:
                providers['groq'] = {
                    'client': AsyncOpenAI(
                        base_url="https://api.groq.com/openai/v1",
                        api_key=groq_key
                    ),
                    'model': 'llama-3.1-70b-versatile',
                    'priority': 3,
                    'cost_per_1k': 0.0  # Free tier
                }
                logger.info("✅ Groq configured (Llama 3.1 70B)")
            except Exception as e:
                logger.error(f"❌ Groq setup failed: {e}")
        
        # 4. Azure OpenAI
        azure_key = os.getenv('AZURE_OPENAI_API_KEY')
        azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        if azure_key and azure_endpoint and OPENAI_AVAILABLE:
            try:
                providers['azure'] = {
                    'client': AsyncOpenAI(
                        base_url=f"{azure_endpoint}/openai/deployments",
                        api_key=azure_key
                    ),
                    'model': os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
                    'priority': 4,
                    'cost_per_1k': 0.03
                }
                logger.info("✅ Azure OpenAI configured")
            except Exception as e:
                logger.error(f"❌ Azure setup failed: {e}")
        
        # 5. OpenAI (fallback, but has quota issues)
        openai_key = os.getenv('OPENAI_API_KEY') or os.getenv('CHATGPT_API_KEY')
        if openai_key and OPENAI_AVAILABLE:
            try:
                providers['openai'] = {
                    'client': AsyncOpenAI(api_key=openai_key),
                    'model': 'gpt-3.5-turbo',  # Cheaper model due to quota
                    'priority': 5,
                    'cost_per_1k': 0.0015
                }
                logger.info("✅ OpenAI configured (GPT-3.5 Turbo)")
            except Exception as e:
                logger.error(f"❌ OpenAI setup failed: {e}")
        
        return providers
    
    def _select_primary_provider(self) -> Optional[str]:
        """Select primary AI provider based on priority"""
        if not self.ai_providers:
            return None
        
        # Sort by priority (lower = better)
        sorted_providers = sorted(
            self.ai_providers.items(),
            key=lambda x: x[1]['priority']
        )
        
        return sorted_providers[0][0] if sorted_providers else None
    
    def _load_prompts(self) -> Dict[int, str]:
        """Load all 1,000 legal prompts from file"""
        prompts = {}
        
        if not self.prompts_file.exists():
            logger.error(f"❌ Prompts file not found: {self.prompts_file}")
            return prompts
        
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse numbered prompts (format: "123. Prompt text...")
            pattern = r'^(\d+)\.\s+(.+?)(?=^\d+\.\s+|\Z)'
            matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
            
            for number, text in matches:
                prompt_num = int(number)
                prompt_text = text.strip()
                if prompt_text and not prompt_text.startswith('#'):
                    prompts[prompt_num] = prompt_text
            
            logger.info(f"📄 Loaded {len(prompts)} legal prompts from file")
            return prompts
            
        except Exception as e:
            logger.error(f"❌ Failed to load prompts: {e}")
            return prompts
    
    def initialize_database(self) -> bool:
        """Initialize legal document generation database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    document_type TEXT NOT NULL,
                    prompt_number INTEGER,
                    prompt_category TEXT,
                    input_parameters TEXT,
                    generated_content TEXT,
                    model_used TEXT DEFAULT 'gpt-4',
                    tokens_used INTEGER DEFAULT 0,
                    processing_time REAL DEFAULT 0,
                    quality_score REAL DEFAULT 0,
                    client_id TEXT,
                    case_number TEXT,
                    status TEXT DEFAULT 'draft'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_number INTEGER UNIQUE,
                    prompt_category TEXT,
                    times_used INTEGER DEFAULT 0,
                    avg_quality_score REAL DEFAULT 0,
                    avg_processing_time REAL DEFAULT 0,
                    success_rate REAL DEFAULT 0,
                    last_used DATETIME
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS client_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT NOT NULL,
                    client_name TEXT,
                    case_number TEXT,
                    document_count INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0,
                    subscription_tier TEXT DEFAULT 'free',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Legal document database initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    def get_prompt_by_number(self, prompt_number: int) -> Optional[str]:
        """Get specific prompt by number"""
        return self.prompts.get(prompt_number)
    
    def get_prompts_by_category(self, category: str) -> Dict[int, str]:
        """Get all prompts in a category"""
        if category not in self.prompt_categories:
            logger.error(f"❌ Unknown category: {category}")
            return {}
        
        cat_config = self.prompt_categories[category]
        return {
            num: prompt 
            for num, prompt in self.prompts.items() 
            if cat_config['start'] <= num <= cat_config['end']
        }
    
    def list_categories(self) -> Dict:
        """List all available prompt categories with counts"""
        category_info = {}
        
        for cat_name, config in self.prompt_categories.items():
            prompts_in_category = sum(
                1 for num in self.prompts.keys() 
                if config['start'] <= num <= config['end']
            )
            
            category_info[cat_name] = {
                'description': config['description'],
                'range': f"{config['start']}-{config['end']}",
                'count': prompts_in_category
            }
        
        return category_info
    
    async def generate_document(
        self, 
        prompt_number: int, 
        parameters: Dict[str, str],
        model: str = "gpt-4",
        client_id: Optional[str] = None
    ) -> Dict:
        """
        Generate legal document using specified prompt and parameters
        
        Args:
            prompt_number: Number of prompt to use (1-1000)
            parameters: Dict of parameter replacements (e.g., {'CASE_NUMBER': '1:23-cv-12345'})
            model: OpenAI model to use
            client_id: Optional client identifier for tracking
        
        Returns:
            Dict with generated content, metadata, and status
        """
        start_time = datetime.now()
        
        # Get prompt template
        prompt_template = self.get_prompt_by_number(prompt_number)
        if not prompt_template:
            return {
                'success': False,
                'error': f'Prompt {prompt_number} not found',
                'prompt_number': prompt_number
            }
        
        # Get category
        category = self._get_category_for_prompt(prompt_number)
        
        # Replace parameters in prompt
        final_prompt = prompt_template
        for key, value in parameters.items():
            final_prompt = final_prompt.replace(f'[{key}]', str(value))
        
        # Generate document
        if not self.ai_providers:
            # Simulation mode when no AI providers available
            generated_content = f"[SIMULATED OUTPUT]\n\nPrompt: {final_prompt[:200]}...\n\nThis would generate a legal document using AI."
            tokens_used = 0
            quality_score = 0.0
        else:
            try:
                # Call AI with automatic fallback
                response = await self._call_ai_with_fallback(final_prompt, model)
                generated_content = response['content']
                tokens_used = response['tokens']
                quality_score = self._assess_quality(generated_content)
                
            except Exception as e:
                logger.error(f"❌ All AI providers failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'prompt_number': prompt_number
                }
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Store in database
        doc_id = await self._store_generated_document(
            prompt_number=prompt_number,
            category=category,
            parameters=parameters,
            content=generated_content,
            model=model,
            tokens=tokens_used,
            processing_time=processing_time,
            quality_score=quality_score,
            client_id=client_id
        )
        
        # Update performance metrics
        await self._update_prompt_performance(
            prompt_number, category, processing_time, quality_score
        )
        
        result = {
            'success': True,
            'document_id': doc_id,
            'prompt_number': prompt_number,
            'category': category,
            'content': generated_content,
            'tokens_used': tokens_used,
            'processing_time': processing_time,
            'quality_score': quality_score,
            'model': model,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"✅ Generated document {doc_id} using prompt {prompt_number} ({processing_time:.2f}s)")
        
        return result
    
    async def _call_ai_with_fallback(self, prompt: str, model: str) -> Dict:
        """Call AI with automatic provider fallback"""
        # Try providers in priority order
        sorted_providers = sorted(
            self.ai_providers.items(),
            key=lambda x: x[1]['priority']
        )
        
        last_error = None
        for provider_name, config in sorted_providers:
            try:
                logger.info(f"🤖 Attempting {provider_name}...")
                
                if provider_name == 'claude':
                    # Claude uses different API
                    response = await self._call_claude(prompt, config)
                else:
                    # OpenAI-compatible APIs
                    response = await self._call_openai_compatible(prompt, config)
                
                logger.info(f"✅ {provider_name} successful ({response['tokens']} tokens)")
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️  {provider_name} failed: {e}")
                continue
        
        # All providers failed
        raise Exception(f"All AI providers failed. Last error: {last_error}")
    
    async def _call_openai_compatible(self, prompt: str, config: Dict) -> Dict:
        """Call OpenAI-compatible API (OpenAI, Azure, Groq, OpenRouter)"""
        try:
            response = await config['client'].chat.completions.create(
                model=config['model'],
                messages=[
                    {"role": "system", "content": "You are an expert legal assistant specializing in consumer law, FCRA, FDCPA, civil procedure, and federal court practice. Generate professional, accurate legal documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens': response.usage.total_tokens
            }
            
        except Exception as e:
            raise
    
    async def _call_claude(self, prompt: str, config: Dict) -> Dict:
        """Call Claude API directly"""
        try:
            message = await config['client'].messages.create(
                model=config['model'],
                max_tokens=2000,
                temperature=0.3,
                system="You are an expert legal assistant specializing in consumer law, FCRA, FDCPA, civil procedure, and federal court practice. Generate professional, accurate legal documents.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'content': message.content[0].text,
                'tokens': message.usage.input_tokens + message.usage.output_tokens
            }
            
        except Exception as e:
            raise
    
    def _assess_quality(self, content: str) -> float:
        """Assess quality of generated legal document (0.0-1.0)"""
        score = 0.5  # Base score
        
        # Check length (legal docs should be substantive)
        if len(content) > 500:
            score += 0.1
        if len(content) > 1000:
            score += 0.1
        
        # Check for legal terminology
        legal_terms = ['pursuant to', 'hereby', 'plaintiff', 'defendant', 'FRCP', 'USC', 'motion', 'court']
        terms_found = sum(1 for term in legal_terms if term.lower() in content.lower())
        score += min(0.2, terms_found * 0.025)
        
        # Check for structure (paragraphs)
        paragraphs = content.count('\n\n')
        if paragraphs >= 3:
            score += 0.1
        
        return min(1.0, score)
    
    def _get_category_for_prompt(self, prompt_number: int) -> str:
        """Determine category for prompt number"""
        for category, config in self.prompt_categories.items():
            if config['start'] <= prompt_number <= config['end']:
                return category
        return 'unknown'
    
    async def _store_generated_document(
        self, 
        prompt_number: int,
        category: str,
        parameters: Dict,
        content: str,
        model: str,
        tokens: int,
        processing_time: float,
        quality_score: float,
        client_id: Optional[str]
    ) -> int:
        """Store generated document in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO generated_documents 
                (document_type, prompt_number, prompt_category, input_parameters,
                 generated_content, model_used, tokens_used, processing_time,
                 quality_score, client_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                category,
                prompt_number,
                category,
                json.dumps(parameters),
                content,
                model,
                tokens,
                processing_time,
                quality_score,
                client_id
            ))
            
            doc_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return doc_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store document: {e}")
            return 0
    
    async def _update_prompt_performance(
        self, 
        prompt_number: int, 
        category: str,
        processing_time: float,
        quality_score: float
    ):
        """Update performance metrics for prompt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute(
                "SELECT times_used, avg_quality_score, avg_processing_time FROM prompt_performance WHERE prompt_number = ?",
                (prompt_number,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing record
                times_used, avg_quality, avg_time = row
                new_times = times_used + 1
                new_avg_quality = (avg_quality * times_used + quality_score) / new_times
                new_avg_time = (avg_time * times_used + processing_time) / new_times
                
                cursor.execute("""
                    UPDATE prompt_performance 
                    SET times_used = ?, avg_quality_score = ?, avg_processing_time = ?, last_used = CURRENT_TIMESTAMP
                    WHERE prompt_number = ?
                """, (new_times, new_avg_quality, new_avg_time, prompt_number))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO prompt_performance 
                    (prompt_number, prompt_category, times_used, avg_quality_score, avg_processing_time, last_used)
                    VALUES (?, ?, 1, ?, ?, CURRENT_TIMESTAMP)
                """, (prompt_number, category, quality_score, processing_time))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to update performance metrics: {e}")
    
    async def generate_credit_dispute_letter(
        self, 
        case_number: str,
        debt_collector: str,
        dismissal_date: str,
        credit_bureau: str = "Equifax",
        client_id: Optional[str] = None
    ) -> Dict:
        """
        Quick helper: Generate credit dispute letter for dismissed lawsuit
        Uses prompt #1 (credit dispute for dismissed case)
        """
        parameters = {
            'CASE_NUMBER': case_number,
            'DEBT_COLLECTOR': debt_collector,
            'DATE': dismissal_date,
            'CREDIT_BUREAU': credit_bureau
        }
        
        logger.info(f"📝 Generating credit dispute letter for case {case_number}")
        return await self.generate_document(1, parameters, client_id=client_id)
    
    async def generate_motion_to_dismiss(
        self,
        case_number: str,
        claim_type: str,
        missing_element: str,
        client_id: Optional[str] = None
    ) -> Dict:
        """
        Quick helper: Generate Motion to Dismiss under FRCP 12(b)(6)
        Uses prompt #401 (Motion to Dismiss)
        """
        parameters = {
            'CASE_NUMBER': case_number,
            'CLAIM': claim_type,
            'REQUIRED_ELEMENT': missing_element
        }
        
        logger.info(f"📝 Generating Motion to Dismiss for case {case_number}")
        return await self.generate_document(401, parameters, client_id=client_id)
    
    async def analyze_pacer_case(
        self,
        case_number: str,
        district: str,
        client_id: Optional[str] = None
    ) -> Dict:
        """
        Quick helper: Analyze PACER case docket
        Uses prompt #201 (comprehensive case analysis)
        """
        parameters = {
            'CASE_NUMBER': case_number,
            'DISTRICT': district
        }
        
        logger.info(f"📊 Analyzing PACER case {case_number}")
        return await self.generate_document(201, parameters, client_id=client_id)
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics for all prompts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Overall stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_documents,
                    AVG(quality_score) as avg_quality,
                    AVG(processing_time) as avg_time,
                    SUM(tokens_used) as total_tokens
                FROM generated_documents
            """)
            overall = cursor.fetchone()
            
            # Category breakdown
            cursor.execute("""
                SELECT 
                    prompt_category,
                    COUNT(*) as count,
                    AVG(quality_score) as avg_quality
                FROM generated_documents
                GROUP BY prompt_category
                ORDER BY count DESC
            """)
            categories = cursor.fetchall()
            
            # Top performing prompts
            cursor.execute("""
                SELECT 
                    prompt_number,
                    times_used,
                    avg_quality_score
                FROM prompt_performance
                ORDER BY times_used DESC
                LIMIT 10
            """)
            top_prompts = cursor.fetchall()
            
            conn.close()
            
            return {
                'overall': {
                    'total_documents': overall[0] or 0,
                    'avg_quality': overall[1] or 0,
                    'avg_processing_time': overall[2] or 0,
                    'total_tokens': overall[3] or 0
                },
                'by_category': [
                    {'category': row[0], 'count': row[1], 'avg_quality': row[2]}
                    for row in categories
                ],
                'top_prompts': [
                    {'prompt_number': row[0], 'times_used': row[1], 'avg_quality': row[2]}
                    for row in top_prompts
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance stats: {e}")
            return {}


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="EQ12 Legal Prompt Executor")
    parser.add_argument("--action", choices=["list", "test", "generate", "stats"], 
                       default="list", help="Action to perform")
    parser.add_argument("--prompt", type=int, help="Prompt number to use")
    parser.add_argument("--category", help="Category to list/use")
    parser.add_argument("--case", help="Case number for generation")
    args = parser.parse_args()
    
    # Initialize executor
    executor = LegalPromptExecutor()
    executor.initialize_database()
    
    print("="*80)
    print("🏛️  EQ12 LEGAL PROMPT EXECUTOR")
    print(f"   {len(executor.prompts)} Legal/PACER Prompts Loaded")
    if executor.ai_providers:
        print(f"   🤖 AI Providers: {len(executor.ai_providers)} configured")
        print(f"   ✅ Primary: {executor.primary_provider}")
        for name, config in sorted(executor.ai_providers.items(), key=lambda x: x[1]['priority']):
            print(f"      {config['priority']}. {name:12} - {config['model']}")
    else:
        print("   ⚠️  No AI providers configured")
    print("="*80)
    
    if args.action == "list":
        print("\n📚 AVAILABLE PROMPT CATEGORIES:\n")
        categories = executor.list_categories()
        for cat_name, info in categories.items():
            print(f"   {cat_name:25} | {info['description']:40} | Prompts: {info['count']:3} | Range: {info['range']}")
    
    elif args.action == "test":
        print("\n🧪 TESTING LEGAL DOCUMENT GENERATION\n")
        
        # Test 1: Credit Dispute Letter
        print("Test 1: Credit Dispute Letter for Dismissed Lawsuit")
        result = await executor.generate_credit_dispute_letter(
            case_number="1:23-cv-12345",
            debt_collector="ABC Collections LLC",
            dismissal_date="October 15, 2025",
            credit_bureau="Equifax",
            client_id="test_client_001"
        )
        
        if result['success']:
            print(f"   ✅ Generated document {result['document_id']}")
            print(f"   ⏱️  Processing time: {result['processing_time']:.2f}s")
            print(f"   ⭐ Quality score: {result['quality_score']:.2f}")
            print(f"   📄 Content preview:\n")
            print(f"   {result['content'][:300]}...")
        else:
            print(f"   ❌ Generation failed: {result.get('error')}")
        
        print("\n" + "-"*80 + "\n")
        
        # Test 2: Motion to Dismiss
        print("Test 2: Motion to Dismiss under FRCP 12(b)(6)")
        result = await executor.generate_motion_to_dismiss(
            case_number="1:24-cv-54321",
            claim_type="breach of contract",
            missing_element="consideration",
            client_id="test_client_002"
        )
        
        if result['success']:
            print(f"   ✅ Generated document {result['document_id']}")
            print(f"   ⏱️  Processing time: {result['processing_time']:.2f}s")
            print(f"   ⭐ Quality score: {result['quality_score']:.2f}")
        
    elif args.action == "generate":
        if not args.prompt:
            print("❌ --prompt required for generate action")
            return
        
        print(f"\n📝 GENERATING DOCUMENT WITH PROMPT #{args.prompt}\n")
        
        # Example parameters (customize based on prompt)
        parameters = {
            'CASE_NUMBER': args.case or '1:25-cv-00001',
            'DEBT_COLLECTOR': 'Example Collector LLC',
            'DATE': datetime.now().strftime('%B %d, %Y'),
            'DISTRICT': 'Northern District of California'
        }
        
        result = await executor.generate_document(args.prompt, parameters)
        
        if result['success']:
            print(f"✅ Document generated successfully!")
            print(f"   Document ID: {result['document_id']}")
            print(f"   Category: {result['category']}")
            print(f"   Tokens: {result['tokens_used']}")
            print(f"   Quality: {result['quality_score']:.2f}")
            print(f"\n📄 GENERATED CONTENT:\n")
            print(result['content'])
        else:
            print(f"❌ Generation failed: {result.get('error')}")
    
    elif args.action == "stats":
        print("\n📊 PERFORMANCE STATISTICS\n")
        stats = executor.get_performance_stats()
        
        if stats:
            overall = stats['overall']
            print(f"Overall Statistics:")
            print(f"   Total Documents: {overall['total_documents']}")
            print(f"   Avg Quality: {overall['avg_quality']:.2f}")
            print(f"   Avg Processing Time: {overall['avg_processing_time']:.2f}s")
            print(f"   Total Tokens Used: {overall['total_tokens']:,}")
            
            if stats['by_category']:
                print(f"\nBy Category:")
                for cat in stats['by_category']:
                    print(f"   {cat['category']:25} | Documents: {cat['count']:3} | Avg Quality: {cat['avg_quality']:.2f}")
            
            if stats['top_prompts']:
                print(f"\nTop 10 Most Used Prompts:")
                for prompt in stats['top_prompts']:
                    print(f"   Prompt #{prompt['prompt_number']:4} | Used: {prompt['times_used']:3}x | Quality: {prompt['avg_quality']:.2f}")
    
    print("\n" + "="*80)
    print("✅ Legal Prompt Executor completed!")

if __name__ == "__main__":
    asyncio.run(main())
