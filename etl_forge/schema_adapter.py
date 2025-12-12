"""
Schema adapter module for converting established schema standards to ETLForge format.

This module provides adapters for:
- Frictionless Table Schema (https://specs.frictionlessdata.io/table-schema/)
- JSON Schema (https://json-schema.org/)

These adapters allow ETLForge to consume schemas defined in widely-adopted
standards, improving interoperability with other data tools.
"""

from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import yaml
from .exceptions import ETLForgeError


class SchemaAdapter:
    """
    Base class for schema adapters.
    
    Schema adapters convert schemas from established standards
    to ETLForge's internal format.
    """
    
    @staticmethod
    def detect_schema_type(schema: Dict[str, Any]) -> str:
        """
        Detect the type of schema based on its structure.
        
        Args:
            schema: A dictionary containing the schema definition.
            
        Returns:
            One of: 'etlforge', 'frictionless', 'jsonschema', or 'unknown'
        """
        if not isinstance(schema, dict):
            return 'unknown'
        
        # ETLForge native format
        if 'fields' in schema and isinstance(schema.get('fields'), list):
            # Check if it looks like ETLForge format (has 'type' with our types)
            fields = schema['fields']
            if fields and isinstance(fields[0], dict):
                first_field = fields[0]
                if 'type' in first_field:
                    etlforge_types = {'int', 'float', 'string', 'date', 'category'}
                    if first_field['type'] in etlforge_types:
                        return 'etlforge'
                    # Frictionless uses different type names
                    frictionless_types = {'integer', 'number', 'boolean', 'object', 
                                          'array', 'datetime', 'time', 'year', 
                                          'yearmonth', 'duration', 'geopoint', 'geojson'}
                    if first_field['type'] in frictionless_types or first_field['type'] == 'string':
                        # Could be either, check for frictionless-specific fields
                        if any(key in first_field for key in ['constraints', 'format', 'rdfType']):
                            return 'frictionless'
                        # Check if it has ETLForge-specific fields
                        if any(key in first_field for key in ['range', 'faker_template', 'null_rate', 'values']):
                            return 'etlforge'
                        return 'frictionless'  # Default to frictionless if unclear
        
        # JSON Schema format
        if '$schema' in schema or 'properties' in schema:
            return 'jsonschema'
        
        return 'unknown'
    
    @staticmethod
    def load_and_convert(schema_path: Union[str, Path, dict]) -> Dict[str, Any]:
        """
        Load a schema from a file or dict and convert to ETLForge format.
        
        This method auto-detects the schema type and applies the appropriate
        conversion.
        
        Args:
            schema_path: The path to a schema file or a dictionary.
            
        Returns:
            A schema dictionary in ETLForge format.
            
        Raises:
            ETLForgeError: If the schema cannot be loaded or converted.
        """
        if isinstance(schema_path, dict):
            schema = schema_path
        else:
            schema_path_obj = Path(schema_path)
            if not schema_path_obj.exists():
                raise ETLForgeError(f"Schema file not found at: {schema_path}")
            
            suffix = schema_path_obj.suffix.lower()
            try:
                with open(schema_path_obj, "r", encoding="utf-8") as file:
                    if suffix in [".yaml", ".yml"]:
                        schema = yaml.safe_load(file) or {}
                    elif suffix == ".json":
                        schema = json.load(file) or {}
                    else:
                        raise ETLForgeError(f"Unsupported schema file format: {suffix}")
            except (IOError, yaml.YAMLError, json.JSONDecodeError) as e:
                raise ETLForgeError(f"Failed to load or parse schema file: {e}") from e
        
        schema_type = SchemaAdapter.detect_schema_type(schema)
        
        if schema_type == 'etlforge':
            return schema
        elif schema_type == 'frictionless':
            return FrictionlessAdapter.convert(schema)
        elif schema_type == 'jsonschema':
            return JsonSchemaAdapter.convert(schema)
        else:
            # Try to use as-is, validation will catch issues
            return schema


class FrictionlessAdapter:
    """
    Adapter for Frictionless Table Schema.
    
    Frictionless Table Schema is a standard for describing tabular data.
    Spec: https://specs.frictionlessdata.io/table-schema/
    
    Supported Frictionless types and their ETLForge mappings:
    - integer -> int
    - number -> float
    - string -> string
    - date/datetime/time -> date
    - boolean -> category (with values [True, False])
    - array/object -> Not supported (raises error)
    
    Supported constraints:
    - required -> nullable (inverted)
    - unique -> unique
    - minimum/maximum -> range.min/range.max
    - minLength/maxLength -> length.min/length.max
    - enum -> values (for category type)
    - pattern -> Not directly supported (logged as warning)
    """
    
    # Type mapping from Frictionless to ETLForge
    TYPE_MAP = {
        'integer': 'int',
        'number': 'float',
        'string': 'string',
        'date': 'date',
        'datetime': 'date',
        'time': 'date',
        'boolean': 'category',
        'year': 'int',
        'yearmonth': 'string',
    }
    
    @classmethod
    def convert(cls, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a Frictionless Table Schema to ETLForge format.
        
        Args:
            schema: A Frictionless Table Schema dictionary.
            
        Returns:
            An ETLForge-compatible schema dictionary.
            
        Raises:
            ETLForgeError: If the schema contains unsupported types.
        """
        if not isinstance(schema, dict):
            raise ETLForgeError("Frictionless schema must be a dictionary")
        
        if 'fields' not in schema:
            raise ETLForgeError("Frictionless schema must contain 'fields' key")
        
        etl_fields = []
        
        for field in schema['fields']:
            etl_field = cls._convert_field(field)
            etl_fields.append(etl_field)
        
        etl_schema = {'fields': etl_fields}
        
        # Preserve any metadata
        if 'missingValues' in schema:
            etl_schema['_frictionless_missingValues'] = schema['missingValues']
        if 'primaryKey' in schema:
            etl_schema['_frictionless_primaryKey'] = schema['primaryKey']
        
        return etl_schema
    
    @classmethod
    def _convert_field(cls, field: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single Frictionless field to ETLForge format."""
        if not isinstance(field, dict):
            raise ETLForgeError("Each field must be a dictionary")
        
        if 'name' not in field:
            raise ETLForgeError("Each field must have a 'name' property")
        
        name = field['name']
        frictionless_type = field.get('type', 'string')
        
        # Check for unsupported types
        if frictionless_type in ['array', 'object', 'geopoint', 'geojson', 'duration']:
            raise ETLForgeError(
                f"Field '{name}' has unsupported Frictionless type '{frictionless_type}'. "
                f"ETLForge only supports tabular data types."
            )
        
        # Map the type
        etl_type = cls.TYPE_MAP.get(frictionless_type, 'string')
        
        etl_field: Dict[str, Any] = {
            'name': name,
            'type': etl_type,
        }
        
        # Handle constraints
        constraints = field.get('constraints', {})
        
        # Required/nullable (inverted logic)
        if 'required' in constraints:
            etl_field['nullable'] = not constraints['required']
        else:
            etl_field['nullable'] = True
        
        # Unique constraint
        if constraints.get('unique'):
            etl_field['unique'] = True
        
        # Numeric range constraints
        if etl_type in ['int', 'float']:
            range_config = {}
            if 'minimum' in constraints:
                range_config['min'] = constraints['minimum']
            if 'maximum' in constraints:
                range_config['max'] = constraints['maximum']
            if range_config:
                etl_field['range'] = range_config
        
        # String length constraints
        if etl_type == 'string':
            length_config = {}
            if 'minLength' in constraints:
                length_config['min'] = constraints['minLength']
            if 'maxLength' in constraints:
                length_config['max'] = constraints['maxLength']
            if length_config:
                etl_field['length'] = length_config
        
        # Enum values (converts to category type)
        if 'enum' in constraints:
            etl_field['type'] = 'category'
            etl_field['values'] = constraints['enum']
        
        # Boolean type special handling
        if frictionless_type == 'boolean':
            etl_field['values'] = ['true', 'false']
        
        # Date format handling
        if etl_type == 'date' and 'format' in field:
            # Frictionless uses different format strings, try to convert common ones
            frictionless_format = field['format']
            etl_field['format'] = cls._convert_date_format(frictionless_format)
        
        # Handle date range (Frictionless doesn't have this, but check for constraints)
        if etl_type == 'date':
            range_config = {}
            if 'minimum' in constraints:
                range_config['start'] = str(constraints['minimum'])
            if 'maximum' in constraints:
                range_config['end'] = str(constraints['maximum'])
            if range_config:
                etl_field['range'] = range_config
        
        # Preserve description as a comment
        if 'description' in field:
            etl_field['_description'] = field['description']
        
        return etl_field
    
    @staticmethod
    def _convert_date_format(frictionless_format: str) -> str:
        """Convert Frictionless date format to Python strftime format."""
        # Frictionless uses 'default' for ISO 8601 or custom patterns
        format_map = {
            'default': '%Y-%m-%d',
            'any': '%Y-%m-%d',
            '%Y-%m-%d': '%Y-%m-%d',
            '%Y/%m/%d': '%Y/%m/%d',
            '%d-%m-%Y': '%d-%m-%Y',
            '%d/%m/%Y': '%d/%m/%Y',
            '%m/%d/%Y': '%m/%d/%Y',
        }
        return format_map.get(frictionless_format, '%Y-%m-%d')
    
    @classmethod
    def to_frictionless(cls, etl_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert an ETLForge schema to Frictionless Table Schema format.
        
        Args:
            etl_schema: An ETLForge schema dictionary.
            
        Returns:
            A Frictionless Table Schema dictionary.
        """
        if 'fields' not in etl_schema:
            raise ETLForgeError("ETLForge schema must contain 'fields' key")
        
        # Reverse type mapping
        reverse_type_map = {
            'int': 'integer',
            'float': 'number',
            'string': 'string',
            'date': 'date',
            'category': 'string',
        }
        
        frictionless_fields = []
        
        for field in etl_schema['fields']:
            etl_type = field.get('type', 'string')
            frictionless_type = reverse_type_map.get(etl_type, 'string')
            
            fl_field: Dict[str, Any] = {
                'name': field['name'],
                'type': frictionless_type,
            }
            
            constraints: Dict[str, Any] = {}
            
            # Nullable -> required (inverted)
            if 'nullable' in field:
                constraints['required'] = not field['nullable']
            
            # Unique
            if field.get('unique'):
                constraints['unique'] = True
            
            # Range constraints
            if 'range' in field:
                if 'min' in field['range']:
                    constraints['minimum'] = field['range']['min']
                if 'max' in field['range']:
                    constraints['maximum'] = field['range']['max']
            
            # Length constraints
            if 'length' in field:
                if 'min' in field['length']:
                    constraints['minLength'] = field['length']['min']
                if 'max' in field['length']:
                    constraints['maxLength'] = field['length']['max']
            
            # Category values -> enum
            if etl_type == 'category' and 'values' in field:
                constraints['enum'] = field['values']
            
            if constraints:
                fl_field['constraints'] = constraints
            
            # Date format
            if etl_type == 'date' and 'format' in field:
                fl_field['format'] = field['format']
            
            # Description
            if '_description' in field:
                fl_field['description'] = field['_description']
            
            frictionless_fields.append(fl_field)
        
        return {'fields': frictionless_fields}


class JsonSchemaAdapter:
    """
    Adapter for JSON Schema.
    
    JSON Schema is a widely-adopted standard for describing JSON data.
    Spec: https://json-schema.org/
    
    This adapter supports JSON Schema Draft-07 and later for describing
    tabular data where each row is an object with properties.
    
    Supported JSON Schema types and their ETLForge mappings:
    - integer -> int
    - number -> float  
    - string -> string (or date if format is date/date-time)
    - boolean -> category (with values [true, false])
    - array/object -> Not supported as field types
    
    Supported keywords:
    - required -> nullable (inverted)
    - minimum/maximum -> range.min/range.max
    - exclusiveMinimum/exclusiveMaximum -> adjusted range
    - minLength/maxLength -> length.min/length.max
    - enum -> category type with values
    - format (date, date-time, email, etc.) -> type hints
    """
    
    TYPE_MAP = {
        'integer': 'int',
        'number': 'float',
        'string': 'string',
        'boolean': 'category',
    }
    
    @classmethod
    def convert(cls, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a JSON Schema to ETLForge format.
        
        Args:
            schema: A JSON Schema dictionary describing a tabular row structure.
            
        Returns:
            An ETLForge-compatible schema dictionary.
            
        Raises:
            ETLForgeError: If the schema cannot be converted.
        """
        if not isinstance(schema, dict):
            raise ETLForgeError("JSON Schema must be a dictionary")
        
        # JSON Schema should have 'properties' for object schemas
        if 'properties' not in schema:
            raise ETLForgeError(
                "JSON Schema must contain 'properties' key describing row fields"
            )
        
        properties = schema['properties']
        required_fields = set(schema.get('required', []))
        
        etl_fields = []
        
        # Process properties in order if possible
        property_order = schema.get('propertyOrder', list(properties.keys()))
        
        for prop_name in property_order:
            if prop_name not in properties:
                continue
            prop_schema = properties[prop_name]
            is_required = prop_name in required_fields
            etl_field = cls._convert_property(prop_name, prop_schema, is_required)
            etl_fields.append(etl_field)
        
        return {'fields': etl_fields}
    
    @classmethod
    def _convert_property(
        cls, 
        name: str, 
        prop_schema: Dict[str, Any],
        is_required: bool
    ) -> Dict[str, Any]:
        """Convert a single JSON Schema property to an ETLForge field."""
        if not isinstance(prop_schema, dict):
            raise ETLForgeError(f"Property '{name}' must have a schema object")
        
        # Handle $ref (not fully supported, just note it)
        if '$ref' in prop_schema:
            raise ETLForgeError(
                f"Property '{name}' uses $ref which is not supported. "
                f"Please dereference the schema first."
            )
        
        # Get the JSON Schema type
        json_type = prop_schema.get('type', 'string')
        
        # Handle type arrays (e.g., ["string", "null"])
        if isinstance(json_type, list):
            # Filter out 'null' and use the first real type
            non_null_types = [t for t in json_type if t != 'null']
            is_nullable = 'null' in json_type
            json_type = non_null_types[0] if non_null_types else 'string'
        else:
            is_nullable = not is_required
        
        # Check for unsupported types
        if json_type in ['array', 'object']:
            raise ETLForgeError(
                f"Property '{name}' has unsupported type '{json_type}'. "
                f"ETLForge only supports tabular data types."
            )
        
        # Map the type
        etl_type = cls.TYPE_MAP.get(json_type, 'string')
        
        # Check for date format
        if json_type == 'string' and 'format' in prop_schema:
            format_val = prop_schema['format']
            if format_val in ['date', 'date-time']:
                etl_type = 'date'
        
        etl_field: Dict[str, Any] = {
            'name': name,
            'type': etl_type,
            'nullable': is_nullable,
        }
        
        # Numeric range constraints
        if etl_type in ['int', 'float']:
            range_config: Dict[str, Any] = {}
            if 'minimum' in prop_schema:
                range_config['min'] = prop_schema['minimum']
            if 'maximum' in prop_schema:
                range_config['max'] = prop_schema['maximum']
            if 'exclusiveMinimum' in prop_schema:
                # Add 1 for int, small amount for float
                if etl_type == 'int':
                    range_config['min'] = prop_schema['exclusiveMinimum'] + 1
                else:
                    range_config['min'] = prop_schema['exclusiveMinimum'] + 0.0001
            if 'exclusiveMaximum' in prop_schema:
                if etl_type == 'int':
                    range_config['max'] = prop_schema['exclusiveMaximum'] - 1
                else:
                    range_config['max'] = prop_schema['exclusiveMaximum'] - 0.0001
            if range_config:
                etl_field['range'] = range_config
        
        # String length constraints
        if json_type == 'string':
            length_config: Dict[str, Any] = {}
            if 'minLength' in prop_schema:
                length_config['min'] = prop_schema['minLength']
            if 'maxLength' in prop_schema:
                length_config['max'] = prop_schema['maxLength']
            if length_config:
                etl_field['length'] = length_config
        
        # Enum values
        if 'enum' in prop_schema:
            etl_field['type'] = 'category'
            etl_field['values'] = prop_schema['enum']
        
        # Boolean handling
        if json_type == 'boolean':
            etl_field['values'] = ['true', 'false']
        
        # Date format handling
        if etl_type == 'date':
            format_val = prop_schema.get('format', 'date')
            if format_val == 'date-time':
                etl_field['format'] = '%Y-%m-%dT%H:%M:%S'
            else:
                etl_field['format'] = '%Y-%m-%d'
        
        # String format hints for faker
        if json_type == 'string' and 'format' in prop_schema:
            format_val = prop_schema['format']
            faker_map = {
                'email': 'email',
                'uri': 'url',
                'hostname': 'hostname',
                'ipv4': 'ipv4',
                'ipv6': 'ipv6',
                'uuid': 'uuid4',
            }
            if format_val in faker_map:
                etl_field['faker_template'] = faker_map[format_val]
        
        # Description
        if 'description' in prop_schema:
            etl_field['_description'] = prop_schema['description']
        
        # Title
        if 'title' in prop_schema:
            etl_field['_title'] = prop_schema['title']
        
        return etl_field
    
    @classmethod
    def to_jsonschema(cls, etl_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert an ETLForge schema to JSON Schema format.
        
        Args:
            etl_schema: An ETLForge schema dictionary.
            
        Returns:
            A JSON Schema dictionary.
        """
        if 'fields' not in etl_schema:
            raise ETLForgeError("ETLForge schema must contain 'fields' key")
        
        # Reverse type mapping
        reverse_type_map = {
            'int': 'integer',
            'float': 'number',
            'string': 'string',
            'date': 'string',
            'category': 'string',
        }
        
        properties: Dict[str, Any] = {}
        required: List[str] = []
        property_order: List[str] = []
        
        for field in etl_schema['fields']:
            name = field['name']
            etl_type = field.get('type', 'string')
            json_type = reverse_type_map.get(etl_type, 'string')
            
            prop: Dict[str, Any] = {
                'type': json_type,
            }
            
            # Nullable handling
            if field.get('nullable', False):
                prop['type'] = [json_type, 'null']
            else:
                required.append(name)
            
            # Range constraints
            if 'range' in field:
                if 'min' in field['range']:
                    prop['minimum'] = field['range']['min']
                if 'max' in field['range']:
                    prop['maximum'] = field['range']['max']
            
            # Length constraints
            if 'length' in field:
                if 'min' in field['length']:
                    prop['minLength'] = field['length']['min']
                if 'max' in field['length']:
                    prop['maxLength'] = field['length']['max']
            
            # Category values -> enum
            if etl_type == 'category' and 'values' in field:
                prop['enum'] = field['values']
            
            # Date format
            if etl_type == 'date':
                prop['format'] = 'date'
            
            # Faker template hints
            if 'faker_template' in field:
                faker_format_map = {
                    'email': 'email',
                    'url': 'uri',
                    'hostname': 'hostname',
                    'ipv4': 'ipv4',
                    'ipv6': 'ipv6',
                    'uuid4': 'uuid',
                }
                if field['faker_template'] in faker_format_map:
                    prop['format'] = faker_format_map[field['faker_template']]
            
            # Description
            if '_description' in field:
                prop['description'] = field['_description']
            
            # Title
            if '_title' in field:
                prop['title'] = field['_title']
            
            properties[name] = prop
            property_order.append(name)
        
        json_schema: Dict[str, Any] = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            'type': 'object',
            'properties': properties,
            'propertyOrder': property_order,
        }
        
        if required:
            json_schema['required'] = required
        
        return json_schema
