# Product Metrics Copilot

A production-ready CLI tool that automatically analyzes product metrics data, detects what changed, and provides actionable insights for Product Managers.

## What It Does

Product Metrics Copilot answers the key questions every PM asks:
- **"What happened in the data?"** - Automated trend analysis, change point detection, and experiment results
- **"Why might it have happened?"** - Segment decomposition and hypothesis generation
- **"What should I check next?"** - Recommended follow-up investigations with SQL-like queries
- **"What decision should I make?"** - Evidence-based decision recommendations with confidence levels

## Features

### Core Capabilities
- ✅ **Smart CSV Ingestion** - Auto-detects delimiters, encoding, date formats, and cleans messy data
- ✅ **Data Quality Checks** - Identifies missing values, impossible values, and schema issues
- ✅ **KPI Detection** - Automatically identifies metrics (rates, counts, revenue, duration)
- ✅ **Trend Analysis** - Detects direction, change points, and largest deltas
- ✅ **A/B Test Analysis** - Calculates uplift, confidence intervals, and statistical significance
- ✅ **Segment Decomposition** - Identifies which segments drive changes in KPIs
- ✅ **Insight Generation** - Creates hypotheses with confidence levels and supporting evidence
- ✅ **Decision Recommendations** - Suggests actions based on the data

### Output Formats
1. **Human-friendly PM summary** (console)
   - Executive summary
   - What happened narrative
   - Key drivers and anomalies
   - Recommendations

2. **Machine-readable JSON report** (for further processing)
3. **Markdown report** (for documentation)

## Installation

```bash
# Clone or download the project
cd metrics_copilot

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

## Quick Start

### 1. Generate Sample Data

```bash
python -m metrics_copilot.generate_samples
```

This creates three sample CSV files in the `examples/` directory:
- `sample_timeseries.csv` - 90 days of product metrics with a change point
- `sample_experiment.csv` - A/B test data with significant results
- `sample_messy.csv` - Messy data to test data cleaning

### 2. Run Analysis

```bash
# Basic analysis (console output only)
python -m metrics_copilot.cli examples/sample_timeseries.csv

# With JSON output
python -m metrics_copilot.cli examples/sample_timeseries.csv --out report.json

# With both JSON and Markdown output
python -m metrics_copilot.cli examples/sample_experiment.csv --out report.json --markdown report.md
```

## Example Output

```
================================================================================
PRODUCT METRICS COPILOT
================================================================================

Analyzing: examples/sample_timeseries.csv

📊 Step 1/7: Ingesting and cleaning data...
  ✓ Loaded 8,100 rows, 9 columns
  ✓ Date column: date

🔍 Step 2/7: Profiling data...
  ✓ Data mode: timeseries
  ✓ Quality issues: 0

📈 Step 3/7: Detecting KPIs...
  ✓ Detected 6 KPI columns
  ✓ Primary KPIs: revenue, conversion_rate

📉 Step 4/7: Analyzing trends...
  ✓ Analyzed trends for 6 KPIs
  ✓ Detected 3 change points

================================================================================
EXECUTIVE SUMMARY
================================================================================
• Analyzed 8,100 rows across 9 columns (timeseries mode)
• Time range: 2024-01-01 to 2024-03-30
• Primary KPIs: revenue, conversion_rate
• Largest change: dau increased 20.5% on 2024-02-15

================================================================================
WHAT HAPPENED
================================================================================

📊 Overall Trends:
  📈 dau increased +20.12% overall (recent: +19.87%)
  📈 conversion_rate increased +15.34% overall (recent: +14.92%)
  📈 revenue increased +19.98% overall (recent: +20.11%)

🔔 Major Change Points:
  ↑ 2024-02-15: dau changed +20.5% (confidence: high)
  ↑ 2024-02-15: conversion_rate changed +15.8% (confidence: high)
  ↑ 2024-02-15: revenue changed +19.9% (confidence: high)

================================================================================
RECOMMENDED DECISIONS
================================================================================

1. Investigate improvement on 2024-02-15
   Confidence: 🟢 HIGH
   Rationale: Multiple KPIs improved significantly on this date
   ...
```

## CSV Input Format

The tool accepts any CSV file with product metrics. It works best with:

### Time Series Data
- A date/datetime column (any common format)
- Metric columns (DAU, revenue, conversion_rate, etc.)
- Optional segment columns (platform, country, user_type, etc.)

### Experiment Data
- A variant/group column (control vs test)
- Metric columns to compare
- Optional segment columns

### Messy Data is OK!
The tool handles:
- Multiple date formats
- Numbers with commas: `1,000`
- Percentages: `5.5%`
- Currency: `$100.50`
- Missing values
- Inconsistent column names

## Project Structure

```
metrics_copilot/
├── __init__.py
├── schemas.py              # Data classes and type definitions
├── ingest.py              # CSV ingestion and cleaning
├── profiling.py           # Data profiling and KPI detection
├── analysis_trends.py     # Time series trend analysis
├── analysis_experiments.py # A/B test analysis
├── decomposition.py       # Segment decomposition
├── insights.py            # Hypothesis and decision generation
├── cli.py                 # Command-line interface
├── generate_samples.py    # Sample data generator
└── tests/                 # Unit tests
    ├── test_ingest.py
    ├── test_profiling.py
    └── test_experiments.py
```

## Running Tests

```bash
pytest metrics_copilot/tests/
```

## How It Works

### 1. Data Ingestion (`ingest.py`)
- Auto-detects file encoding and delimiter
- Standardizes column names to snake_case
- Parses dates from various formats
- Cleans numeric columns (removes commas, %, $)
- Validates data quality

### 2. Profiling (`profiling.py`)
- Profiles each column (type, missingness, cardinality)
- Detects KPI columns by name and value patterns
- Identifies data mode (timeseries, experiment, both, static)
- Finds segment columns for decomposition

### 3. Trend Analysis (`analysis_trends.py`)
- Calculates overall and recent percent changes
- Detects change points using rolling window statistics
- Finds largest spikes and drops
- Determines trend direction (increasing, decreasing, stable, volatile)

### 4. Experiment Analysis (`analysis_experiments.py`)
- Identifies control vs test groups
- Calculates uplift with bootstrap confidence intervals
- Performs statistical significance testing
- Generates warnings for sample size, variance, and duration issues

### 5. Segment Decomposition (`decomposition.py`)
- Calculates each segment's contribution to overall changes
- Identifies top positive and negative drivers
- Finds anomalous segments using z-score analysis

### 6. Insight Generation (`insights.py`)
- Generates hypotheses with confidence levels (high/medium/low)
- Provides supporting evidence from the data
- Suggests follow-up investigations
- Recommends decisions with rationale and risks

## Design Principles

1. **Transparency** - Always show reasoning and supporting evidence
2. **Grounded in Data** - Never claim causation without data patterns
3. **Confidence Levels** - Mark speculation as "low confidence"
4. **No External APIs** - Everything runs offline
5. **Production-Ready** - Type hints, error handling, comprehensive testing

## Limitations & Future Work

Current limitations:
- Simple change point detection (no advanced algorithms like PELT)
- Limited to univariate analysis (doesn't model multivariate relationships)
- No time series forecasting
- No automated causal inference

Future enhancements:
- Web UI (Streamlit or FastAPI)
- Advanced change point detection (ruptures library)
- Anomaly detection algorithms
- Export to visualization tools
- Integration with data warehouses

## License

MIT License - feel free to use and modify for your needs.

## Contributing

This is a demonstration project. For production use, consider:
- Adding more robust error handling
- Implementing proper logging
- Adding visualization capabilities
- Integrating with your data infrastructure
- Customizing KPI detection for your domain

## Questions?

The tool is designed to be self-explanatory. If you're unsure about any output:
1. Check the confidence level
2. Review the supporting evidence
3. Follow the recommended next checks
4. Consult the JSON output for full details
