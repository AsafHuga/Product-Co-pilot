# Integrating Product Metrics Copilot with Lovable

This guide shows you how to connect the Product Metrics Copilot to your Lovable web application.

## Option 1: FastAPI Backend (Recommended)

### 1. Install API Dependencies

```bash
~/.local/bin/uv pip install fastapi uvicorn python-multipart
```

### 2. Start the API Server

```bash
~/.local/bin/uv run python metrics_copilot/api.py
```

The API will be available at `http://localhost:8000`

### 3. API Endpoints

**Health Check:**
```bash
GET http://localhost:8000/
```

**Full Analysis:**
```bash
POST http://localhost:8000/analyze
Content-Type: multipart/form-data
Body: file (CSV)

Returns: Complete analysis report (JSON)
```

**Quick Analysis (faster):**
```bash
POST http://localhost:8000/analyze/quick
Content-Type: multipart/form-data
Body: file (CSV)

Returns: Executive summary and key insights (JSON)
```

### 4. Lovable Frontend Code

In your Lovable app, use this code to upload and analyze CSV files:

```typescript
// Upload and analyze CSV file
async function analyzeMetrics(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/analyze/quick', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Analysis failed');
    }

    const results = await response.json();
    return results;
  } catch (error) {
    console.error('Error analyzing metrics:', error);
    throw error;
  }
}

// Example usage in a React component
function MetricsUploader() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    try {
      const analysisResults = await analyzeMetrics(file);
      setResults(analysisResults);
    } catch (error) {
      console.error('Failed to analyze:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" accept=".csv" onChange={handleFileUpload} />
      {loading && <p>Analyzing metrics...</p>}
      {results && (
        <div>
          <h2>Analysis Results</h2>
          <pre>{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

### 5. Response Format

**Quick Analysis Response:**
```json
{
  "executive_summary": {
    "row_count": 810,
    "column_count": 9,
    "data_mode": "timeseries",
    "time_range": {
      "start": "2024-01-01",
      "end": "2024-03-30"
    }
  },
  "kpis": [
    {
      "name": "revenue",
      "type": "money",
      "is_primary": true
    }
  ],
  "top_trends": [
    {
      "kpi": "conversion_rate",
      "direction": "increasing",
      "change_pct": 47.2
    }
  ],
  "top_change_points": [
    {
      "date": "2024-02-15",
      "kpi": "conversions",
      "delta_pct": 38.0,
      "confidence": "high"
    }
  ],
  "top_hypotheses": [
    {
      "description": "conversions increased by 38.0% on 2024-02-15",
      "confidence": "high"
    }
  ],
  "recommended_decisions": [
    {
      "decision": "Investigate improvement on 2024-02-15",
      "confidence": "high",
      "rationale": "Multiple KPIs improved significantly"
    }
  ]
}
```

---

## Option 2: Direct Python Integration

If your Lovable app has a Python backend, you can import directly:

```python
from metrics_copilot.cli import analyze_csv

# Analyze a CSV file
report = analyze_csv('data.csv', output_json='report.json')

# Access results
print(f"Found {len(report.kpis_detected)} KPIs")
print(f"Detected {len(report.change_points)} change points")

# Return as JSON
import json
return json.dumps(report.to_dict())
```

---

## Option 3: Deploy as Serverless Function

### Deploy to Vercel/Netlify

1. Create `api/analyze.py`:
```python
from fastapi import FastAPI, UploadFile
from metrics_copilot.api import app

# Export for serverless
handler = app
```

2. Add `vercel.json`:
```json
{
  "builds": [
    {
      "src": "api/analyze.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/analyze.py"
    }
  ]
}
```

3. Deploy:
```bash
vercel deploy
```

---

## Example Lovable UI Components

### File Upload Component

```tsx
import { useState } from 'react';
import { Upload, FileText, TrendingUp } from 'lucide-react';

export function MetricsAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const analyzeFile = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/analyze/quick', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Product Metrics Copilot</h1>

      {/* File Upload */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mt-4"
        />
        {file && (
          <div className="mt-4">
            <p className="text-sm text-gray-600">
              <FileText className="inline h-4 w-4" /> {file.name}
            </p>
            <button
              onClick={analyzeFile}
              disabled={loading}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {loading ? 'Analyzing...' : 'Analyze Metrics'}
            </button>
          </div>
        )}
      </div>

      {/* Results Display */}
      {results && (
        <div className="mt-8 space-y-6">
          {/* Executive Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Executive Summary</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Rows</p>
                <p className="text-2xl font-bold">
                  {results.executive_summary.row_count.toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Data Mode</p>
                <p className="text-2xl font-bold capitalize">
                  {results.executive_summary.data_mode}
                </p>
              </div>
            </div>
          </div>

          {/* Top Trends */}
          {results.top_trends && results.top_trends.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">
                <TrendingUp className="inline h-5 w-5 mr-2" />
                Top Trends
              </h2>
              <div className="space-y-3">
                {results.top_trends.map((trend: any, i: number) => (
                  <div key={i} className="flex justify-between items-center">
                    <span className="font-medium">{trend.kpi}</span>
                    <span className={`px-3 py-1 rounded ${
                      trend.change_pct > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {trend.change_pct > 0 ? '+' : ''}{trend.change_pct.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Decisions */}
          {results.recommended_decisions && results.recommended_decisions.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Recommended Decisions</h2>
              {results.recommended_decisions.map((decision: any, i: number) => (
                <div key={i} className="mb-4 last:mb-0">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      decision.confidence === 'high' ? 'bg-green-100 text-green-800' :
                      decision.confidence === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {decision.confidence.toUpperCase()}
                    </span>
                    <h3 className="font-semibold">{decision.decision}</h3>
                  </div>
                  <p className="text-sm text-gray-600">{decision.rationale}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

---

## Testing

### Test the API

```bash
# Start the server
~/.local/bin/uv run python metrics_copilot/api.py

# In another terminal, test with curl
curl -X POST "http://localhost:8000/analyze/quick" \
  -F "file=@examples/sample_timeseries.csv"
```

### Test from Lovable

1. Start the API server locally
2. In your Lovable app, create a file upload component
3. Use the example code above to call the API
4. Display the results in your UI

---

## Production Deployment

### Option A: Railway.app

1. Create `Procfile`:
```
web: uvicorn metrics_copilot.api:app --host 0.0.0.0 --port $PORT
```

2. Deploy to Railway

### Option B: Render.com

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: metrics-copilot-api
    runtime: python
    buildCommand: pip install -r requirements.txt -r requirements-api.txt
    startCommand: uvicorn metrics_copilot.api:app --host 0.0.0.0 --port $PORT
```

2. Connect your GitHub repo to Render

---

## Security Notes

- In production, update CORS settings to only allow your Lovable app domain
- Add authentication if needed (API keys, JWT, etc.)
- Implement rate limiting
- Validate file sizes (add max size limit)
- Scan uploaded files for security

---

## Need Help?

- API Documentation: `http://localhost:8000/docs` (Swagger UI)
- Check the example code in this file
- Test with the sample CSV files in `examples/`
