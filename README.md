# Polars Utils 🐻‍❄️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Utilities for Polars DataFrame analysis and manipulation, with a focus on making join operations easier to understand and debug.

## Features ✨

- **Join Analysis**: Automatically analyze potential join relationships between DataFrames
- **Type Coercion**: Smart type coercion for join operations
- **Rich Output**: Beautiful formatted tables for analysis results
- **Match Statistics**: Detailed matching statistics for join columns

## Installation 📦

```bash
pip install polars-utils
```

## Quick Start 🚀

```python
import polars as pl
from polars_utils import register_extensions

# Register the extensions
register_extensions()

# Create sample DataFrames
df1 = pl.DataFrame({
    "id": [1, 2, 3, 4],
    "name": ["A", "B", "C", "D"]
})

df2 = pl.DataFrame({
    "id": [1, 2, 3, 5],
    "score": [100, 200, 300, 400]
})

# Analyze join possibilities
df1.polars_utils.join_analysis(df2)
```

Output:
```
                                              Join Analysis Results                                               
╔═════════════╦══════════════╦════════════════╦══════════════╦═══════════════╦═════════╦═════════════════════════╗
║ Left Column ║ Right Column ║ Types          ║ Left Match % ║ Right Match % ║ Matched ║ Coercion Applied        ║
╠═════════════╬══════════════╬════════════════╬══════════════╬═══════════════╬═════════╬═════════════════════════╣
║ id          ║ id           ║ Int64          ║ 75.0%        ║ 75.0%         ║ 3       ║ -                       ║
║ id          ║ score        ║ Int64          ║ -            ║ -             ║ -       ║ -                       ║
║ name        ║ id           ║ String ↔ Int64 ║ -            ║ -             ║ -       ║ Coerced right to String ║
║ name        ║ score        ║ String ↔ Int64 ║ -            ║ -             ║ -       ║ Coerced right to String ║
╚═════════════╩══════════════╩════════════════╩══════════════╩═══════════════╩═════════╩═════════════════════════╝
```

## Features in Detail 🔍

### Join Analysis

The join analysis functionality helps you:
- Identify optimal join keys between DataFrames
- Understand match rates for potential joins
- Detect type mismatches and necessary coercions
- View sample values from both sides of the join

### Example

```python
# Load customer and order data
customers = pl.read_csv("customers.csv")
orders = pl.read_csv("orders.csv")

# Analyze join possibilities
customers.polars_utils.join_analysis(orders)

# Get detailed join statistics
results = customers.polars_utils.analyze_joins(orders)
for result in results:
    print(f"Match rate for {result.left_column}: {result.left_match_percentage:.1f}%")
```

## Use Cases 📊

- **Data Quality**: Validate join relationships between tables
- **Data Exploration**: Discover potential relationships between datasets
- **Debug Joins**: Understand why joins might not be working as expected
- **Data Integration**: Find matching columns between different data sources

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- Built on top of the amazing [Polars](https://github.com/pola-rs/polars) DataFrame library
- Inspired by the need for better join debugging tools in data analysis

---
Made with ❤️ for the Polars community
