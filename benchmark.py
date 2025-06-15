"""
Performance benchmark script for ETLTest.

This script measures the time taken for two core operations:
1. Data Generation: Creating a DataFrame based on a schema.
2. Data Validation: Validating a DataFrame against a schema.

It tests these operations on several datasets of increasing size to demonstrate
the scalability of the framework.
"""
import time
import platform
import psutil
import pandas as pd
from etltest.generator import DataGenerator
from etltest.validator import DataValidator

# --- Configuration ---
SCHEMA_PATH = 'benchmark_schema.yaml'
ROW_COUNTS = [10_000, 100_000, 1_000_000]

def get_system_info():
    """Gathers system information for benchmark context."""
    return {
        "Platform": platform.platform(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "RAM": f"{psutil.virtual_memory().total / (1024**3):.2f} GB"
    }

def run_benchmark():
    """Runs the full benchmark suite and prints the results."""
    print("--- ETLTest Performance Benchmark ---")
    
    # Print System Info
    print("\n[System Information]")
    sys_info = get_system_info()
    for key, value in sys_info.items():
        print(f"{key}: {value}")

    # Initialize tools
    try:
        generator = DataGenerator(SCHEMA_PATH)
        validator = DataValidator(SCHEMA_PATH)
    except Exception as e:
        print(f"\nError initializing tools: {e}")
        return

    results = []

    print("\n[Running Benchmarks...]")
    for rows in ROW_COUNTS:
        print(f"\nTesting with {rows:,} rows...")
        
        # 1. Benchmark Data Generation
        start_time_gen = time.perf_counter()
        try:
            df = generator.generate_data(rows)
            end_time_gen = time.perf_counter()
            gen_duration = end_time_gen - start_time_gen
            print(f"  - Generation took: {gen_duration:.4f} seconds")
        except Exception as e:
            print(f"  - Generation failed: {e}")
            gen_duration = -1.0
            df = None

        # 2. Benchmark Data Validation
        val_duration = -1.0
        if df is not None:
            start_time_val = time.perf_counter()
            try:
                validator.validate(df)
                end_time_val = time.perf_counter()
                val_duration = end_time_val - start_time_val
                print(f"  - Validation took: {val_duration:.4f} seconds")
            except Exception as e:
                print(f"  - Validation failed: {e}")
                val_duration = -1.0

        results.append({
            "Rows": f"{rows:,}",
            "Generation Time (s)": f"{gen_duration:.4f}",
            "Validation Time (s)": f"{val_duration:.4f}",
        })

    # Print results in a markdown-friendly table
    print("\n--- Benchmark Results ---")
    header = "| Rows       | Generation Time (s) | Validation Time (s) |"
    separator = "|------------|---------------------|---------------------|"
    print(header)
    print(separator)
    for res in results:
        print(f"| {res['Rows']:<10} | {res['Generation Time (s)']:<19} | {res['Validation Time (s)']:<19} |")

if __name__ == "__main__":
    run_benchmark() 