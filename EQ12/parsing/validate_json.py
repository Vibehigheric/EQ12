"""
EQ12 JSON Schema Validation

Provides robust JSON/YAML validation with user-friendly error messages.
Supports schema generation, validation, and error reporting for EQ12 data structures.

Key functions:
- validate(): Validate JSON/dict against schema with friendly errors
- generate_schema(): Auto-generate JSON schema from sample data
- validate_file(): Validate JSON/YAML files directly
- SchemaError: Custom exception with detailed path information
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import ValidationError, validators


class SchemaValidationError(Exception):
    """Custom exception for schema validation errors with friendly messages."""

    def __init__(self, message: str, path: list[str] | None = None, value: Any = None):
        self.message = message
        self.path = path or []
        self.value = value
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with path information."""
        if self.path:
            path_str = " -> ".join(str(p) for p in self.path)
            return f"{self.message} at path: {path_str}"
        return self.message


def _format_validation_error(error: ValidationError) -> str:
    """
    Convert jsonschema ValidationError to friendly message.

    Args:
        error: ValidationError from jsonschema

    Returns:
        User-friendly error description
    """
    # Build path string
    path_parts = []
    for part in error.absolute_path:
        if isinstance(part, int):
            path_parts.append(f"[{part}]")
        else:
            path_parts.append(str(part))

    path_str = ".".join(path_parts) if path_parts else "root"

    # Format message based on error type
    if error.validator == "required":
        missing_props = error.message.split("'")[1::2]
        return f"Missing required properties: {', '.join(missing_props)} (at {path_str})"

    if error.validator == "type":
        expected = error.schema.get("type", "unknown")
        actual = type(error.instance).__name__
        return f"Expected type '{expected}', got '{actual}' (at {path_str})"

    if error.validator == "enum":
        allowed = error.schema.get("enum", [])
        return f"Value must be one of {allowed}, got '{error.instance}' (at {path_str})"

    if error.validator == "format":
        format_name = error.schema.get("format", "unknown")
        return f"Invalid {format_name} format: '{error.instance}' (at {path_str})"

    if error.validator == "minLength":
        min_len = error.schema.get("minLength", 0)
        actual_len = len(error.instance)
        return f"String too short: minimum {min_len} characters, got {actual_len} (at {path_str})"

    if error.validator == "maxLength":
        max_len = error.schema.get("maxLength", 0)
        actual_len = len(error.instance)
        return f"String too long: maximum {max_len} characters, got {actual_len} (at {path_str})"

    if error.validator == "minimum":
        min_val = error.schema.get("minimum", 0)
        return f"Value too small: minimum {min_val}, got {error.instance} (at {path_str})"

    if error.validator == "maximum":
        max_val = error.schema.get("maximum", 0)
        return f"Value too large: maximum {max_val}, got {error.instance} (at {path_str})"

    # Fallback to original message with path
    return f"{error.message} (at {path_str})"


def validate(data: Any, schema: dict[str, Any] | str | Path, strict: bool = True) -> dict[str, Any]:
    """
    Validate data against JSON schema with friendly error messages.

    Args:
        data: Data to validate (dict, list, or any JSON-serializable object)
        schema: JSON schema as dict, or path to schema file
        strict: If True, raise exception on validation errors

    Returns:
        Validation result dict with keys: valid, errors, warnings

    Raises:
        SchemaValidationError: If validation fails and strict=True
        FileNotFoundError: If schema file doesn't exist

    Example:
        result = validate({"name": "John", "age": 30}, "user_schema.json")
        if not result["valid"]:
            print("Validation errors:", result["errors"])
    """
    # Load schema if it's a file path
    if isinstance(schema, (str, Path)):
        schema_path = Path(schema)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        try:
            with open(schema_path, encoding="utf-8") as f:
                schema_dict = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")
    else:
        schema_dict = schema

    # Validate schema itself
    try:
        validators.validator_for(schema_dict).check_schema(schema_dict)
    except Exception as e:
        raise ValueError(f"Invalid schema: {e}")

    # Perform validation
    validator = validators.validator_for(schema_dict)(schema_dict)
    errors = []
    warnings = []

    # Collect all validation errors
    validation_errors = list(validator.iter_errors(data))

    for error in validation_errors:
        friendly_error = _format_validation_error(error)

        # Categorize as error or warning based on severity
        if error.validator in ["required", "type"]:
            errors.append(friendly_error)
        else:
            warnings.append(friendly_error)

    # Build result
    result = {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }

    # Raise exception if strict mode and errors exist
    if strict and errors:
        error_msg = f"Validation failed with {len(errors)} error(s)"
        if len(errors) == 1:
            error_msg = errors[0]
        raise SchemaValidationError(error_msg)

    return result


def validate_file(
    file_path: str | Path, schema: dict[str, Any] | str | Path, strict: bool = True
) -> dict[str, Any]:
    """
    Validate JSON/YAML file against schema.

    Args:
        file_path: Path to JSON/YAML file to validate
        schema: JSON schema as dict or path to schema file
        strict: If True, raise exception on validation errors

    Returns:
        Validation result dict
    """
    data_path = Path(file_path)

    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load data using our universal parser
    from .ingest_any import load_any

    try:
        data = load_any(data_path)
    except Exception as e:
        raise ValueError(f"Could not parse data file: {e}")

    # Handle parse errors from load_any
    if isinstance(data, dict) and "error" in data:
        raise ValueError(f"Could not parse data file: {data['error']}")

    return validate(data, schema, strict)


def generate_schema(
    sample_data: Any,
    title: str = "Generated Schema",
    description: str = "Auto-generated JSON schema",
) -> dict[str, Any]:
    """
    Generate JSON schema from sample data.

    Args:
        sample_data: Sample data to analyze
        title: Schema title
        description: Schema description

    Returns:
        Generated JSON schema dict

    Example:
        sample = {"name": "John", "age": 30, "active": True}
        schema = generate_schema(sample, "User Schema")
    """

    def _infer_type(value: Any) -> dict[str, Any]:
        """Infer JSON schema type from Python value."""
        if value is None:
            return {"type": "null"}
        if isinstance(value, bool):
            return {"type": "boolean"}
        if isinstance(value, int):
            return {"type": "integer"}
        if isinstance(value, float):
            return {"type": "number"}
        if isinstance(value, str):
            schema = {"type": "string"}
            # Add format hints for common patterns
            if "@" in value and "." in value:
                schema["format"] = "email"
            elif value.startswith(("http://", "https://")):
                schema["format"] = "uri"
            return schema
        if isinstance(value, list):
            schema = {"type": "array"}
            if value:
                # Analyze first few items to infer item type
                item_schemas = [_infer_type(item) for item in value[:5]]
                if len({json.dumps(s, sort_keys=True) for s in item_schemas}) == 1:
                    schema["items"] = item_schemas[0]
            return schema
        if isinstance(value, dict):
            schema = {"type": "object", "properties": {}, "required": []}
            for key, val in value.items():
                schema["properties"][key] = _infer_type(val)
                schema["required"].append(key)
            return schema
        return {"type": "string", "description": f"Unknown type: {type(value)}"}

    base_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "description": description,
    }

    # Generate schema from sample data
    inferred_schema = _infer_type(sample_data)
    base_schema.update(inferred_schema)

    return base_schema


def create_eq12_schemas() -> dict[str, dict[str, Any]]:
    """
    Create common JSON schemas for EQ12 data structures.

    Returns:
        Dictionary of schema name -> schema dict
    """
    schemas = {
        "eq12_config": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "EQ12 Configuration",
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                "enabled": {"type": "boolean"},
                "settings": {
                    "type": "object",
                    "properties": {
                        "timeout": {"type": "integer", "minimum": 0},
                        "retries": {"type": "integer", "minimum": 0},
                        "debug": {"type": "boolean"},
                    },
                },
            },
            "required": ["name", "version", "enabled"],
        },
        "eq12_log_entry": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "EQ12 Log Entry",
            "type": "object",
            "properties": {
                "timestamp": {"type": "string", "format": "date-time"},
                "level": {
                    "type": "string",
                    "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                },
                "module": {"type": "string", "minLength": 1},
                "message": {"type": "string"},
                "attempt_id": {"type": "integer", "minimum": 1},
                "error_type": {
                    "type": "string",
                    "enum": [
                        "rate_limit",
                        "quota_exhausted",
                        "timeout",
                        "connection_error",
                    ],
                },
                "backoff_seconds": {"type": "integer", "minimum": 0},
            },
            "required": ["timestamp", "level", "message"],
        },
        "eq12_task_result": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "EQ12 Task Result",
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "minLength": 1},
                "status": {
                    "type": "string",
                    "enum": ["success", "failure", "pending", "cancelled"],
                },
                "started_at": {"type": "string", "format": "date-time"},
                "completed_at": {"type": "string", "format": "date-time"},
                "duration_ms": {"type": "number", "minimum": 0},
                "result": {"type": "object"},
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object"},
                    },
                },
            },
            "required": ["task_id", "status", "started_at"],
        },
    }

    return schemas


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python validate_json.py <command> <file> [schema]")
        print("Commands:")
        print("  validate - Validate file against schema")
        print("  generate - Generate schema from sample file")
        print("  schemas - Show built-in EQ12 schemas")
        sys.exit(1)

    command = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else None
    schema_path = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        if command == "validate":
            if not schema_path:
                print("Error: Schema file path required for validation")
                sys.exit(1)

            result = validate_file(file_path, schema_path, strict=False)

            if result["valid"]:
                print(f"✅ Validation passed: {file_path}")
            else:
                print(f"❌ Validation failed: {file_path}")
                for error in result["errors"]:
                    print(f"  Error: {error}")
                for warning in result["warnings"]:
                    print(f"  Warning: {warning}")

        elif command == "generate":
            from .ingest_any import load_any

            data = load_any(file_path)
            schema = generate_schema(data, f"Schema for {Path(file_path).name}")

            output_path = Path(file_path).with_suffix(".schema.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2)

            print(f"✅ Generated schema: {output_path}")

        elif command == "schemas":
            schemas = create_eq12_schemas()
            for name, schema in schemas.items():
                print(f"\n{name}:")
                print(json.dumps(schema, indent=2))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
