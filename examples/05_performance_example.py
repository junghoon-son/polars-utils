import polars as pl
from polars_utils import register_extensions
import time
import random

register_extensions()

# Create larger DataFrames with realistic data patterns
size = 100_000
overlap_ratio = 0.7  # 70% overlap

# Generate IDs with partial overlap
all_ids = list(range(size * 2))
df1_ids = random.sample(all_ids, size)
df2_ids = random.sample(df1_ids[:int(size * overlap_ratio)] + all_ids[size:], size)

df1 = pl.DataFrame({
    "id": df1_ids,
    "value": [f"value_{i}" for i in range(size)],
    "category": random.choices(["A", "B", "C"], k=size)
})

df2 = pl.DataFrame({
    "id": df2_ids,
    "score": [random.random() * 100 for _ in range(size)],
    "status": random.choices(["active", "inactive"], k=size)
})

# Analyze join possibilities
start_time = time.time()
print("Join Analysis:")
df1.polars_utils.join_analysis(df2)
print(f"Analysis completed in {time.time() - start_time:.2f} seconds")

# Show join statistics
print("\nJoin Results:")
inner_joined = df1.join(df2, on="id", how="inner")
left_joined = df1.join(df2, on="id", how="left")

print(f"Original Rows: df1={df1.shape[0]}, df2={df2.shape[0]}")
print(f"Inner Join Rows: {inner_joined.shape[0]}")
print(f"Left Join Rows: {left_joined.shape[0]}")
print(f"Match Rate: {inner_joined.shape[0]/df1.shape[0]*100:.1f}%") 