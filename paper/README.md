# Paper Submission Files

This folder contains the JOSS paper submission files:

- `paper.md` - Main paper file with all content
- `paper.bib` - Bibliography with all references
- `benchmark_plot.png` - Performance benchmark plot

## Generating the Plot

To regenerate the benchmark plot, run from the root directory:

```bash
python benchmark.py
python plot_benchmark.py
```

The plot will be saved as `benchmark_plot.png` in the root directory and should be copied here for the paper submission.

## Building the Paper

The paper is designed to be processed by JOSS's publication system. The bibliography references are properly formatted for academic citation. 