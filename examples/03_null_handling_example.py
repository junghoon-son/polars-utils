import polars as pl
from polars_utils import register_extensions

register_extensions()

# Create DataFrames with null values
customers = pl.DataFrame({
    "customer_id": [1, 2, None, 4, 5],
    "email": ["a@ex.com", None, "c@ex.com", "d@ex.com", "e@ex.com"],
})

purchases = pl.DataFrame({
    "customer_id": [1, 2, 3, None, 5],
    "amount": [100, 200, 300, 400, 500],
})

# Analyze join possibilities
print("Join Analysis:")
customers.polars_utils.join_analysis(purchases)

# Show different join behaviors
print("\nInner Join (excludes nulls):")
print(customers.join(purchases, on="customer_id", how="inner"))

print("\nOuter/Full Join (keeps nulls):")
print(customers.join(purchases, on="customer_id", how="full")) 