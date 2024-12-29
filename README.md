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

## Use Cases 📊

- **Data Quality**: Validate join relationships between tables, mismapped/misaligned tables.
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
