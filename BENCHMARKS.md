# Performance Benchmarks

This document provides performance benchmarks for the `ETLTest` framework. The benchmarks were run using the `benchmark.py` script, which measures the time for data generation and validation across a range of dataset sizes.

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

The results show that both generation and validation times scale linearly with the number of rows.

| Rows        | Generation Time (s) | Validation Time (s) |
|-------------|-----------------------|-----------------------|
| 10,000      | 1.1838                | 0.0594                |
| 100,000     | 12.6293               | 0.4794                |
| 1,000,000   | 189.0517              | 4.7033                |

---

To reproduce these benchmarks, run the following command from the root of the repository:

```bash
pip install -r requirements.txt
python benchmark.py
``` 