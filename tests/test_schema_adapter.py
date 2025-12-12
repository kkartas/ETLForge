"""
Tests for schema adapter module.

Tests for converting Frictionless Table Schema and JSON Schema to ETLForge format.
"""

import pytest
from etl_forge.schema_adapter import (
    SchemaAdapter,
    FrictionlessAdapter,
    JsonSchemaAdapter,
)
from etl_forge.exceptions import ETLForgeError
from etl_forge import DataGenerator, DataValidator


class TestSchemaAdapter:
    """Tests for SchemaAdapter class."""

    def test_detect_etlforge_schema(self):
        """Test detection of ETLForge native schema."""
        schema = {
            "fields": [
                {"name": "id", "type": "int", "nullable": False},
                {"name": "name", "type": "string"},
            ]
        }
        assert SchemaAdapter.detect_schema_type(schema) == "etlforge"

    def test_detect_etlforge_with_range(self):
        """Test detection of ETLForge schema with range constraint."""
        schema = {
            "fields": [
                {"name": "id", "type": "int", "range": {"min": 1, "max": 100}},
            ]
        }
        assert SchemaAdapter.detect_schema_type(schema) == "etlforge"

    def test_detect_etlforge_with_faker(self):
        """Test detection of ETLForge schema with faker template."""
        schema = {
            "fields": [
                {"name": "email", "type": "string", "faker_template": "email"},
            ]
        }
        assert SchemaAdapter.detect_schema_type(schema) == "etlforge"

    def test_detect_frictionless_schema(self):
        """Test detection of Frictionless Table Schema."""
        schema = {
            "fields": [
                {"name": "id", "type": "integer", "constraints": {"required": True}},
                {"name": "name", "type": "string"},
            ]
        }
        assert SchemaAdapter.detect_schema_type(schema) == "frictionless"

    def test_detect_jsonschema(self):
        """Test detection of JSON Schema."""
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
        }
        assert SchemaAdapter.detect_schema_type(schema) == "jsonschema"

    def test_detect_jsonschema_without_schema_key(self):
        """Test detection of JSON Schema without $schema key."""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
        }
        assert SchemaAdapter.detect_schema_type(schema) == "jsonschema"

    def test_detect_unknown_schema(self):
        """Test detection returns unknown for unrecognized format."""
        schema = {"random": "data"}
        assert SchemaAdapter.detect_schema_type(schema) == "unknown"

    def test_detect_non_dict_returns_unknown(self):
        """Test detection returns unknown for non-dict input."""
        assert SchemaAdapter.detect_schema_type([1, 2, 3]) == "unknown"
        assert SchemaAdapter.detect_schema_type("string") == "unknown"

    def test_load_and_convert_etlforge(self):
        """Test load_and_convert passes through ETLForge schemas."""
        schema = {
            "fields": [
                {"name": "id", "type": "int", "nullable": False},
            ]
        }
        result = SchemaAdapter.load_and_convert(schema)
        assert result == schema

    def test_load_and_convert_frictionless(self):
        """Test load_and_convert converts Frictionless schemas."""
        frictionless_schema = {
            "fields": [
                {"name": "id", "type": "integer", "constraints": {"required": True}},
            ]
        }
        result = SchemaAdapter.load_and_convert(frictionless_schema)
        assert result["fields"][0]["type"] == "int"
        assert result["fields"][0]["nullable"] == False

    def test_load_and_convert_jsonschema(self):
        """Test load_and_convert converts JSON Schema."""
        json_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
            },
            "required": ["id"],
        }
        result = SchemaAdapter.load_and_convert(json_schema)
        assert result["fields"][0]["type"] == "int"
        assert result["fields"][0]["name"] == "id"


class TestFrictionlessAdapter:
    """Tests for FrictionlessAdapter class."""

    def test_convert_basic_schema(self):
        """Test conversion of basic Frictionless schema."""
        frictionless = {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
                {"name": "price", "type": "number"},
                {"name": "created", "type": "date"},
            ]
        }
        result = FrictionlessAdapter.convert(frictionless)
        
        assert len(result["fields"]) == 4
        assert result["fields"][0]["type"] == "int"
        assert result["fields"][1]["type"] == "string"
        assert result["fields"][2]["type"] == "float"
        assert result["fields"][3]["type"] == "date"

    def test_convert_with_constraints(self):
        """Test conversion of Frictionless schema with constraints."""
        frictionless = {
            "fields": [
                {
                    "name": "id",
                    "type": "integer",
                    "constraints": {
                        "required": True,
                        "unique": True,
                        "minimum": 1,
                        "maximum": 1000,
                    },
                },
                {
                    "name": "username",
                    "type": "string",
                    "constraints": {
                        "minLength": 3,
                        "maxLength": 20,
                    },
                },
            ]
        }
        result = FrictionlessAdapter.convert(frictionless)
        
        id_field = result["fields"][0]
        assert id_field["nullable"] == False
        assert id_field["unique"] == True
        assert id_field["range"]["min"] == 1
        assert id_field["range"]["max"] == 1000
        
        username_field = result["fields"][1]
        assert username_field["length"]["min"] == 3
        assert username_field["length"]["max"] == 20

    def test_convert_enum_to_category(self):
        """Test conversion of enum constraint to category type."""
        frictionless = {
            "fields": [
                {
                    "name": "status",
                    "type": "string",
                    "constraints": {
                        "enum": ["active", "inactive", "pending"],
                    },
                },
            ]
        }
        result = FrictionlessAdapter.convert(frictionless)
        
        assert result["fields"][0]["type"] == "category"
        assert result["fields"][0]["values"] == ["active", "inactive", "pending"]

    def test_convert_boolean(self):
        """Test conversion of boolean type."""
        frictionless = {
            "fields": [
                {"name": "is_active", "type": "boolean"},
            ]
        }
        result = FrictionlessAdapter.convert(frictionless)
        
        assert result["fields"][0]["type"] == "category"
        assert result["fields"][0]["values"] == ["true", "false"]

    def test_convert_date_format(self):
        """Test conversion of date format."""
        frictionless = {
            "fields": [
                {"name": "created", "type": "date", "format": "default"},
            ]
        }
        result = FrictionlessAdapter.convert(frictionless)
        
        assert result["fields"][0]["type"] == "date"
        assert result["fields"][0]["format"] == "%Y-%m-%d"

    def test_convert_year_type(self):
        """Test conversion of year type to int."""
        frictionless = {
            "fields": [
                {"name": "birth_year", "type": "year"},
            ]
        }
        result = FrictionlessAdapter.convert(frictionless)
        
        assert result["fields"][0]["type"] == "int"

    def test_convert_preserves_description(self):
        """Test that description is preserved."""
        frictionless = {
            "fields": [
                {
                    "name": "id",
                    "type": "integer",
                    "description": "Primary identifier",
                },
            ]
        }
        result = FrictionlessAdapter.convert(frictionless)
        
        assert result["fields"][0]["_description"] == "Primary identifier"

    def test_convert_rejects_unsupported_types(self):
        """Test that unsupported types raise errors."""
        frictionless = {
            "fields": [
                {"name": "data", "type": "object"},
            ]
        }
        with pytest.raises(ETLForgeError, match="unsupported Frictionless type"):
            FrictionlessAdapter.convert(frictionless)

    def test_convert_rejects_array_type(self):
        """Test that array type raises error."""
        frictionless = {
            "fields": [
                {"name": "items", "type": "array"},
            ]
        }
        with pytest.raises(ETLForgeError, match="unsupported Frictionless type"):
            FrictionlessAdapter.convert(frictionless)

    def test_convert_missing_fields_key(self):
        """Test error when fields key is missing."""
        frictionless = {"name": "test"}
        with pytest.raises(ETLForgeError, match="must contain 'fields' key"):
            FrictionlessAdapter.convert(frictionless)

    def test_convert_missing_field_name(self):
        """Test error when field name is missing."""
        frictionless = {
            "fields": [
                {"type": "integer"},
            ]
        }
        with pytest.raises(ETLForgeError, match="must have a 'name' property"):
            FrictionlessAdapter.convert(frictionless)

    def test_to_frictionless_roundtrip(self):
        """Test conversion to Frictionless format."""
        etl_schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "int",
                    "nullable": False,
                    "unique": True,
                    "range": {"min": 1, "max": 100},
                },
                {
                    "name": "status",
                    "type": "category",
                    "values": ["active", "inactive"],
                },
            ]
        }
        result = FrictionlessAdapter.to_frictionless(etl_schema)
        
        assert result["fields"][0]["type"] == "integer"
        assert result["fields"][0]["constraints"]["required"] == True
        assert result["fields"][0]["constraints"]["unique"] == True
        assert result["fields"][0]["constraints"]["minimum"] == 1
        assert result["fields"][0]["constraints"]["maximum"] == 100
        
        assert result["fields"][1]["constraints"]["enum"] == ["active", "inactive"]


class TestJsonSchemaAdapter:
    """Tests for JsonSchemaAdapter class."""

    def test_convert_basic_schema(self):
        """Test conversion of basic JSON Schema."""
        json_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "price": {"type": "number"},
            },
            "required": ["id"],
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        fields_by_name = {f["name"]: f for f in result["fields"]}
        assert fields_by_name["id"]["type"] == "int"
        assert fields_by_name["id"]["nullable"] == False
        assert fields_by_name["name"]["type"] == "string"
        assert fields_by_name["name"]["nullable"] == True
        assert fields_by_name["price"]["type"] == "float"

    def test_convert_with_range_constraints(self):
        """Test conversion of numeric constraints."""
        json_schema = {
            "type": "object",
            "properties": {
                "age": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 120,
                },
                "score": {
                    "type": "number",
                    "exclusiveMinimum": 0,
                    "exclusiveMaximum": 100,
                },
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        fields_by_name = {f["name"]: f for f in result["fields"]}
        assert fields_by_name["age"]["range"]["min"] == 0
        assert fields_by_name["age"]["range"]["max"] == 120
        assert fields_by_name["score"]["range"]["min"] == 0.0001
        assert fields_by_name["score"]["range"]["max"] == 99.9999

    def test_convert_string_length_constraints(self):
        """Test conversion of string length constraints."""
        json_schema = {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 20,
                },
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        assert result["fields"][0]["length"]["min"] == 3
        assert result["fields"][0]["length"]["max"] == 20

    def test_convert_enum(self):
        """Test conversion of enum to category."""
        json_schema = {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "pending"],
                },
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        assert result["fields"][0]["type"] == "category"
        assert result["fields"][0]["values"] == ["active", "inactive", "pending"]

    def test_convert_boolean(self):
        """Test conversion of boolean type."""
        json_schema = {
            "type": "object",
            "properties": {
                "is_active": {"type": "boolean"},
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        assert result["fields"][0]["type"] == "category"
        assert result["fields"][0]["values"] == ["true", "false"]

    def test_convert_date_format(self):
        """Test conversion of date format."""
        json_schema = {
            "type": "object",
            "properties": {
                "created": {"type": "string", "format": "date"},
                "updated": {"type": "string", "format": "date-time"},
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        fields_by_name = {f["name"]: f for f in result["fields"]}
        assert fields_by_name["created"]["type"] == "date"
        assert fields_by_name["created"]["format"] == "%Y-%m-%d"
        assert fields_by_name["updated"]["type"] == "date"
        assert fields_by_name["updated"]["format"] == "%Y-%m-%dT%H:%M:%S"

    def test_convert_email_format(self):
        """Test conversion of email format to faker template."""
        json_schema = {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        assert result["fields"][0]["faker_template"] == "email"

    def test_convert_nullable_type_array(self):
        """Test conversion of nullable type arrays."""
        json_schema = {
            "type": "object",
            "properties": {
                "name": {"type": ["string", "null"]},
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        assert result["fields"][0]["type"] == "string"
        assert result["fields"][0]["nullable"] == True

    def test_convert_preserves_description(self):
        """Test that description and title are preserved."""
        json_schema = {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer",
                    "title": "User ID",
                    "description": "Unique identifier for the user",
                },
            },
        }
        result = JsonSchemaAdapter.convert(json_schema)
        
        assert result["fields"][0]["_title"] == "User ID"
        assert result["fields"][0]["_description"] == "Unique identifier for the user"

    def test_convert_rejects_array_type(self):
        """Test that array type raises error."""
        json_schema = {
            "type": "object",
            "properties": {
                "items": {"type": "array"},
            },
        }
        with pytest.raises(ETLForgeError, match="unsupported type"):
            JsonSchemaAdapter.convert(json_schema)

    def test_convert_rejects_object_type(self):
        """Test that nested object type raises error."""
        json_schema = {
            "type": "object",
            "properties": {
                "address": {"type": "object"},
            },
        }
        with pytest.raises(ETLForgeError, match="unsupported type"):
            JsonSchemaAdapter.convert(json_schema)

    def test_convert_rejects_ref(self):
        """Test that $ref raises error."""
        json_schema = {
            "type": "object",
            "properties": {
                "address": {"$ref": "#/definitions/Address"},
            },
        }
        with pytest.raises(ETLForgeError, match="\\$ref.*not supported"):
            JsonSchemaAdapter.convert(json_schema)

    def test_convert_missing_properties(self):
        """Test error when properties key is missing."""
        json_schema = {"type": "object"}
        with pytest.raises(ETLForgeError, match="must contain 'properties'"):
            JsonSchemaAdapter.convert(json_schema)

    def test_to_jsonschema(self):
        """Test conversion to JSON Schema format."""
        etl_schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "int",
                    "nullable": False,
                    "range": {"min": 1, "max": 100},
                },
                {
                    "name": "email",
                    "type": "string",
                    "faker_template": "email",
                },
                {
                    "name": "status",
                    "type": "category",
                    "values": ["active", "inactive"],
                },
            ]
        }
        result = JsonSchemaAdapter.to_jsonschema(etl_schema)
        
        assert result["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert result["type"] == "object"
        assert "id" in result["required"]
        assert result["properties"]["id"]["type"] == "integer"
        assert result["properties"]["id"]["minimum"] == 1
        assert result["properties"]["id"]["maximum"] == 100
        assert result["properties"]["email"]["format"] == "email"
        assert result["properties"]["status"]["enum"] == ["active", "inactive"]


class TestIntegrationWithGeneratorValidator:
    """Integration tests for using adapters with DataGenerator and DataValidator."""

    def test_generator_with_frictionless_schema(self):
        """Test DataGenerator works with Frictionless Table Schema."""
        frictionless_schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "integer",
                    "constraints": {"required": True, "minimum": 1, "maximum": 100},
                },
                {
                    "name": "status",
                    "type": "string",
                    "constraints": {"required": True, "enum": ["active", "inactive"]},
                },
            ]
        }
        generator = DataGenerator(frictionless_schema)
        df = generator.generate_data(10)
        
        assert len(df) == 10
        assert "id" in df.columns
        assert "status" in df.columns
        assert df["id"].between(1, 100).all()
        assert df["status"].isin(["active", "inactive"]).all()

    def test_generator_with_jsonschema(self):
        """Test DataGenerator works with JSON Schema."""
        json_schema = {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                },
                "role": {
                    "type": "string",
                    "enum": ["admin", "user", "guest"],
                },
            },
            "required": ["user_id", "role"],
        }
        generator = DataGenerator(json_schema)
        df = generator.generate_data(10)
        
        assert len(df) == 10
        assert "user_id" in df.columns
        assert "role" in df.columns
        assert df["user_id"].between(1, 1000).all()
        assert df["role"].isin(["admin", "user", "guest"]).all()

    def test_validator_with_frictionless_schema(self):
        """Test DataValidator works with Frictionless Table Schema."""
        import pandas as pd
        
        frictionless_schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "integer",
                    "constraints": {"required": True},
                },
                {
                    "name": "name",
                    "type": "string",
                },
            ]
        }
        
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        })
        
        validator = DataValidator(frictionless_schema)
        result = validator.validate(df)
        
        assert result.is_valid

    def test_validator_with_jsonschema(self):
        """Test DataValidator works with JSON Schema."""
        import pandas as pd
        
        json_schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
            },
            "required": ["id"],
        }
        
        df = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
        })
        
        validator = DataValidator(json_schema)
        result = validator.validate(df)
        
        assert result.is_valid

    def test_roundtrip_frictionless_generation_validation(self):
        """Test generating and validating with Frictionless schema."""
        frictionless_schema = {
            "fields": [
                {
                    "name": "id",
                    "type": "integer",
                    "constraints": {"required": True, "minimum": 1, "maximum": 100},
                },
                {
                    "name": "status",
                    "type": "string",
                    "constraints": {"enum": ["active", "inactive"]},
                },
            ]
        }
        
        generator = DataGenerator(frictionless_schema)
        df = generator.generate_data(50)
        
        validator = DataValidator(frictionless_schema)
        result = validator.validate(df)
        
        assert result.is_valid

    def test_roundtrip_jsonschema_generation_validation(self):
        """Test generating and validating with JSON Schema."""
        json_schema = {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 1000,
                },
                "email": {
                    "type": "string",
                    "format": "email",
                },
                "role": {
                    "type": "string",
                    "enum": ["admin", "user", "guest"],
                },
            },
            "required": ["user_id", "role"],
        }
        
        generator = DataGenerator(json_schema)
        df = generator.generate_data(50)
        
        validator = DataValidator(json_schema)
        result = validator.validate(df)
        
        assert result.is_valid
