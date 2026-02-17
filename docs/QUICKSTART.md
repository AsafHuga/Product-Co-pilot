# Product Metrics Copilot - Quick Start Guide

## Installation (30 seconds)

```bash
# Install dependencies
pip install -r requirements.txt

# Or using uv
uv pip install pandas numpy scipy chardet
```

## Generate Sample Data (5 seconds)

```bash
python -m metrics_copilot.generate_samples
```

This creates:
- `examples/sample_timeseries.csv` - Time series with change points
- `examples/sample_experiment.csv` - A/B test data
- `examples/sample_messy.csv` - Messy data for testing

## Run Your First Analysis (10 seconds)

```bash
# Basic analysis
python -m metrics_copilot.cli examples/sample_timeseries.csv

# With JSON output
python -m metrics_copilot.cli examples/sample_experiment.csv --out report.json

# With markdown report
python -m metrics_copilot.cli examples/sample_experiment.csv --out report.json --markdown report.md
```

## What You'll Get

### Console Output
- 📊 Executive summary (3-6 key bullets)
- 📈 What happened (trends, change points, experiments)
- 🎯 Key drivers (which segments matter most)
- 💡 Hypotheses (what might have caused changes)
- 🔍 Recommended next steps (with SQL-like queries)
- ✅ Decision recommendations (ship/don't ship/investigate)

### JSON Report (`report.json`)
Complete structured data including:
- Data profile and quality checks
- Detected KPIs
- Trends and change points
- Experiment results with statistics
- Segment drivers
- Hypotheses with confidence levels
- Recommended decisions

### Markdown Report (`report.md`)
Human-readable documentation with:
- Executive summary
- Key findings
- Hypotheses
- Recommendations

## Use Your Own Data

Your CSV can have any structure. The tool handles:

### Time Series Data
```csv
date,platform,country,dau,sessions,conversion_rate,revenue
2024-01-01,iOS,US,10000,25000,0.05,50000
2024-01-02,iOS,US,10500,26000,0.052,52000
...
```

### Experiment Data
```csv
user_id,variant,converted,revenue,platform
user_1,control,1,50.00,iOS
user_2,test,0,0,Android
...
```

### Messy Data (we'll clean it!)
```csv
DATE,Daily Active Users,Conversion %,Revenue ($)
01/01/2024,"10,000",5.5%,$50,000.00
2024-01-02,10500,5.2%,52000
...
```

## Understanding the Output

### Confidence Levels
- 🟢 **HIGH** - Strongly supported by data patterns
- 🟡 **MEDIUM** - Plausible but indirect evidence
- 🔴 **LOW** - Speculation, needs more investigation

### Change Point Confidence
- **HIGH** - Large change (>30%) with low variance
- **MEDIUM** - Moderate change (>20%) or medium variance
- **LOW** - Smaller changes or high variance

### Experiment Results
- **Significant** - p < 0.05 and CI doesn't cross zero
- **Not significant** - Insufficient evidence for effect
- **Warnings** - Sample size, variance, duration issues

## Common Workflows

### 1. Weekly Metrics Review
```bash
python -m metrics_copilot.cli weekly_metrics.csv --markdown weekly_review.md
# Share weekly_review.md with team
```

### 2. A/B Test Analysis
```bash
python -m metrics_copilot.cli experiment_results.csv --out experiment.json
# Review decision recommendation in console output
# Share JSON with data team for deep dive
```

### 3. Investigating a Metric Drop
```bash
python -m metrics_copilot.cli metrics.csv
# Check "Change Points" section for when it happened
# Review "Key Drivers" for which segments are affected
# Follow "Recommended Next Steps" for investigation queries
```

## Tips

1. **Column Names**: Any format works - we'll standardize them
2. **Date Formats**: We detect automatically (2024-01-01, 01/01/2024, etc.)
3. **Missing Values**: We handle them transparently and report issues
4. **Segments**: Low-cardinality columns (2-50 values) auto-detected as segments
5. **Experiments**: Columns with "variant", "group", "control", "test" auto-detected

## Troubleshooting

### "No date column detected"
- Make sure you have a column with dates or timestamps
- Column name should include: date, time, day, dt, timestamp, ts

### "No KPIs detected"
- Check that you have numeric columns
- Common KPI names: dau, revenue, conversion_rate, sessions, etc.

### "No experiment detected"
- Need a column with variant/group/control/test values
- Should be low cardinality (2-10 unique values)

## Next Steps

1. Try the sample data: `python -m metrics_copilot.generate_samples`
2. Run basic analysis: `python -m metrics_copilot.cli examples/sample_timeseries.csv`
3. Review the output sections
4. Try your own data!

## Need Help?

- Check the README.md for detailed documentation
- Review DEMO_RESULTS.md for example outputs
- Look at the sample CSV files in `examples/`

Happy analyzing! 📊
