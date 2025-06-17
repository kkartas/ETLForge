#!/usr/bin/env python3
"""
ETLForge Example - Complete workflow demonstration

This example shows how to use ETLForge for synthetic data generation
and validation in a typical ETL testing scenario.
"""

from etl_forge import DataGenerator, DataValidator


def main():
    """Demonstrate ETLForge's core functionality."""
    
    # 1. Define schema - single source of truth for both generation and validation
    schema = {
        "fields": [
            {
                "name": "customer_id",
                "type": "int",
                "unique": True,
                "range": {"min": 1, "max": 10000}
            },
            {
                "name": "name",
                "type": "string",
                "nullable": False,
                "faker_template": "name"  # Requires faker: pip install etl-forge[faker]
            },
            {
                "name": "email",
                "type": "string",
                "unique": True,
                "faker_template": "email"
            },
            {
                "name": "purchase_amount",
                "type": "float",
                "range": {"min": 10.0, "max": 5000.0},
                "nullable": True,
                "null_rate": 0.1  # 10% null values
            },
            {
                "name": "customer_tier",
                "type": "category",
                "values": ["Bronze", "Silver", "Gold", "Platinum"]
            },
            {
                "name": "registration_date",
                "type": "date",
                "range": {"start": "2020-01-01", "end": "2024-12-31"},
                "format": "%Y-%m-%d"
            }
        ]
    }
    
    # 2. Generate synthetic test data
    print("🔄 Generating synthetic test data...")
    generator = DataGenerator(schema)
    df = generator.generate_data(1000)
    
    # Save to CSV
    output_file = 'customer_test_data.csv'
    generator.save_data(df, output_file)
    print(f"✅ Generated {len(df)} rows of test data → {output_file}")
    
    # Display sample
    print("\n📊 Sample of generated data:")
    print(df.head())
    
    # 3. Validate the generated data (should pass)
    print("\n🔍 Validating generated data...")
    validator = DataValidator(schema)
    result = validator.validate(output_file)
    
    if result.is_valid:
        print("✅ Data validation passed!")
        print(f"   • Total rows: {result.summary['total_rows']}")
        print(f"   • Valid rows: {result.summary['valid_rows']}")
    else:
        print(f"❌ Validation failed with {len(result.errors)} errors")
    
    # 4. Demonstrate validation with corrupted data
    print("\n🧪 Testing validation with corrupted data...")
    
    # Create some invalid data
    df_corrupted = df.copy()
    df_corrupted.loc[0, 'customer_id'] = -1  # Invalid: below min range
    df_corrupted.loc[1, 'customer_tier'] = 'Invalid'  # Invalid: not in allowed values
    df_corrupted.loc[2, 'email'] = 'not-an-email'  # Invalid: bad format
    
    corrupted_file = 'corrupted_data.csv'
    df_corrupted.to_csv(corrupted_file, index=False)
    
    result_corrupted = validator.validate(corrupted_file)
    print(f"❌ Corrupted data validation: {len(result_corrupted.errors)} errors found")
    
    # Show first few errors
    for i, error in enumerate(result_corrupted.errors[:3]):
        print(f"   {i+1}. {error}")
    
    # 5. Generate validation report
    report_file = 'validation_errors.csv'
    validator.validate_and_report(corrupted_file, report_file)
    print(f"📄 Detailed error report saved to: {report_file}")
    
    print("\n🎉 Example completed! Key benefits demonstrated:")
    print("   • Single schema drives both generation and validation")
    print("   • Realistic data with Faker integration")
    print("   • Comprehensive validation with detailed reporting")
    print("   • Perfect synchronization between test data and validation rules")


if __name__ == "__main__":
    main() 