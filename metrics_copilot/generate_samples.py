"""Generate sample CSV files for testing."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def generate_timeseries_sample(output_path: str = "examples/sample_timeseries.csv"):
    """Generate a sample time series CSV with product metrics."""
    np.random.seed(42)
    random.seed(42)

    # Generate 90 days of data
    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(90)]

    data = []
    for i, date in enumerate(dates):
        # Create a change point at day 45
        if i < 45:
            base_dau = 10000 + np.random.normal(0, 500)
            base_conversion = 0.05 + np.random.normal(0, 0.005)
            base_revenue = 50000 + np.random.normal(0, 2000)
        else:
            # Simulate an improvement after a product launch
            base_dau = 12000 + np.random.normal(0, 500)  # 20% increase
            base_conversion = 0.058 + np.random.normal(0, 0.005)  # 16% increase
            base_revenue = 60000 + np.random.normal(0, 2000)  # 20% increase

        # Add weekly seasonality
        day_of_week = date.weekday()
        if day_of_week >= 5:  # Weekend
            base_dau *= 0.8
            base_conversion *= 1.1

        # Generate segments with different performance
        for platform in ["iOS", "Android", "Web"]:
            for country in ["US", "UK", "DE"]:
                # Platform effects
                platform_multiplier = {"iOS": 1.2, "Android": 0.9, "Web": 1.0}[platform]
                # Country effects
                country_multiplier = {"US": 1.3, "UK": 1.0, "DE": 0.8}[country]

                dau = max(0, base_dau * platform_multiplier * country_multiplier / 9 + np.random.normal(0, 100))
                sessions = dau * (2.5 + np.random.normal(0, 0.3))
                conversion_rate = min(
                    1.0, max(0, base_conversion * platform_multiplier * country_multiplier + np.random.normal(0, 0.01))
                )
                conversions = dau * conversion_rate
                revenue = base_revenue * platform_multiplier * country_multiplier / 9 + np.random.normal(0, 500)
                arpdau = revenue / dau if dau > 0 else 0

                data.append(
                    {
                        "Date": date.strftime("%Y-%m-%d"),
                        "Platform": platform,
                        "Country": country,
                        "DAU": int(dau),
                        "Sessions": int(sessions),
                        "Conversion Rate": round(conversion_rate, 4),
                        "Conversions": int(conversions),
                        "Revenue": round(revenue, 2),
                        "ARPDAU": round(arpdau, 2),
                    }
                )

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated time series sample: {output_path}")
    return df


def generate_experiment_sample(output_path: str = "examples/sample_experiment.csv"):
    """Generate a sample A/B test CSV."""
    np.random.seed(42)

    data = []

    # Control group: 5000 users
    for i in range(5000):
        variant = "control"
        # Base metrics
        session_duration = max(0, np.random.normal(180, 60))  # 3 minutes avg
        pages_viewed = max(1, int(np.random.normal(5, 2)))
        converted = np.random.random() < 0.05  # 5% conversion
        revenue = np.random.gamma(2, 25) if converted else 0  # $50 avg if converted

        data.append(
            {
                "user_id": f"user_{i}",
                "variant": variant,
                "session_duration": round(session_duration, 1),
                "pages_viewed": pages_viewed,
                "converted": 1 if converted else 0,
                "revenue": round(revenue, 2),
            }
        )

    # Test group: 5000 users with improved conversion
    for i in range(5000, 10000):
        variant = "test"
        # Improved metrics
        session_duration = max(0, np.random.normal(190, 60))  # 5% longer sessions
        pages_viewed = max(1, int(np.random.normal(5.5, 2)))  # 10% more pages
        converted = np.random.random() < 0.058  # 16% relative improvement (5.8% absolute)
        revenue = np.random.gamma(2, 26) if converted else 0  # Slightly higher AOV

        data.append(
            {
                "user_id": f"user_{i}",
                "variant": variant,
                "session_duration": round(session_duration, 1),
                "pages_viewed": pages_viewed,
                "converted": 1 if converted else 0,
                "revenue": round(revenue, 2),
            }
        )

    # Add segments to show heterogeneous effects
    for row in data:
        row["platform"] = random.choice(["iOS", "Android", "Web"])
        row["user_type"] = random.choice(["new", "returning"])

        # iOS shows stronger effect
        if row["variant"] == "test" and row["platform"] == "iOS":
            if random.random() < 0.02:  # Additional 2% conversion boost on iOS
                row["converted"] = 1
                row["revenue"] = round(np.random.gamma(2, 26), 2)

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated experiment sample: {output_path}")
    return df


def generate_messy_sample(output_path: str = "examples/sample_messy.csv"):
    """Generate a messy CSV to test data cleaning."""
    np.random.seed(42)

    dates = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(30)]

    data = []
    for i, date in enumerate(dates):
        # Introduce various data quality issues
        dau = int(10000 + np.random.normal(0, 500))
        conversion_rate = 0.05 + np.random.normal(0, 0.005)

        # Random format variations
        date_format = random.choice(["%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"])

        # Add commas to numbers
        dau_str = f"{dau:,}" if random.random() < 0.5 else str(dau)

        # Add % to conversion rate
        conv_str = f"{conversion_rate*100:.2f}%" if random.random() < 0.5 else str(conversion_rate)

        # Add $ to revenue
        revenue = 50000 + np.random.normal(0, 2000)
        revenue_str = f"${revenue:,.2f}" if random.random() < 0.5 else str(round(revenue, 2))

        # Random missing values
        if random.random() < 0.1:
            dau_str = ""
        if random.random() < 0.1:
            conv_str = ""

        data.append(
            {
                "DATE": date.strftime(date_format),
                "Daily Active Users": dau_str,
                "Conversion %": conv_str,
                "Revenue ($)": revenue_str,
                "Platform": random.choice(["iOS", "Android", "Web", None]),
            }
        )

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Generated messy sample: {output_path}")
    return df


if __name__ == "__main__":
    import os

    os.makedirs("examples", exist_ok=True)

    generate_timeseries_sample()
    generate_experiment_sample()
    generate_messy_sample()

    print("\n✓ All sample files generated successfully!")
