"""
Generates and saves a performance benchmark plot for ETLForge.

This script runs the benchmark, captures the results, and uses matplotlib
to create a plot visualizing the scalability of data generation and validation.
The plot is saved as `benchmark_plot.png`.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configuration ---
RESULTS_PATH = 'benchmark_results.csv'
PLOT_PATH = 'benchmark_plot.png'

def create_plot(df: pd.DataFrame):
    """Generates and saves a plot from the benchmark data."""
    if df.empty:
        print("Benchmark data is empty. Skipping plot generation.")
        return

    # Set plot style
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # Melt the DataFrame to have a 'variable' column for hue
    df_melted = df.melt(id_vars=['Rows'], 
                        value_vars=['Generation Time (s)', 'Validation Time (s)'],
                        var_name='Operation', 
                        value_name='Time (s)')

    # Create the plot
    ax = sns.lineplot(data=df_melted, x='Rows', y='Time (s)', hue='Operation', marker='o')

    # Customize plot
    ax.set_title('ETLForge Performance Benchmark', fontsize=16)
    ax.set_xlabel('Number of Rows', fontsize=12)
    ax.set_ylabel('Time (seconds)', fontsize=12)
    ax.ticklabel_format(style='plain', axis='x') # No scientific notation on x-axis
    
    # Format x-axis labels with commas
    ax.get_xaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot
    try:
        plt.savefig(PLOT_PATH)
        print(f"Plot saved to '{PLOT_PATH}'")
    except IOError as e:
        print(f"Error saving plot: {e}")

def main():
    """Main function to read results and generate the plot."""
    try:
        benchmark_df = pd.read_csv(RESULTS_PATH)
        print(f"Loaded benchmark results from '{RESULTS_PATH}'")
        create_plot(benchmark_df)
    except FileNotFoundError:
        print(f"Error: Benchmark results file not found at '{RESULTS_PATH}'")
        print("Please run 'python benchmark.py' first to generate the results.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main() 