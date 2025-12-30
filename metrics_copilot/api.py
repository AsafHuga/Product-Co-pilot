"""FastAPI wrapper for Product Metrics Copilot."""

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path
from typing import Optional
import pandas as pd

from metrics_copilot.cli import analyze_csv
from metrics_copilot.data_transformer import auto_transform_data, preview_transformation

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


@app.post("/preview")
async def preview_data_transformation(file: UploadFile = File(...)):
    """
    Preview what transformations will be applied to raw data.

    Args:
        file: CSV file upload

    Returns:
        JSON with preview of transformations
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
        preview = preview_transformation(temp_path)
        preview['filename'] = file.filename
        return JSONResponse(content=preview)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview failed: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@app.post("/analyze")
async def analyze_metrics(
    file: UploadFile = File(...),
    use_llm: bool = Query(True, description="Use LLM for enhanced insights"),
    auto_transform: bool = Query(True, description="Automatically transform raw data to required format")
):
    """
    Analyze a CSV file and return insights.

    Args:
        file: CSV file upload
        use_llm: Whether to use OpenAI LLM for enhanced insights (default: True)
        auto_transform: Whether to automatically transform raw data (default: True)

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

    transformed_path = None
    try:
        analysis_path = temp_path
        transformation_metadata = None

        # Auto-transform if requested
        if auto_transform:
            try:
                transformed_df, transformation_metadata = auto_transform_data(temp_path)

                # Save transformed data to new temp file
                transformed_path = temp_path.replace('.csv', '_transformed.csv')
                transformed_df.to_csv(transformed_path, index=False)
                analysis_path = transformed_path
            except Exception as transform_error:
                # If transformation fails, try analyzing original data
                transformation_metadata = {
                    "transformation_attempted": True,
                    "transformation_failed": True,
                    "error": str(transform_error),
                    "using_original_data": True
                }

        # Create temporary output path for JSON
        output_path = analysis_path.replace('.csv', '_report.json')

        # Run analysis
        report = analyze_csv(analysis_path, output_json=output_path, use_llm=use_llm)

        # Convert report to dict
        result = report.to_dict()

        # Add metadata
        result['metadata'] = {
            'filename': file.filename,
            'file_size_bytes': len(content),
            'auto_transform_enabled': auto_transform,
            'transformation_metadata': transformation_metadata
        }

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    finally:
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if transformed_path and os.path.exists(transformed_path):
            os.unlink(transformed_path)
        if 'output_path' in locals() and os.path.exists(output_path):
            os.unlink(output_path)


@app.post("/analyze/quick")
async def quick_analyze(
    file: UploadFile = File(...),
    use_llm: bool = Query(True, description="Use LLM for enhanced insights"),
    auto_transform: bool = Query(True, description="Automatically transform raw data to required format")
):
    """
    Quick analysis returning only key insights (faster response).

    Args:
        file: CSV file upload
        use_llm: Whether to use OpenAI LLM for enhanced insights (default: True)
        auto_transform: Whether to automatically transform raw data (default: True)

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

    transformed_path = None
    try:
        analysis_path = temp_path
        transformation_metadata = None

        # Auto-transform if requested
        if auto_transform:
            try:
                transformed_df, transformation_metadata = auto_transform_data(temp_path)

                # Save transformed data to new temp file
                transformed_path = temp_path.replace('.csv', '_transformed.csv')
                transformed_df.to_csv(transformed_path, index=False)
                analysis_path = transformed_path
            except Exception as transform_error:
                # If transformation fails, try analyzing original data
                transformation_metadata = {
                    "transformation_attempted": True,
                    "transformation_failed": True,
                    "error": str(transform_error),
                    "using_original_data": True
                }

        # Run analysis
        report = analyze_csv(analysis_path, use_llm=use_llm)

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
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if transformed_path and os.path.exists(transformed_path):
            os.unlink(transformed_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
