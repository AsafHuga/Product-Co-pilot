"""Setup script for Product Metrics Copilot."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="metrics-copilot",
    version="0.1.0",
    author="Product Metrics Copilot",
    description="Automated product analytics and insights for product managers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "chardet>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "metrics-copilot=metrics_copilot.cli:main",
        ],
    },
)
