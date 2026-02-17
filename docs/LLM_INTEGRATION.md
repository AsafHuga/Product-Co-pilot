# 🤖 LLM Integration Guide

Your Product Metrics Copilot now supports **OpenAI LLM-enhanced insights** for more natural, intelligent analysis!

## What's New?

The LLM integration enhances your analysis with:

✨ **Natural Language Hypotheses** - GPT-4 generates contextual, data-driven hypotheses
✨ **Executive Summaries** - Clear, PM-friendly summaries written by AI
✨ **Smarter Recommendations** - More nuanced, context-aware decision suggestions
✨ **Fallback to Rule-Based** - If LLM is unavailable, uses the original statistical insights

---

## Setup (5 minutes)

### Step 1: Get Your OpenAI API Key

1. Go to **https://platform.openai.com/api-keys**
2. Sign up or log in
3. Click **"Create new secret key"**
4. Copy the key (starts with `sk-...`)

### Step 2: Set Your API Key

Create a `.env` file in your project directory:

```bash
cd /Users/asafhuga
cp .env.example .env
```

Edit `.env` and add your key:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 3: Install Dependencies

```bash
uv pip install openai python-dotenv
```

Or if using regular pip:

```bash
pip install -r requirements.txt
```

**Done!** ✅

---

## Usage

### CLI Usage

**With LLM (default):**
```bash
python -m metrics_copilot.cli examples/sample_timeseries.csv
```

**Explicitly enable LLM:**
```bash
python -m metrics_copilot.cli examples/sample_timeseries.csv --use-llm
```

**Disable LLM (rule-based only):**
```bash
python -m metrics_copilot.cli examples/sample_timeseries.csv --no-llm
```

### API Usage

**With LLM (default):**
```bash
curl -X POST "http://localhost:8000/analyze/quick" \
  -F "file=@examples/sample_timeseries.csv"
```

**Disable LLM:**
```bash
curl -X POST "http://localhost:8000/analyze/quick?use_llm=false" \
  -F "file=@examples/sample_timeseries.csv"
```

### Python Usage

```python
from metrics_copilot.cli import analyze_csv

# With LLM
report = analyze_csv("data.csv", use_llm=True)

# Without LLM
report = analyze_csv("data.csv", use_llm=False)
```

---

## How It Works

### Rule-Based Insights (Original)

```python
# Pattern matching and statistical thresholds
if change_point.magnitude > 0.2 and change_point.confidence == "high":
    hypothesis = f"Significant jump in {metric} on {date}"
```

### LLM-Enhanced Insights (New)

```python
# GPT-4 analyzes all findings together
llm_generator.enhance_hypotheses(report)
# Returns: "The 22% spike in conversions on Dec 20 coincides with
#           the Platform='Undefined' segment becoming dominant,
#           suggesting a potential tracking configuration change..."
```

The LLM sees:
- All KPIs and their trends
- Change points and their timing
- Segment contributions
- Experiment results
- Data quality issues

And generates **contextual hypotheses** that connect the dots!

---

## Cost Estimate

**For typical Product Metrics analysis:**

- **GPT-4 Turbo**: ~$0.05 - $0.15 per analysis
- **GPT-3.5 Turbo**: ~$0.01 - $0.03 per analysis

**Example monthly cost:**
- 100 analyses/month with GPT-4 Turbo: ~$5-15/month
- 100 analyses/month with GPT-3.5 Turbo: ~$1-3/month

**Recommendation:** Start with GPT-4 Turbo for best quality. Switch to GPT-3.5 if cost is a concern.

---

## Choosing the Model

Edit your `.env` file:

```env
# Best quality (default)
OPENAI_MODEL=gpt-4-turbo-preview

# Faster, cheaper
OPENAI_MODEL=gpt-3.5-turbo

# Most capable (expensive)
OPENAI_MODEL=gpt-4
```

Or set in code:

```python
from metrics_copilot.llm_insights import LLMInsightGenerator

generator = LLMInsightGenerator(model="gpt-3.5-turbo")
```

---

## Deployment with Railway

### Option 1: Environment Variables in Railway Dashboard

1. Go to your Railway project
2. Click **Settings** → **Variables**
3. Add: `OPENAI_API_KEY` = `sk-your-key-here`
4. Redeploy (automatic)

### Option 2: Using Railway CLI

```bash
railway variables set OPENAI_API_KEY=sk-your-key-here
railway deploy
```

---

## Troubleshooting

### "OpenAI API key not found"

**Solution:** Make sure `.env` file exists with:
```env
OPENAI_API_KEY=sk-...
```

Or set environment variable:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

### "LLM hypothesis generation failed, falling back to rule-based"

This is **not an error** - it means LLM didn't work, but analysis continues with original insights.

**Common causes:**
- No API key set
- API key invalid
- Network issues
- OpenAI rate limit hit

### "Import Error: No module named 'openai'"

**Solution:**
```bash
pip install openai python-dotenv
```

### LLM not being used even though API key is set

**Check if it's enabled:**
```bash
python -c "from metrics_copilot.llm_insights import is_llm_available; print(is_llm_available())"
```

Should print `True`. If `False`, check:
1. `.env` file in correct location
2. `OPENAI_API_KEY` is set
3. `openai` package is installed

---

## Comparing Results

### Test with and without LLM:

```bash
# With LLM
python -m metrics_copilot.cli examples/sample_timeseries.csv \
  --use-llm -o report_llm.json

# Without LLM
python -m metrics_copilot.cli examples/sample_timeseries.csv \
  --no-llm -o report_baseline.json
```

Compare the `hypotheses` section in both JSON files!

---

## Privacy & Security

### What data is sent to OpenAI?

**Summary statistics ONLY** - not raw data:
- Row/column counts
- KPI names and trend directions (e.g., "DAU up 5%")
- Change point dates and magnitudes
- Segment contribution percentages

**NOT sent:**
- Raw CSV data
- Individual row values
- User IDs or personal information

### Example of what OpenAI sees:

```
DATA: 240 rows, 8 columns
KPIs: Daily Active Users, Conversion %, Revenue ($)
TRENDS: DAU ↘️ down -2.8%; Conversion % ↗️ up 15.2%
CHANGES: Conversion % jump of 22.8% on 2024-12-20
SEGMENTS: Platform=Undefined drives 74.2% of change
```

### Keeping data 100% private

Use `--no-llm` flag to analyze without sending any data to OpenAI:

```bash
python -m metrics_copilot.cli data.csv --no-llm
```

---

## Advanced Configuration

### Custom System Prompt

Edit [`metrics_copilot/llm_insights.py`](metrics_copilot/llm_insights.py):

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=[
        {
            "role": "system",
            "content": "You are a senior product analyst..."  # Customize this!
        },
        ...
    ]
)
```

### Adjusting Temperature (Creativity)

```python
# More creative/varied (0.7 default)
temperature=0.9

# More focused/deterministic
temperature=0.3
```

### Custom Max Tokens

```python
max_tokens=3000  # Longer responses (costs more)
max_tokens=500   # Shorter responses (cheaper)
```

---

## Example Output Comparison

### Rule-Based Hypothesis:
> "Significant increase in Conversion % on 2024-12-20 (+22.8%). Check for external factors or campaigns."

### LLM-Enhanced Hypothesis:
> "The dramatic 22.8% spike in conversions on December 20th coincides precisely with Platform='Undefined'
> becoming the dominant segment (74.2% of data). This suggests a tracking implementation change or data
> pipeline issue rather than genuine user behavior. Recommend immediate investigation of analytics
> instrumentation and platform detection logic, particularly any deployments around Dec 20."

**Notice the difference?** LLM connects multiple findings and provides more specific next steps!

---

## Questions?

- LLM not working? Check [Troubleshooting](#troubleshooting)
- Want to customize prompts? See [Advanced Configuration](#advanced-configuration)
- Privacy concerns? See [Privacy & Security](#privacy--security)

---

**Ready to try it?** Just set your `OPENAI_API_KEY` and run an analysis! 🚀
