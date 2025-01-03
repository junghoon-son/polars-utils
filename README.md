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
import polars as pl
from polars_utils import register_extensions

register_extensions()

# Example 1: Basic distribution by age groups
df = pl.DataFrame({
    "age_group": ["0-18", "19-30", "31-50", "51+"],
    "values": [
        [10, 12, 15, 15, 16, 17, 18],  # Young, clustered
        [20, 21, 21, 25, 25, 25, 29],  # Young adults, right skewed
        [35, 35, 35, 40, 45, 45, 50],  # Middle age, bimodal
        [55, 60, 65, 70, 70, 75, 80],  # Senior, spread out
    ]
})

result = df.with_columns(pl.col("values").list.explode()).group_by("age_group").agg(
    pl.col("values").polars_utils.create_histogram(max_width=30).alias("distribution")
)
print(result)

# Example 2: Sales patterns across weekdays
df_sales = pl.DataFrame({
    "day": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "sales": [
        [100, 120, 110, 105, 115],  # Monday - consistent
        [150, 155, 145, 160, 140],  # Tuesday - high, stable
        [200, 180, 190, 195, 185],  # Wednesday - peak
        [160, 150, 155, 145, 165],  # Thursday - declining
        [120, 125, 115, 110, 130],  # Friday - low, variable
    ]
})

result = df_sales.with_columns(pl.col("sales").list.explode()).group_by("day").agg(
    pl.col("sales").polars_utils.create_histogram(max_width=20).alias("distribution")
)
print("\nSales Distribution by Day:")
print(result)
```

Example Outputs:

1. Age Group Distribution:
```
shape: (4, 2)
┌───────────┬──────────────────────────────────────────────────────┐
│ age_group ┆ distribution                                         │
│ ---       ┆ ---                                                  │
│ str       ┆ str                                                  │
╞═══════════╪══════════════════════════════════════════════════════╡
│ 0-18      ┆ ▁▂▃▃█████▇▇                      [10.00, 18.00]     │
│ 19-30     ┆ ▁▂▂▃▃█████▇▅▃▂                   [20.00, 29.00]     │
│ 31-50     ┆ ████▁▁▂▂████▁▁▂▂                 [35.00, 50.00]     │
│ 51+       ┆ ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁                  [55.00, 80.00]     │
└───────────┴──────────────────────────────────────────────────────┘
```

2. Sales Distribution:
```
shape: (5, 2)
┌─────┬────────────────────────────────────────────┐
│ day ┆ distribution                               │
│ --- ┆ ---                                        │
│ str ┆ str                                        │
╞═════╪════════════════════════════════════════════╡
│ Mon ┆ ▅█▃▁█▆              [100.00, 120.00]      │
│ Tue ┆ ▁▇█▅███             [140.00, 160.00]      │
│ Wed ┆ ▂▇▆█████            [180.00, 200.00]      │
│ Thu ┆ ▁▆██▇▅▂             [145.00, 165.00]      │
│ Fri ┆ ▂▃█▇▅▁              [110.00, 130.00]      │
└─────┴────────────────────────────────────────────┘
```

The histograms provide quick visual insights:
- Age groups show different distribution patterns (clustered, skewed, bimodal)
- Sales patterns reveal daily trends (peak days, variability)
- Min/max values help contextualize the distributions

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
