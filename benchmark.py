"""
Performance benchmark script for ETLForge.

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
from etl_forge.generator import DataGenerator
from etl_forge.validator import DataValidator

# --- Configuration ---
SCHEMA_PATH = 'benchmark_schema.yaml'
ROW_COUNTS = [
    1_000,      # 1K - baseline small dataset
    5_000,      # 5K - small intermediate  
    10_000,     # 10K - original starting point
    25_000,     # 25K - better granularity in 10K-100K range
    50_000,     # 50K - mid-range
    100_000,    # 100K - original mid point
    250_000,    # 250K - better coverage before 1M
    500_000,    # 500K - pre-million scale
    1_000_000,  # 1M - original endpoint
    2_500_000,  # 2.5M - test beyond million scale
    5_000_000,  # 5M - large-scale performance test
]
RESULTS_PATH = 'benchmark_results.csv'

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
    print("--- ETLForge Performance Benchmark ---")
    
    # Print System Info
    print("\n[System Information]")
    sys_info = get_system_info()
    for key, value in sys_info.items():
        print(f"{key}: {value}")

    # Initialize tools
    try:
        generator = DataGenerator(SCHEMA_PATH)
        validator = DataValidator(SCHEMA_PATH)
    except FileNotFoundError:
        print(f"\nError: Schema file '{SCHEMA_PATH}' not found.")
        print("Please ensure the benchmark schema file exists in the current directory.")
        return
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
            "Rows": rows,
            "Generation Time (s)": gen_duration,
            "Validation Time (s)": val_duration,
        })

    # Create and save results DataFrame
    results_df = pd.DataFrame(results)
    try:
        results_df.to_csv(RESULTS_PATH, index=False)
        print(f"\nBenchmark results saved to '{RESULTS_PATH}'")
    except IOError as e:
        print(f"\nError saving results to '{RESULTS_PATH}': {e}")
        
    # Print results in a markdown-friendly table
    print("\n--- Benchmark Results ---")
    # Format for printing
    display_df = results_df.copy()
    display_df["Rows"] = display_df["Rows"].apply(lambda x: f"{x:,}")
    display_df["Generation Time (s)"] = display_df["Generation Time (s)"].apply(lambda x: f"{x:.4f}")
    display_df["Validation Time (s)"] = display_df["Validation Time (s)"].apply(lambda x: f"{x:.4f}")

    header = "| Rows       | Generation Time (s) | Validation Time (s) |"
    separator = "|------------|---------------------|---------------------|"
    print(header)
    print(separator)
    for _, res in display_df.iterrows():
        print(f"| {res['Rows']:<10} | {res['Generation Time (s)']:<19} | {res['Validation Time (s)']:<19} |")

if __name__ == "__main__":
    run_benchmark() 