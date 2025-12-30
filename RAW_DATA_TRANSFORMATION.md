# Raw Data Auto-Transformation

The Product Metrics Copilot now automatically transforms raw data into analysis-ready format! 🎉

## What This Means

You can now upload **any CSV format** and the system will automatically:
- Parse and clean numeric values (removes $, %, commas)
- Detect and convert date columns
- Transform event-level data into aggregated timeseries
- Handle wide-format data
- Standardize column names

## Supported Data Formats

### 1. **Timeseries Format** (Already optimal)
```csv
Date,Platform,DAU,Revenue
2024-01-01,iOS,1000,5000
2024-01-02,iOS,1200,6000
```
✅ No transformation needed

### 2. **Event-Level Data** (Auto-aggregated)
```csv
timestamp,user_id,event_name,revenue,platform
2024-01-01 10:30:00,user123,purchase,49.99,iOS
2024-01-01 11:45:00,user456,purchase,29.99,Android
```
✨ Automatically aggregated to daily metrics:
- Counts events per day
- Calculates DAU (unique users)
- Sums revenue
- Groups by dimensions (platform, etc.)

### 3. **Raw Data with Formatting** (Auto-cleaned)
```csv
Date,Daily Active Users,Revenue ($),Conversion %
2024-01-01,"69,882","$7,313.43",0.00%
```
✨ Automatically parsed:
- Removes commas: "69,882" → 69882
- Removes currency: "$7,313.43" → 7313.43
- Converts percentages: "0.00%" → 0.00

### 4. **Wide Format** (Detected, kept as-is or melted)
```csv
Date,iOS_DAU,Android_DAU,Web_DAU
2024-01-01,1000,800,500
```
✅ Detected and handled appropriately

## How It Works

### API Endpoints

#### 1. Preview Transformation
```bash
curl -X POST "https://web-production-55d55.up.railway.app/preview" \
  -F "file=@your_data.csv"
```

**Response:**
```json
{
  "detected_format": "event_level",
  "planned_transformation": "Will aggregate events to daily metrics",
  "original_shape": [10000, 5],
  "date_column": "timestamp",
  "numeric_columns": ["revenue", "duration"],
  "sample_data": [...]
}
```

#### 2. Analyze with Auto-Transform (Default)
```bash
curl -X POST "https://web-production-55d55.up.railway.app/analyze/quick" \
  -F "file=@your_data.csv"
```

The transformation happens automatically! Results include transformation metadata:

```json
{
  "executive_summary": {...},
  "metadata": {
    "transformation_metadata": {
      "detected_format": "event_level",
      "transformation_type": "event_aggregation",
      "original_rows": 10000,
      "final_rows": 30,
      "transformations": [
        "Extracted date from timestamp",
        "Calculated DAU from user_id",
        "Aggregated revenue"
      ]
    }
  }
}
```

#### 3. Skip Auto-Transform (if needed)
```bash
curl -X POST "https://web-production-55d55.up.railway.app/analyze/quick?auto_transform=false" \
  -F "file=@your_data.csv"
```

## UI Experience

When you upload raw data in the web interface:

1. **Upload any CSV** - The system detects the format
2. **Automatic transformation** - Data is cleaned and formatted
3. **Visual feedback** - A purple alert shows what was transformed:

   ```
   ✨ Data Automatically Transformed
   Detected format: event_level
   10,000 events → 30 aggregated rows
   • Extracted date from timestamp
   • Calculated DAU from user_id
   • Aggregated revenue
   ```

4. **Analyze as normal** - All insights work on the transformed data

## Transformation Logic

### Event Detection
The system detects event-level data by looking for:
- High-cardinality timestamp columns
- User/customer ID columns
- Event name/type columns

### Aggregation Rules
When aggregating events:
- **Date:** Extracts date from timestamp
- **User metrics:** Counts unique users (DAU)
- **Event counts:** Counts total events/sessions
- **Revenue:** Sums revenue columns
- **Conversions:** Sums boolean/success columns
- **Rates:** Calculates conversion rates
- **ARPDAU:** Revenue per DAU

### Dimension Handling
Automatically detects categorical columns with reasonable cardinality:
- Platform
- Country
- Device type
- User segment
- etc.

Groups metrics by: `[date, dimension1, dimension2, ...]`

## Examples

### Example 1: Mixpanel Raw Export

**Input:**
```csv
DATE,Daily Active Users,Conversion %,Revenue ($),Platform
2025-11-29,"69,882",0.00%,"$7,313.43",Android
2025-11-29,"11,422",0.00%,"$1,195.36",iOS
```

**Automatic transformations:**
1. Standardizes columns: `date`, `daily_active_users`, `conversion`, `revenue`, `platform`
2. Parses numbers: `"69,882"` → `69882`
3. Parses currency: `"$7,313.43"` → `7313.43`
4. Converts percentage: `"0.00%"` → `0.00`
5. Ready for analysis!

### Example 2: Raw Event Stream

**Input:**
```csv
timestamp,user_id,purchased,amount,country
2024-01-01 08:00:00,u123,true,49.99,US
2024-01-01 09:30:00,u456,false,0,UK
2024-01-01 10:15:00,u123,true,29.99,US
```

**Automatic transformations:**
1. Extracts date: `2024-01-01`
2. Calculates DAU per country
3. Counts events/sessions
4. Sums purchases: `purchased=true` → count
5. Sums revenue: `amount`
6. Calculates conversion rate: `purchases / events`

**Output:**
```csv
date,country,events,dau,purchased_count,revenue,purchased_rate
2024-01-01,US,2,1,2,79.98,1.0
2024-01-01,UK,1,1,0,0,0.0
```

## Testing Locally

```bash
# Test transformation preview
python test_transformation.py

# Or manually
uv run python -c "
from metrics_copilot.data_transformer import preview_transformation
preview = preview_transformation('your_data.csv')
print(preview)
"
```

## Benefits

✅ **No manual formatting needed** - Upload raw exports directly
✅ **Intelligent parsing** - Handles currency, percentages, commas
✅ **Event aggregation** - Converts logs to metrics automatically
✅ **Transparent** - Shows exactly what was transformed
✅ **Fallback safe** - If transformation fails, tries original data
✅ **Always enabled** - Just works out of the box

## Next Steps

After deploying to Railway, this feature will work automatically for all uploads through both:
- The web UI (metrics-copilot-ui)
- Direct API calls

No configuration needed - just upload your data and go! 🚀
