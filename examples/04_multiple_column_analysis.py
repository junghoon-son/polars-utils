import polars as pl
from polars_utils import register_extensions

register_extensions()

# Create DataFrames with multiple potential join columns
employees = pl.DataFrame({
    "emp_id": [1, 2, 3, 4],
    "dept_id": [10, 20, 20, 30],
    "location": ["NY", "SF", "NY", "LA"],
    "name": ["Alice", "Bob", "Charlie", "David"],
})

departments = pl.DataFrame({
    "dept_id": [10, 20, 30],
    "location": ["NY", "SF", "LA"],
    "dept_name": ["Sales", "Engineering", "Marketing"],
})

# Analyze join possibilities
print("Join Analysis:")
employees.polars_utils.join_analysis(departments)

# Show different join strategies
print("\nSingle Column Join (dept_id):")
print(employees.join(departments, on="dept_id"))

print("\nMulti-Column Join (dept_id and location):")
print(employees.join(departments, on=["dept_id", "location"])) 