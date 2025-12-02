"""
Tests for Faker integration and unique constraint enforcement.
"""

import pytest
from etl_forge.generator import DataGenerator
from etl_forge.exceptions import ETLForgeError


class TestFakerIntegration:
    """Test cases for Faker template integration."""

    def test_unique_faker_email(self):
        """Test unique email generation with Faker."""
        schema = {
            "fields": [
                {
                    "name": "email",
                    "type": "string",
                    "unique": True,
                    "faker_template": "email",
                }
            ]
        }
        generator = DataGenerator(schema)
        df = generator.generate_data(100)

        # All emails should be unique
        assert df["email"].nunique() == 100
        assert len(df) == 100

    def test_unique_faker_name(self):
        """Test unique name generation with Faker."""
        schema = {
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                    "unique": True,
                    "faker_template": "name",
                }
            ]
        }
        generator = DataGenerator(schema)
        df = generator.generate_data(50)

        assert df["name"].nunique() == 50

    def test_non_unique_faker_values(self):
        """Test non-unique Faker values (should allow duplicates)."""
        schema = {
            "fields": [
                {
                    "name": "color",
                    "type": "string",
                    "unique": False,
                    "faker_template": "color_name",
                }
            ]
        }
        generator = DataGenerator(schema)
        df = generator.generate_data(100)

        # Should generate data, duplicates are allowed
        assert len(df) == 100

    def test_faker_invalid_template_with_unique(self):
        """Test that invalid Faker template falls back to random strings with unique constraint."""
        schema = {
            "fields": [
                {
                    "name": "field",
                    "type": "string",
                    "unique": True,
                    "faker_template": "nonexistent_faker_method",
                    "length": {"min": 10, "max": 15},
                }
            ]
        }
        generator = DataGenerator(schema)
        df = generator.generate_data(50)

        # Should fall back to random strings
        assert len(df) == 50
        assert df["field"].nunique() == 50
        # Check string length
        assert all(10 <= len(val) <= 15 for val in df["field"])

    def test_faker_invalid_template_non_unique(self):
        """Test that invalid Faker template falls back to random strings without unique constraint."""
        schema = {
            "fields": [
                {
                    "name": "field",
                    "type": "string",
                    "unique": False,
                    "faker_template": "nonexistent_faker_method",
                    "length": {"min": 8, "max": 12},
                }
            ]
        }
        generator = DataGenerator(schema)
        df = generator.generate_data(30)

        assert len(df) == 30
        assert all(8 <= len(val) <= 12 for val in df["field"])

    def test_unique_faker_insufficient_variety(self):
        """Test error when Faker cannot generate enough unique values."""
        # Use a non-existent faker method to trigger the fallback,
        # but set max_attempts low enough to fail
        schema = {
            "fields": [
                {
                    "name": "limited_str",
                    "type": "string",
                    "unique": True,
                    "faker_template": "nonexistent_method_that_will_fallback",
                    "length": {
                        "min": 1,
                        "max": 2,
                    },  # Very short strings, limited variety
                }
            ]
        }
        generator = DataGenerator(schema)

        # Should fail - can't generate 10000 unique 1-2 character strings
        # Max possible: 62 (1-char) + 62*62 (2-char) = 3906 unique values
        with pytest.raises(
            ETLForgeError,
            match="Could not generate .* unique values .* using faker template",
        ):
            generator.generate_data(5000)

    def test_faker_without_faker_installed(self):
        """Test Faker template when faker is not available."""
        schema = {
            "fields": [
                {
                    "name": "name",
                    "type": "string",
                    "faker_template": "name",
                }
            ]
        }
        generator = DataGenerator(schema)
        # Temporarily disable faker
        original_faker = generator.faker
        generator.faker = None

        df = generator.generate_data(10)

        # Should fall back to random strings
        assert len(df) == 10
        assert all(isinstance(val, str) for val in df["name"])

        # Restore faker
        generator.faker = original_faker

    def test_unique_faker_with_nulls(self):
        """Test unique Faker values with nullable field."""
        schema = {
            "fields": [
                {
                    "name": "email",
                    "type": "string",
                    "unique": True,
                    "nullable": True,
                    "null_rate": 0.2,
                    "faker_template": "email",
                }
            ]
        }
        generator = DataGenerator(schema)
        df = generator.generate_data(50)

        # Should have some nulls
        assert df["email"].isna().sum() > 0
        # Non-null values should be unique
        non_null_emails = df["email"].dropna()
        assert non_null_emails.nunique() == len(non_null_emails)
