import polars as pl
from polars_utils import register_extensions

register_extensions()

# Create DataFrames with different types
users = pl.DataFrame({
    "user_id": ["1", "2", "3", "4"],  # String IDs
    "name": ["Alice", "Bob", "Charlie", "David"],
})

orders = pl.DataFrame({
    "user_id": [1, 2, 2, 3],  # Integer IDs
    "order_amount": [100, 200, 150, 300],
})

# Analyze join possibilities - will show type differences and potential coercions
print("Join Analysis:")
users.polars_utils.join_analysis(orders)

# Convert string IDs to integers for joining
users_converted = users.with_columns([
    pl.col("user_id").cast(pl.Int64)
])

# Perform the join with converted types
joined = users_converted.join(
    orders,
    on="user_id",
    how="left"
)

print("\nJoined Result:")
print(joined)

print("\nJoined DataFrame Schema:")
print(joined.schema) 