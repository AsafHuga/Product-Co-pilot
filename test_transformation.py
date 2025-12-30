#!/usr/bin/env python3
"""Test the data transformation functionality."""

import sys
sys.path.insert(0, '/Users/asafhuga/metrics_copilot')

from data_transformer import auto_transform_data, preview_transformation
import json

# Test preview
print("=" * 60)
print("TESTING PREVIEW TRANSFORMATION")
print("=" * 60)

preview = preview_transformation('/Users/asafhuga/Desktop/Mixpanel_Formatted_Report.csv')
print(f"\nDetected Format: {preview['detected_format']}")
print(f"Planned Transformation: {preview['planned_transformation']}")
print(f"Original Shape: {preview['original_shape']}")
print(f"Date Column: {preview['date_column']}")
print(f"Numeric Columns Count: {preview['numeric_count']}")
print(f"\nSample Data (first 3 rows):")
for row in preview['sample_data'][:3]:
    print(f"  {row}")

# Test actual transformation
print("\n" + "=" * 60)
print("TESTING ACTUAL TRANSFORMATION")
print("=" * 60)

df, metadata = auto_transform_data('/Users/asafhuga/Desktop/Mixpanel_Formatted_Report.csv')

print(f"\nOriginal Shape: {metadata['original_shape']}")
print(f"Final Shape: {metadata['final_shape']}")
print(f"Detected Format: {metadata.get('detected_format', 'N/A')}")
print(f"\nFinal Columns: {metadata['final_columns']}")
print(f"\nTransformation Steps:")
for step in metadata.get('steps', []):
    print(f"  - {step['step']}")
    if 'note' in step:
        print(f"    Note: {step['note']}")

print(f"\nFirst 5 rows of transformed data:")
print(df.head())

print("\n✅ Transformation test completed successfully!")
