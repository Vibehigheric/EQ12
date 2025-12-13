#!/usr/bin/env python3
"""
EQ12 GODSTACK - Recipe Loader & Validator
Configuration-driven research engine with hot-reload capabilities

Core Features:
- Load and validate research recipes from YAML/JSON
- Hot-reload configuration without code restart
- JSONSchema validation for recipe structure
- Version management and recipe inheritance
- Environment-specific overrides
- Recipe dependency resolution
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("C:/EQ12/logs/recipe_loader.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class RecipeMetadata:
    """Recipe metadata and versioning"""

    name: str
    version: str
    description: str
    author: str
    created_at: datetime
    updated_at: datetime

    # Dependencies
    depends_on: list[str] = field(default_factory=list)
    inherits_from: str | None = None

    # Validation
    schema_version: str = "1.0"
    hash_signature: str = ""

    # Environment
    environments: list[str] = field(default_factory=lambda: ["default"])
    tags: list[str] = field(default_factory=list)


@dataclass
class RecipeConfig:
    """Complete recipe configuration"""

    metadata: RecipeMetadata

    # Core configuration sections
    planner: dict[str, Any]
    retrievers: list[dict[str, Any]]
    ranking: dict[str, Any]
    synthesis: dict[str, Any]
    policies: dict[str, Any]

    # Runtime configuration
    models: dict[str, Any]
    budgets: dict[str, Any]
    cache: dict[str, Any]
    outputs: dict[str, Any]

    # Environment overrides
    overrides: dict[str, dict[str, Any]] = field(default_factory=dict)


class RecipeValidator:
    """Recipe validation using JSONSchema"""

    def __init__(self):
        self.schema = self._load_recipe_schema()

    def _load_recipe_schema(self) -> dict[str, Any]:
        """Load recipe validation schema"""

        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["name", "planner", "retrievers", "synthesis"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "version": {"type": "string", "default": "1.0"},
                "description": {"type": "string"},
                "author": {"type": "string"},
                "planner": {
                    "type": "object",
                    "properties": {
                        "classifier": {"type": "string"},
                        "steps": {"type": "array", "items": {"type": "string"}},
                        "max_subqueries": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                        },
                    },
                },
                "retrievers": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "type"],
                        "properties": {
                            "name": {"type": "string"},
                            "type": {
                                "enum": [
                                    "http",
                                    "vector",
                                    "bm25",
                                    "graph",
                                    "rss",
                                    "sql",
                                ]
                            },
                            "enabled": {"type": "boolean", "default": True},
                            "priority": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 10,
                            },
                            "rate_limit": {
                                "type": "object",
                                "properties": {
                                    "rpm": {"type": "integer"},
                                    "burst": {"type": "integer"},
                                },
                            },
                        },
                    },
                },
                "ranking": {
                    "type": "object",
                    "properties": {
                        "reranker": {"type": "string"},
                        "weights": {
                            "type": "object",
                            "properties": {
                                "recency": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "authority": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "semantic": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                                "diversity": {
                                    "type": "number",
                                    "minimum": 0,
                                    "maximum": 1,
                                },
                            },
                        },
                        "max_results": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                        },
                    },
                },
                "synthesis": {
                    "type": "object",
                    "required": ["style"],
                    "properties": {
                        "style": {
                            "enum": [
                                "bullet+citations",
                                "narrative",
                                "structured",
                                "data_sheet",
                            ]
                        },
                        "require_citation": {"type": "boolean", "default": True},
                        "max_tokens": {
                            "type": "integer",
                            "minimum": 100,
                            "maximum": 8000,
                        },
                        "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                    },
                },
                "policies": {
                    "type": "object",
                    "properties": {
                        "allow_domains": {"type": "array", "items": {"type": "string"}},
                        "deny_domains": {"type": "array", "items": {"type": "string"}},
                        "freshness_days": {"type": "integer", "minimum": 1},
                        "safety": {
                            "enum": [
                                "strict",
                                "moderate",
                                "permissive",
                                "sports_advisory_only",
                            ]
                        },
                    },
                },
                "models": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string"},
                        "fallbacks": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "budgets": {
                    "type": "object",
                    "properties": {
                        "tpm": {"type": "integer", "minimum": 1000},
                        "rpm": {"type": "integer", "minimum": 10},
                        "cost_usd": {"type": "number", "minimum": 0},
                    },
                },
            },
        }

        return schema

    def validate_recipe(self, recipe_data: dict[str, Any]) -> Tuple[bool, list[str]]:
        """Validate recipe against schema"""

        errors = []

        try:
            jsonschema.validate(recipe_data, self.schema)

            # Additional business logic validation

            # Check weight sum for ranking
            if "ranking" in recipe_data and "weights" in recipe_data["ranking"]:
                weights = recipe_data["ranking"]["weights"]
                weight_sum = sum(weights.values())
                if not (0.9 <= weight_sum <= 1.1):  # Allow small tolerance
                    errors.append(f"Ranking weights sum to {weight_sum:.2f}, should be ~1.0")

            # Check for conflicting domains
            if "policies" in recipe_data:
                policies = recipe_data["policies"]
                allow_domains = set(policies.get("allow_domains", []))
                deny_domains = set(policies.get("deny_domains", []))

                conflicts = allow_domains.intersection(deny_domains)
                if conflicts:
                    errors.append(f"Conflicting domains in allow/deny lists: {conflicts}")

            # Check model availability (simplified)
            if "models" in recipe_data:
                models = recipe_data["models"]
                if "primary" in models:
                    primary = models["primary"]
                    fallbacks = models.get("fallbacks", [])

                    if primary in fallbacks:
                        errors.append("Primary model should not be in fallback list")

            return len(errors) == 0, errors

        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Validation error: {e!s}")
            return False, errors


class RecipeWatcher(FileSystemEventHandler):
    """Watch recipe files for changes and trigger hot-reload"""

    def __init__(self, loader):
        self.loader = loader

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith((".yaml", ".yml", ".json")):
            logger.info(f"Recipe file changed: {event.src_path}")
            self.loader.reload_recipe_from_path(event.src_path)


class RecipeLoader:
    """Main recipe loading and management system"""

    def __init__(self, recipes_dir: str = "C:/EQ12/recipes", enable_watching: bool = True):
        self.recipes_dir = Path(recipes_dir)
        self.enable_watching = enable_watching

        self.recipes: dict[str, RecipeConfig] = {}
        self.validator = RecipeValidator()
        self.file_hashes: dict[str, str] = {}

        # Hot-reload watcher
        self.observer = None
        if enable_watching:
            self.observer = Observer()
            self.observer.schedule(RecipeWatcher(self), str(self.recipes_dir), recursive=True)

        logger.info(f"RecipeLoader initialized for {self.recipes_dir}")

    def start_watching(self):
        """Start file watching for hot-reload"""
        if self.observer and not self.observer.is_alive():
            self.observer.start()
            logger.info("Recipe file watching started")

    def stop_watching(self):
        """Stop file watching"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            logger.info("Recipe file watching stopped")

    def load_all_recipes(self) -> dict[str, bool]:
        """Load all recipes from recipes directory"""

        results = {}

        if not self.recipes_dir.exists():
            logger.warning(f"Recipes directory does not exist: {self.recipes_dir}")
            return results

        for recipe_file in self.recipes_dir.glob("**/*.yaml"):
            success = self.load_recipe_from_path(str(recipe_file))
            results[str(recipe_file)] = success

        for recipe_file in self.recipes_dir.glob("**/*.yml"):
            success = self.load_recipe_from_path(str(recipe_file))
            results[str(recipe_file)] = success

        for recipe_file in self.recipes_dir.glob("**/*.json"):
            success = self.load_recipe_from_path(str(recipe_file))
            results[str(recipe_file)] = success

        logger.info(f"Loaded {sum(results.values())}/{len(results)} recipes")

        return results

    def load_recipe_from_path(self, file_path: str) -> bool:
        """Load single recipe from file path"""

        try:
            file_path = Path(file_path)

            # Check if file changed
            current_hash = self._calculate_file_hash(file_path)
            if str(file_path) in self.file_hashes:
                if self.file_hashes[str(file_path)] == current_hash:
                    logger.debug(f"Recipe file unchanged: {file_path}")
                    return True

            # Load file content
            with open(file_path, encoding="utf-8") as f:
                if file_path.suffix.lower() in [".yaml", ".yml"]:
                    recipe_data = yaml.safe_load(f)
                else:  # JSON
                    recipe_data = json.load(f)

            # Validate recipe
            is_valid, errors = self.validator.validate_recipe(recipe_data)
            if not is_valid:
                logger.error(f"Recipe validation failed for {file_path}: {errors}")
                return False

            # Parse recipe
            recipe = self._parse_recipe_data(recipe_data, file_path)

            # Store recipe
            self.recipes[recipe.metadata.name] = recipe
            self.file_hashes[str(file_path)] = current_hash

            logger.info(f"Loaded recipe: {recipe.metadata.name} v{recipe.metadata.version}")

            return True

        except Exception as e:
            logger.error(f"Failed to load recipe from {file_path}: {e}")
            return False

    def reload_recipe_from_path(self, file_path: str) -> bool:
        """Hot-reload recipe from file path"""

        logger.info(f"Hot-reloading recipe: {file_path}")
        return self.load_recipe_from_path(file_path)

    def get_recipe(self, name: str, environment: str = "default") -> RecipeConfig | None:
        """Get recipe by name with environment overrides"""

        if name not in self.recipes:
            return None

        recipe = self.recipes[name]

        # Apply environment overrides
        if environment in recipe.overrides:
            recipe = self._apply_overrides(recipe, recipe.overrides[environment])

        return recipe

    def list_recipes(self) -> dict[str, dict[str, Any]]:
        """List all loaded recipes with metadata"""

        recipes_info = {}

        for name, recipe in self.recipes.items():
            recipes_info[name] = {
                "version": recipe.metadata.version,
                "description": recipe.metadata.description,
                "author": recipe.metadata.author,
                "created_at": recipe.metadata.created_at.isoformat(),
                "updated_at": recipe.metadata.updated_at.isoformat(),
                "tags": recipe.metadata.tags,
                "environments": recipe.metadata.environments,
                "retrievers": len(recipe.retrievers),
                "has_overrides": len(recipe.overrides) > 0,
            }

        return recipes_info

    def validate_recipe_dependencies(self, recipe_name: str) -> Tuple[bool, list[str]]:
        """Validate recipe dependencies are available"""

        if recipe_name not in self.recipes:
            return False, [f"Recipe {recipe_name} not found"]

        recipe = self.recipes[recipe_name]
        missing_deps = []

        # Check direct dependencies
        for dep in recipe.metadata.depends_on:
            if dep not in self.recipes:
                missing_deps.append(dep)

        # Check inheritance
        if recipe.metadata.inherits_from:
            if recipe.metadata.inherits_from not in self.recipes:
                missing_deps.append(f"Parent recipe: {recipe.metadata.inherits_from}")

        return len(missing_deps) == 0, missing_deps

    def _parse_recipe_data(self, recipe_data: dict[str, Any], file_path: Path) -> RecipeConfig:
        """Parse recipe data into RecipeConfig object"""

        # Parse metadata
        metadata = RecipeMetadata(
            name=recipe_data["name"],
            version=recipe_data.get("version", "1.0"),
            description=recipe_data.get("description", ""),
            author=recipe_data.get("author", "unknown"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            depends_on=recipe_data.get("depends_on", []),
            inherits_from=recipe_data.get("inherits_from"),
            environments=recipe_data.get("environments", ["default"]),
            tags=recipe_data.get("tags", []),
        )

        # Calculate hash
        content_str = json.dumps(recipe_data, sort_keys=True)
        metadata.hash_signature = hashlib.md5(content_str.encode()).hexdigest()[:12]

        # Parse configuration sections
        recipe_config = RecipeConfig(
            metadata=metadata,
            planner=recipe_data.get("planner", {}),
            retrievers=recipe_data.get("retrievers", []),
            ranking=recipe_data.get("ranking", {}),
            synthesis=recipe_data.get("synthesis", {}),
            policies=recipe_data.get("policies", {}),
            models=recipe_data.get("models", {}),
            budgets=recipe_data.get("budgets", {}),
            cache=recipe_data.get("cache", {}),
            outputs=recipe_data.get("outputs", {}),
            overrides=recipe_data.get("overrides", {}),
        )

        return recipe_config

    def _apply_overrides(self, recipe: RecipeConfig, overrides: dict[str, Any]) -> RecipeConfig:
        """Apply environment-specific overrides to recipe"""

        # Create a copy of the recipe (shallow copy for now)
        import copy

        modified_recipe = copy.deepcopy(recipe)

        # Apply overrides to each section
        for section, section_overrides in overrides.items():
            if hasattr(modified_recipe, section):
                current_section = getattr(modified_recipe, section)

                if isinstance(current_section, dict):
                    current_section.update(section_overrides)
                elif isinstance(current_section, list):
                    # For lists, replace entirely or extend based on override structure
                    if isinstance(section_overrides, list):
                        setattr(modified_recipe, section, section_overrides)
                else:
                    setattr(modified_recipe, section, section_overrides)

        return modified_recipe

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of file content for change detection"""

        try:
            with open(file_path, "rb") as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception:
            return ""

    def export_recipe_schema(self) -> dict[str, Any]:
        """Export the recipe JSON schema for documentation"""
        return self.validator.schema

    def create_recipe_template(self, name: str, recipe_type: str = "general") -> dict[str, Any]:
        """Create a recipe template for the specified type"""

        templates = {
            "mlb_research": {
                "name": name,
                "version": "1.0",
                "description": "MLB SGP research recipe",
                "author": "EQ12",
                "planner": {
                    "classifier": "intent/v2",
                    "steps": [
                        "pitching_outlook",
                        "hitting_outlook",
                        "park_weather",
                        "market_moves",
                    ],
                    "max_subqueries": 5,
                },
                "retrievers": [
                    {
                        "name": "odds_api",
                        "type": "http",
                        "enabled": True,
                        "priority": 1,
                        "base_url": "https://api.example-odds.io",
                        "rate_limit": {"rpm": 120},
                    },
                    {
                        "name": "vector_news",
                        "type": "vector",
                        "enabled": True,
                        "priority": 2,
                        "index": "qdrant://eq12_news",
                    },
                ],
                "ranking": {
                    "reranker": "crossencoder/mpnet-v3",
                    "weights": {
                        "recency": 0.35,
                        "authority": 0.25,
                        "semantic": 0.30,
                        "diversity": 0.10,
                    },
                    "max_results": 20,
                },
                "synthesis": {
                    "style": "bullet+citations",
                    "require_citation": True,
                    "max_tokens": 1400,
                    "temperature": 0.3,
                },
                "policies": {
                    "allow_domains": ["mlb.com", "fangraphs.com", "statcast"],
                    "freshness_days": 14,
                    "safety": "sports_advisory_only",
                },
                "models": {
                    "primary": "gpt-4o",
                    "fallbacks": ["gpt-4o-mini", "gpt-3.5-turbo"],
                },
                "budgets": {"tpm": 60000, "rpm": 500, "cost_usd": 1.50},
                "cache": {"doc_ttl_min": 720, "answer_ttl_min": 60},
                "outputs": {
                    "sections": [
                        "Summary",
                        "Pitching",
                        "Hitting",
                        "Park/Weather",
                        "Market Moves",
                        "Data Sheet",
                    ]
                },
            },
            "general": {
                "name": name,
                "version": "1.0",
                "description": "General research recipe",
                "author": "EQ12",
                "planner": {
                    "classifier": "intent/basic",
                    "steps": ["main_query"],
                    "max_subqueries": 3,
                },
                "retrievers": [
                    {
                        "name": "web_search",
                        "type": "http",
                        "enabled": True,
                        "priority": 1,
                        "rate_limit": {"rpm": 60},
                    }
                ],
                "ranking": {
                    "weights": {
                        "recency": 0.3,
                        "authority": 0.3,
                        "semantic": 0.3,
                        "diversity": 0.1,
                    },
                    "max_results": 15,
                },
                "synthesis": {
                    "style": "narrative",
                    "require_citation": True,
                    "max_tokens": 1000,
                },
                "policies": {"freshness_days": 7, "safety": "moderate"},
                "models": {"primary": "gpt-4o-mini", "fallbacks": ["gpt-3.5-turbo"]},
                "budgets": {"tpm": 30000, "rpm": 200, "cost_usd": 0.50},
            },
        }

        return templates.get(recipe_type, templates["general"])


def main():
    """CLI interface for recipe management"""

    import argparse

    parser = argparse.ArgumentParser(description="EQ12 Recipe Loader")
    parser.add_argument("--load-all", action="store_true", help="Load all recipes")
    parser.add_argument("--validate", help="Validate specific recipe file")
    parser.add_argument("--list", action="store_true", help="List loaded recipes")
    parser.add_argument("--template", help="Create recipe template")
    parser.add_argument("--type", default="general", help="Template type (general, mlb_research)")
    parser.add_argument("--watch", action="store_true", help="Start file watching")

    args = parser.parse_args()

    loader = RecipeLoader(enable_watching=args.watch)

    if args.load_all:
        print("📂 Loading all recipes...")
        results = loader.load_all_recipes()

        success_count = sum(results.values())
        total_count = len(results)

        print(f"✅ Loaded {success_count}/{total_count} recipes")

        for file_path, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {Path(file_path).name}")

    elif args.validate:
        print(f"🔍 Validating recipe: {args.validate}")

        success = loader.load_recipe_from_path(args.validate)

        if success:
            print("✅ Recipe is valid")
        else:
            print("❌ Recipe validation failed")

    elif args.list:
        recipes = loader.list_recipes()

        print(f"📋 Loaded Recipes ({len(recipes)}):")

        for name, info in recipes.items():
            print(f"\n📄 {name} (v{info['version']})")
            print(f"   Description: {info['description']}")
            print(f"   Author: {info['author']}")
            print(f"   Retrievers: {info['retrievers']}")
            print(f"   Environments: {', '.join(info['environments'])}")
            if info["tags"]:
                print(f"   Tags: {', '.join(info['tags'])}")

    elif args.template:
        print(f"📝 Creating template: {args.template}")

        template = loader.create_recipe_template(args.template, args.type)

        output_path = f"C:/EQ12/recipes/{args.template}.yaml"

        with open(output_path, "w") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Template created: {output_path}")

    elif args.watch:
        print("👀 Starting recipe file watching...")

        loader.load_all_recipes()
        loader.start_watching()

        try:
            print("Press Ctrl+C to stop watching...")
            import time

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            loader.stop_watching()
            print("\n⏹️ File watching stopped")

    else:
        print("📄 EQ12 Recipe Loader - Use --help for options")


if __name__ == "__main__":
    main()
