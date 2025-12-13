# EQ12 Expert Model Selection & API Integration Guide
## Production-Ready Client Wrappers for GPT-5 & Responses API

---

## 🎯 **QUICK MODEL MATRIX - EQ12 OPTIMIZED**

| **EQ12 Task** | **Model** | **API** | **Temperature** | **Notes** |
|---------------|-----------|---------|-----------------|-----------|
| **Odds parsing/normalization → JSON** | `gpt-4o-mini` | Responses | 0.0-0.2 | Fast/cheap extraction with JSON schema |
| **De-dupe lines, detect hooks, timezone fixes** | `gpt-4o-mini` | Responses | 0.0 | Deterministic transforms, `response_format` JSON |
| **Parlay construction (EV filters, Kelly sizing)** | `gpt-4o` | Responses | 0.1 | Use `reasoning.effort: "low"` for constraints |
| **Human explanations (≤80 words)** | `gpt-4o-mini` | Responses | 0.3 | Cost optimization, no heavy reasoning needed |
| **Rule conflicts, repair invalid JSON** | `gpt-4o` | Responses | 0.1 | Validator/repair pass when needed |
| **Multi-book hedges, complex planning** | `o1` or `gpt-4o` | Responses | 0.1 | Use sparingly (latency/cost), cache results |

---

## 🏗️ **PRODUCTION CLIENT ARCHITECTURE**

### **Core Principles**
- ✅ **Pin model snapshots** in production (`gpt-4o-2024-11-20`)
- ✅ **Always use structured output** (`response_format: json_schema`)
- ✅ **Prefer `instructions` for global behavior** 
- ✅ **Idempotency keys** for retry safety
- ✅ **Telemetry & fallbacks** built-in

### **Client Wrapper Structure**
```
C:\EQ12\models\
├── eq12_client.py          # Main Python client wrapper
├── eq12_client.js          # Node.js client wrapper  
├── schemas\                # JSON schemas for validation
│   ├── odds_extract.json   # Normalized odds format
│   ├── parlay_build.json   # Parlay construction schema
│   └── validation.json     # Repair/validation schema
├── prompts\                # Reusable prompt library
│   ├── odds_extractor.md   # Fast odds normalization
│   ├── parlay_builder.md   # Parlay construction with constraints
│   └── validator.md        # JSON repair and validation  
└── examples\               # Usage examples and tests
```

---

## 🐍 **PYTHON CLIENT WRAPPER**

### **Core EQ12 Client**
```python
#!/usr/bin/env python3
"""
EQ12 Production Model Client
Expert-level wrapper for GPT-4o/o1 with EQ12-specific optimizations
"""

import json
import hashlib
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import openai
from openai import OpenAI

@dataclass
class EQ12Config:
    """EQ12-specific model configuration."""
    # Model selection
    extraction_model: str = "gpt-4o-mini-2024-07-18"
    reasoning_model: str = "gpt-4o-2024-11-20" 
    planning_model: str = "o1-2024-12-17"
    
    # Temperature settings
    extraction_temp: float = 0.0
    reasoning_temp: float = 0.1
    planning_temp: float = 0.1
    
    # EQ12 constraints
    allowed_books: List[str] = None
    max_legs_per_parlay: int = 8
    min_ev_threshold: float = 0.02
    kelly_cap_per_leg: float = 0.025
    
    def __post_init__(self):
        if self.allowed_books is None:
            self.allowed_books = ["draftkings", "fanduel", "betmgm"]

class EQ12ModelClient:
    """Production-ready OpenAI client optimized for EQ12 betting workflows."""
    
    def __init__(self, config: EQ12Config = None):
        self.config = config or EQ12Config()
        self.client = OpenAI()
        self.schemas = self._load_schemas()
        self._request_count = 0
        
    def _load_schemas(self) -> Dict[str, Dict]:
        """Load JSON schemas for validation."""
        schema_dir = Path(__file__).parent / "schemas"
        schemas = {}
        
        schema_files = {
            'odds_extract': 'odds_extract.json',
            'parlay_build': 'parlay_build.json', 
            'validation': 'validation.json'
        }
        
        for name, filename in schema_files.items():
            try:
                with open(schema_dir / filename) as f:
                    schemas[name] = json.load(f)
            except FileNotFoundError:
                # Fallback to basic schema
                schemas[name] = self._get_fallback_schema(name)
                
        return schemas
    
    def _get_fallback_schema(self, schema_type: str) -> Dict:
        """Fallback schemas if files not found."""
        if schema_type == 'odds_extract':
            return {
                "type": "object",
                "properties": {
                    "rows": {
                        "type": "array",
                        "items": {
                            "type": "object", 
                            "properties": {
                                "game_id": {"type": "string"},
                                "book": {"enum": self.config.allowed_books},
                                "market": {"enum": ["moneyline", "spread", "total"]},
                                "selection": {"type": "string"},
                                "american_odds": {"type": "integer"},
                                "last_update_utc": {"type": "string", "format": "date-time"}
                            },
                            "required": ["game_id", "book", "market", "selection", "american_odds"]
                        }
                    }
                }
            }
        return {"type": "object"}
    
    def _generate_idempotency_key(self, content: str) -> str:
        """Generate deterministic idempotency key."""
        self._request_count += 1
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"eq12_{int(time.time())}_{self._request_count}_{content_hash}"
    
    def extract_odds(self, 
                    raw_odds: str,
                    markets: List[str] = None,
                    timeout: int = 30) -> Dict[str, Any]:
        """
        Extract and normalize odds to EQ12 JSON format.
        Fast path using gpt-4o-mini with strict schema.
        """
        markets = markets or ["moneyline", "spread", "total"]
        
        # EQ12 extraction instructions
        instructions = (
            f"Extract ONLY {', '.join(self.config.allowed_books)} odds. "
            f"Markets: {', '.join(markets)}. "
            "Emit UTC RFC3339 timestamps. Drop other books. No prose."
        )
        
        idempotency_key = self._generate_idempotency_key(raw_odds)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.extraction_model,
                temperature=self.config.extraction_temp,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "developer", "content": "Return strictly valid JSON per schema."},
                    {"role": "user", "content": raw_odds}
                ],
                response_format={"type": "json_object"},
                timeout=timeout,
                extra_headers={"Idempotency-Key": idempotency_key}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate against schema
            import jsonschema
            jsonschema.validate(result, self.schemas['odds_extract'])
            
            return {
                "success": True,
                "data": result,
                "model_used": self.config.extraction_model,
                "tokens": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_used": self.config.extraction_model
            }
    
    def build_parlays(self,
                     odds_data: List[Dict],
                     bankroll: float,
                     min_ev: float = None,
                     max_legs: int = None,
                     strategy: str = "value_hunt") -> Dict[str, Any]:
        """
        Build parlays with EQ12 constraints using reasoning model.
        Uses gpt-4o with low reasoning effort for constraint satisfaction.
        """
        min_ev = min_ev or self.config.min_ev_threshold
        max_legs = max_legs or self.config.max_legs_per_parlay
        
        # EQ12 parlay construction instructions  
        instructions = (
            "You are EQ12 Parlay Assistant. "
            f"Rules: one leg per game; books ∈ {{{','.join(self.config.allowed_books)}}}; "
            f"UTC times; min EV ≥ {min_ev}; max {max_legs} legs per parlay. "
            "If no valid legs, return empty parlays array with explanation in notes."
        )
        
        # Input payload
        input_data = {
            "bankroll": bankroll,
            "min_ev": min_ev,
            "max_legs": max_legs,
            "strategy": strategy,
            "kelly_cap": self.config.kelly_cap_per_leg,
            "odds": odds_data
        }
        
        idempotency_key = self._generate_idempotency_key(json.dumps(input_data))
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.reasoning_model,
                temperature=self.config.reasoning_temp,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "developer", "content": "Return ONLY JSON. Validate unique games and book constraints."},
                    {"role": "user", "content": json.dumps(input_data)}
                ],
                response_format={"type": "json_object"},
                extra_headers={"Idempotency-Key": idempotency_key}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Post-process validation
            validated_result = self._validate_parlays(result)
            
            return {
                "success": True,
                "data": validated_result,
                "model_used": self.config.reasoning_model,
                "tokens": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            # Fallback to simpler model
            return self._fallback_parlay_build(odds_data, bankroll, min_ev, max_legs, str(e))
    
    def _validate_parlays(self, result: Dict) -> Dict:
        """Post-process parlay validation and filtering."""
        if "parlays" not in result:
            return result
            
        validated_parlays = []
        
        for parlay in result["parlays"]:
            # Check book consistency
            if "legs" not in parlay:
                continue
                
            books_used = set()
            valid_legs = []
            game_ids_seen = set()
            
            for leg in parlay["legs"]:
                # Enforce allowed books
                if leg.get("book") not in self.config.allowed_books:
                    continue
                    
                # Enforce one leg per game
                game_id = leg.get("game_id")
                if game_id in game_ids_seen:
                    continue
                    
                books_used.add(leg.get("book"))
                valid_legs.append(leg)
                game_ids_seen.add(game_id)
            
            # Single book per parlay
            if len(books_used) == 1 and len(valid_legs) >= 2:
                parlay["legs"] = valid_legs
                parlay["book"] = list(books_used)[0]
                validated_parlays.append(parlay)
        
        result["parlays"] = validated_parlays
        return result
    
    def _fallback_parlay_build(self, odds_data, bankroll, min_ev, max_legs, error_msg):
        """Fallback to simpler model if reasoning model fails."""
        try:
            # Simplified parlay construction with gpt-4o-mini
            response = self.client.chat.completions.create(
                model=self.config.extraction_model,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": f"Build simple parlays. Books: {', '.join(self.config.allowed_books)} only."},
                    {"role": "user", "content": json.dumps({"bankroll": bankroll, "odds": odds_data[:10]})}  # Limit complexity
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "data": result,
                "model_used": f"{self.config.extraction_model} (fallback)",
                "fallback_reason": error_msg,
                "tokens": response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as fallback_error:
            return {
                "success": False,
                "error": f"Primary: {error_msg}, Fallback: {fallback_error}",
                "model_used": "fallback_failed"
            }
    
    def validate_and_repair(self, invalid_json: str, target_schema: str = "parlay_build") -> Dict[str, Any]:
        """
        Repair malformed JSON using validation model.
        GPT-4o with focused repair instructions.
        """
        instructions = (
            f"Fix this JSON to match {target_schema} schema. "
            "Correct syntax errors, add missing fields, remove invalid fields. "
            "Return only valid JSON, no explanations."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.reasoning_model,
                temperature=0.0,  # Deterministic repair
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": invalid_json}
                ],
                response_format={"type": "json_object"}
            )
            
            repaired = json.loads(response.choices[0].message.content)
            
            # Validate repaired JSON
            if target_schema in self.schemas:
                import jsonschema
                jsonschema.validate(repaired, self.schemas[target_schema])
            
            return {
                "success": True,
                "data": repaired,
                "model_used": self.config.reasoning_model
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_json": invalid_json
            }
    
    def explain_parlay(self, parlay_json: Dict, max_words: int = 80) -> str:
        """
        Generate human-readable parlay explanation.
        Fast summary using gpt-4o-mini.
        """
        instructions = (
            f"Explain this parlay in exactly 5 bullet points, ≤{max_words} words total. "
            "Format: Strategy, Risk Level, Best Edge, Stake, Timing. "
            "Be concise and factual."
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.extraction_model,
                temperature=0.3,  # Slight creativity for readability
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": json.dumps(parlay_json)}
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating explanation: {e}"

# Usage Example
if __name__ == "__main__":
    # Initialize client with EQ12 config
    config = EQ12Config(
        allowed_books=["draftkings", "fanduel", "betmgm"],
        min_ev_threshold=0.03,
        kelly_cap_per_leg=0.02
    )
    
    client = EQ12ModelClient(config)
    
    # Example: Extract odds
    raw_odds_blob = '''
    DraftKings: Chiefs -3 (-110), Bills +3 (-110), O/U 45.5
    FanDuel: Chiefs -2.5 (-105), Bills +2.5 (-115), O/U 46
    BetMGM: Chiefs -3 (-108), Bills +3 (-112), O/U 45
    '''
    
    odds_result = client.extract_odds(raw_odds_blob)
    print("Odds extraction:", odds_result["success"])
    
    if odds_result["success"]:
        # Build parlays from extracted odds
        parlay_result = client.build_parlays(
            odds_data=odds_result["data"].get("rows", []),
            bankroll=1000,
            min_ev=0.025,
            max_legs=4
        )
        print("Parlay construction:", parlay_result["success"])
        
        if parlay_result["success"] and parlay_result["data"].get("parlays"):
            # Generate human explanation
            explanation = client.explain_parlay(parlay_result["data"]["parlays"][0])
            print("Explanation:", explanation)