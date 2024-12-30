# Polars Utils 🐻‍❄️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A collection of utilities for data exploration and analysis with Polars DataFrames, focusing on making EDA and data processing tasks easier and more insightful.

## Features ✨

### 1. Join Analysis
Automatically analyze potential join relationships between DataFrames:
- Identify optimal join keys
- Detect type mismatches and coercion needs
- Show match rates and relationship patterns
- Handle one-to-many and many-to-one relationships

```python
import polars as pl
from polars_utils import register_extensions

register_extensions()

# Analyze join possibilities between customers and orders
customers.polars_utils.join_analysis(orders)
```

### 2. Data Quality Analysis
Analyze data quality across your DataFrame:
- Null value analysis
- Cardinality measurements
- Type distribution
- Value patterns


### 3. Regex Search
Search for patterns across all columns and values in your DataFrame:
- Regex pattern matching
- Match counts and percentages
- Filter to matching columns only
- Handles mixed data types automatically

```python
# Search for email patterns across all columns
results = df.polars_utils.regex_search(r".*@.*\.com")

# Only show columns with matches
results = df.polars_utils.regex_search("pattern", matches_only=True)
```

## Installation 📦

```bash
pip install polars-utils
```

## Use Cases 📊

- **Data Exploration**: Quick insights into data relationships and patterns
- **Data Quality**: Identify data issues and inconsistencies
- **Join Debugging**: Understand and fix join problems
- **Pattern Matching**: Find specific patterns across your entire dataset
- **Data Integration**: Analyze relationships between different data sources

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- Built on top of the amazing [Polars](https://github.com/pola-rs/polars) DataFrame library
- Inspired by the need for better data exploration tools

---
Made with ❤️ for the Polars community
