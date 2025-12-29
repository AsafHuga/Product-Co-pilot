"""FastAPI wrapper for Product Metrics Copilot."""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path

from metrics_copilot.cli import analyze_csv

app = FastAPI(
    title="Product Metrics Copilot API",
    description="Automated product analytics and insights API",
    version="0.1.0"
)

# Enable CORS for Lovable frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Lovable app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "Product Metrics Copilot API",
        "version": "0.1.0",
        "status": "healthy"
    }


@app.post("/analyze")
async def analyze_metrics(file: UploadFile = File(...)):
    """
    Analyze a CSV file and return insights.

    Args:
        file: CSV file upload

    Returns:
        JSON with analysis results
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Create temporary output path for JSON
        output_path = temp_path.replace('.csv', '_report.json')

        # Run analysis
        report = analyze_csv(temp_path, output_json=output_path)

        # Convert report to dict
        result = report.to_dict()

        # Add metadata
        result['metadata'] = {
            'filename': file.filename,
            'file_size_bytes': len(content),
        }

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if os.path.exists(output_path):
            os.unlink(output_path)


@app.post("/analyze/quick")
async def quick_analyze(file: UploadFile = File(...)):
    """
    Quick analysis returning only key insights (faster response).

    Args:
        file: CSV file upload

    Returns:
        JSON with executive summary and key findings
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    # Save uploaded file to temporary location
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Run analysis
        report = analyze_csv(temp_path)

        # Return only key insights
        result = {
            'executive_summary': {
                'row_count': report.data_profile.row_count,
                'column_count': report.data_profile.column_count,
                'data_mode': report.data_profile.data_mode,
                'time_range': report.time_range,
            },
            'kpis': [
                {
                    'name': kpi.column_name,
                    'type': kpi.kpi_type,
                    'is_primary': kpi.is_primary
                }
                for kpi in report.kpis_detected[:5]
            ],
            'top_trends': [
                {
                    'kpi': trend.kpi,
                    'direction': trend.direction,
                    'change_pct': trend.overall_change_pct
                }
                for trend in report.overall_trends[:5]
            ],
            'top_change_points': [
                {
                    'date': cp.date,
                    'kpi': cp.kpi,
                    'delta_pct': cp.delta_pct,
                    'confidence': cp.confidence
                }
                for cp in report.change_points[:3]
            ],
            'top_hypotheses': [
                {
                    'description': h.description,
                    'confidence': h.confidence
                }
                for h in report.hypotheses[:3]
            ],
            'recommended_decisions': [
                {
                    'decision': d.decision,
                    'confidence': d.confidence,
                    'rationale': d.rationale
                }
                for d in report.recommended_decisions[:2]
            ]
        }

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
