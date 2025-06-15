"""
Generates and saves a performance benchmark plot for ETLTest.

This script runs the benchmark, captures the results, and uses matplotlib
to create a plot visualizing the scalability of data generation and validation.
The plot is saved as `benchmark_plot.png`.
"""
import time
import platform
import pandas as pd
import matplotlib.pyplot as plt
from etltest.generator import DataGenerator
from etltest.validator import DataValidator

# --- Configuration ---
SCHEMA_PATH = 'benchmark_schema.yaml'
ROW_COUNTS = [10_000, 100_000, 500_000, 1_000_000]
OUTPUT_FILENAME = 'benchmark_plot.png'

def run_full_benchmark():
    """Runs the benchmark and returns results as a DataFrame."""
    print("--- Running Benchmark for Plotting ---")
    
    generator = DataGenerator(SCHEMA_PATH)
    validator = DataValidator(SCHEMA_PATH)
    
    results = []

    for rows in ROW_COUNTS:
        print(f"Testing with {rows:,} rows...")
        
        # Generation
        start_time_gen = time.perf_counter()
        df = generator.generate_data(rows)
        gen_duration = time.perf_counter() - start_time_gen
        
        # Validation
        start_time_val = time.perf_counter()
        validator.validate(df)
        val_duration = time.perf_counter() - start_time_val
        
        results.append({
            "Rows": rows,
            "Generation Time (s)": gen_duration,
            "Validation Time (s)": val_duration,
        })
        
    return pd.DataFrame(results)

def create_plot(df: pd.DataFrame):
    """Creates and saves a plot from the benchmark results."""
    print(f"\n--- Generating Plot: {OUTPUT_FILENAME} ---")
    
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Generation Time on the primary y-axis
    color1 = 'tab:blue'
    ax1.set_xlabel('Number of Rows')
    ax1.set_ylabel('Generation Time (s)', color=color1)
    ax1.plot(df['Rows'], df['Generation Time (s)'], 'o-', color=color1, label='Generation')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Create a secondary y-axis for Validation Time
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Validation Time (s)', color=color2)
    ax2.plot(df['Rows'], df['Validation Time (s)'], 's--', color=color2, label='Validation')
    ax2.tick_params(axis='y', labelcolor=color2)

    # Formatting
    plt.title('ETLTest Performance: Generation and Validation', fontsize=16)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax2.set_yscale('log')
    ax1.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    fig.tight_layout()
    plt.savefig(OUTPUT_FILENAME, dpi=300)
    print("Plot saved successfully.")

if __name__ == "__main__":
    benchmark_results = run_full_benchmark()
    print("\n--- Benchmark Results ---")
    print(benchmark_results)
    create_plot(benchmark_results) 