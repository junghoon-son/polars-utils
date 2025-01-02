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

# Create sample DataFrames
df1 = pl.DataFrame({
    "id": [1, 2, 3, 4, None],
    "name": ["A", "B", "C", "D", "E"],
    "value": [10, 20, 30, 40, 50],
    "mixed": ["1", "2", "3", "4", "5"]
})

df2 = pl.DataFrame({
    "id": [1, 2, 3, 3, None],
    "name": ["A", "B", "C", "C", "F"],
    "score": [100, 200, 300, 400, 500],
    "mixed": [1, 2, 3, 4, 5]
})

# Analyze join possibilities
df1.polars_utils.join_analysis(df2)
```

Output:
```
                                             Join Analysis Results                                              
╔═════════════╦══════════════╦════════════════╦══════════════╦═══════════════╦══════════════╦══════════════════╗
║ Left Column ║ Right Column ║ Types          ║ Left Match % ║ Right Match % ║ Matched Rows ║ Coercion Applied ║
╠═════════════╬══════════════╬════════════════╬══════════════╬═══════════════╬══════════════╬══════════════════╣
║ mixed       ║ mixed        ║ String ↔ Int64 ║ 100.0%       ║ 100.0%        ║ 5            ║ R → String       ║
║ id          ║ mixed        ║ Int64          ║ 80.0%        ║ 80.0%         ║ 4            ║ -                ║
║ id          ║ id           ║ Int64          ║ 60.0%        ║ 80.0%         ║ 4            ║ -                ║
║ name        ║ name         ║ String         ║ 60.0%        ║ 80.0%         ║ 4            ║ -                ║
╚═════════════╩══════════════╩════════════════╩══════════════╩═══════════════╩══════════════╩══════════════════╝
```


### Type Coercion

```python
# Create DataFrames with different types
users = pl.DataFrame({
    "user_id": ["1", "2", "3", "4"],  # String IDs
    "name": ["Alice", "Bob", "Charlie", "David"],
})

orders = pl.DataFrame({
    "user_id": [1, 2, 2, 3],  # Integer IDs
    "order_amount": [100, 200, 150, 300],
})

# Analyze join possibilities
users.polars_utils.join_analysis(orders)
```

Output:
```
                                             Join Analysis Results                                              
╔═════════════╦══════════════╦════════════════╦══════════════╦═══════════════╦══════════════╦══════════════════╗
║ Left Column ║ Right Column ║ Types          ║ Left Match % ║ Right Match % ║ Matched Rows ║ Coercion Applied ║
╠═════════════╬══════════════╬════════════════╬══════════════╬═══════════════╬══════════════╬══════════════════╣
║ user_id     ║ user_id      ║ String ↔ Int64 ║ 75.0%        ║ 100.0%        ║ 4            ║ R → String       ║
║ user_id     ║ order_amount ║ String ↔ Int64 ║ -            ║ -             ║ -            ║ R → String       ║
║ name        ║ user_id      ║ String ↔ Int64 ║ -            ║ -             ║ -            ║ R → String       ║
║ name        ║ order_amount ║ String ↔ Int64 ║ -            ║ -             ║ -            ║ R → String       ║
╚═════════════╩══════════════╩════════════════╩══════════════╩═══════════════╩══════════════╩══════════════════╝
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

### 4. Visual Data Analysis
Create compact visualizations within your DataFrame:
- Single-line histograms for numeric columns
- Group-wise distribution visualization
- Customizable characters and widths
- Works with both groupby and window operations

```python
# Create histograms by category
df.group_by("category").agg(
    pl.col("values")
    .polars_utils.create_histogram()
    .alias("distribution")
)

# Add histograms as a column
df.with_columns(
    pl.col("values")
    .polars_utils.create_histogram()
    .over("category")
    .alias("distribution")
)
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
