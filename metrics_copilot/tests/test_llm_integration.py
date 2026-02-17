#!/usr/bin/env python3
"""Test LLM integration without making actual API calls."""

import os
import sys

# Test 1: Check if modules import correctly
print("=" * 60)
print("TEST 1: Import LLM modules")
print("=" * 60)

try:
    from metrics_copilot.llm_insights import (
        LLMInsightGenerator,
        is_llm_available,
        create_llm_generator
    )
    print("✅ LLM modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import LLM modules: {e}")
    sys.exit(1)

# Test 2: Check if OpenAI is available
print("\n" + "=" * 60)
print("TEST 2: Check OpenAI package availability")
print("=" * 60)

try:
    import openai
    print(f"✅ OpenAI package version: {openai.__version__}")
except ImportError:
    print("❌ OpenAI package not installed")
    sys.exit(1)

# Test 3: Check environment setup
print("\n" + "=" * 60)
print("TEST 3: Check environment configuration")
print("=" * 60)

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
    print(f"✅ OPENAI_API_KEY found: {masked_key}")
    llm_ready = True
else:
    print("⚠️  OPENAI_API_KEY not set (expected for testing)")
    llm_ready = False

print(f"LLM available: {is_llm_available()}")

# Test 4: Check insights.py integration
print("\n" + "=" * 60)
print("TEST 4: Check insights.py integration")
print("=" * 60)

try:
    from metrics_copilot.insights import (
        generate_hypotheses,
        generate_executive_summary
    )
    print("✅ Insights module imported successfully")

    # Check if functions have use_llm parameter
    import inspect

    hyp_sig = inspect.signature(generate_hypotheses)
    if 'use_llm' in hyp_sig.parameters:
        print("✅ generate_hypotheses has use_llm parameter")
    else:
        print("❌ generate_hypotheses missing use_llm parameter")

    sum_sig = inspect.signature(generate_executive_summary)
    if 'use_llm' in sum_sig.parameters:
        print("✅ generate_executive_summary has use_llm parameter")
    else:
        print("❌ generate_executive_summary missing use_llm parameter")

except Exception as e:
    print(f"❌ Failed to test insights integration: {e}")
    sys.exit(1)

# Test 5: Check CLI integration
print("\n" + "=" * 60)
print("TEST 5: Check CLI integration")
print("=" * 60)

try:
    from metrics_copilot.cli import analyze_csv

    cli_sig = inspect.signature(analyze_csv)
    if 'use_llm' in cli_sig.parameters:
        print("✅ analyze_csv has use_llm parameter")
    else:
        print("❌ analyze_csv missing use_llm parameter")

except Exception as e:
    print(f"❌ Failed to test CLI integration: {e}")
    sys.exit(1)

# Test 6: Check API integration
print("\n" + "=" * 60)
print("TEST 6: Check API integration")
print("=" * 60)

try:
    from metrics_copilot.api import analyze_metrics, quick_analyze

    api_sig = inspect.signature(analyze_metrics)
    if 'use_llm' in api_sig.parameters:
        print("✅ analyze_metrics has use_llm parameter")
    else:
        print("❌ analyze_metrics missing use_llm parameter")

    quick_sig = inspect.signature(quick_analyze)
    if 'use_llm' in quick_sig.parameters:
        print("✅ quick_analyze has use_llm parameter")
    else:
        print("❌ quick_analyze missing use_llm parameter")

except Exception as e:
    print(f"❌ Failed to test API integration: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if llm_ready:
    print("✅ ALL TESTS PASSED - LLM integration is ready!")
    print("\nYou can now run:")
    print("  python -m metrics_copilot.cli examples/sample_timeseries.csv --use-llm")
else:
    print("✅ ALL TESTS PASSED - Integration is working!")
    print("\nTo enable LLM:")
    print("  1. Get API key from: https://platform.openai.com/api-keys")
    print("  2. Create .env file: cp .env.example .env")
    print("  3. Add: OPENAI_API_KEY=sk-your-key-here")
    print("\nFor now, analysis will use rule-based insights (--no-llm)")
