import polars as pl
from polars_utils import register_extensions

register_extensions()

# Create sample DataFrames
df1 = pl.DataFrame({
    "id": [1, 2, 3, 4, None],
    "name": ["A", "B", "C", "D", "E"],
    "value": [10, 20, 30, 40, 50],
})

df2 = pl.DataFrame({
    "id": [1, 2, 3, 3, None],
    "name": ["A", "B", "C", "C", "F"],
    "score": [100, 200, 300, 400, 500],
})

# Analyze join possibilities
print("Join Analysis:")
df1.polars_utils.join_analysis(df2)

# Perform the join
joined = df1.join(df2, on="id", how="left")

print("\nJoined Result:")
print(joined) 