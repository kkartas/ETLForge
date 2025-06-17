# Performance Benchmarks

This document provides performance benchmarks for the `ETLForge` framework. The benchmarks were run using the `benchmark.py` script, which measures the time for data generation and validation across a range of dataset sizes.

## Methodology

- **Tool**: `benchmark.py` script.
- **Schema**: `benchmark_schema.yaml` (a schema designed to test raw performance without restrictive `unique` constraints).
- **Operations**:
  1.  **Generation**: Time to create a pandas DataFrame in memory.
  2.  **Validation**: Time to validate the in-memory DataFrame against the schema.

## System Environment

The following benchmarks were run on the system detailed below:

- **Platform**: Windows-10-10.0.26100-SP0
- **Processor**: Intel64 Family 6 Model 186 Stepping 3, GenuineIntel
- **Python Version**: 3.11.9
- **RAM**: 31.35 GB

## Results

The comprehensive benchmark covers 11 data points ranging from 1,000 to 5,000,000 rows, spanning 4 orders of magnitude. The results demonstrate that both generation and validation times scale near-linearly with the number of rows across this entire range, confirming the framework's scalability for production ETL workloads.

![ETLForge Performance Plot](paper/benchmark_plot.png)

| Rows        | Generation Time (s) | Validation Time (s) |
|-------------|-----------------------|-----------------------|
| 1,000       | 0.1230                | 0.0091                |
| 5,000       | 0.6030                | 0.0269                |
| 10,000      | 1.2588                | 0.0487                |
| 25,000      | 3.2063                | 0.1336                |
| 50,000      | 6.1208                | 0.2754                |
| 100,000     | 12.5585               | 0.5115                |
| 250,000     | 32.1666               | 1.2316                |
| 500,000     | 65.7119               | 2.4138                |
| 1,000,000   | 130.1015              | 5.1648                |
| 2,500,000   | 390.2832              | 28.9765               |
| 5,000,000   | 1457.9524             | 74.4328               |

---

To reproduce these benchmarks, run the following command from the root of the repository:

```bash
pip install -e ".[dev]"
python benchmark.py
```

To reproduce the plot from the generated `benchmark_results.csv`:

```bash
python plot_benchmark.py
```