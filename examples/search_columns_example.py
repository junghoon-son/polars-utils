import polars as pl
from polars_utils import register_extensions

register_extensions()

# Create sample DataFrame
df = pl.DataFrame({
    "id": [1, 2, 3, 4],
    "name": ["Alice Smith", "Bob Jones", "Charlie Brown", "David Smith"],
    "email": ["alice@test.com", "bob@test.com", "charlie@test.com", "david@test.com"],
    "phone": ["123-456", "789-012", "345-678", "901-234"]
})

# Search for 'Smith' in all columns
print("Searching for 'Smith' in all columns:")
results = df.polars_utils.search_columns("Smith")
print(results)

# Search for email pattern
print("\nSearching for email addresses (matches only):")
results = df.polars_utils.search_columns(r".*@.*\.com", matches_only=True)
print(results)
