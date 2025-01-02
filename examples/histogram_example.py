import polars as pl
import random
from polars_utils import register_extensions

# Set seed for reproducibility
random.seed(42)

register_extensions()

# Example 1: Single Normal Distribution
print("\n1. Single Normal Distribution")
n = 1000
df_normal = pl.DataFrame({
    "values": [random.gauss(mu=0, sigma=1) for _ in range(n)]  # mean=0, std=1
})
print(df_normal.select(pl.col("values").polars_utils.create_histogram().alias("distribution")))

# Example 2: Multiple Normal Distributions
print("\n2. Multiple Normal Distributions with min/max values")
df_multi = pl.DataFrame({
    "group": ["A"] * n + ["B"] * n + ["C"] * n,
    "values": [
        *[random.gauss(mu=-2, sigma=0.5) for _ in range(n)],  # mean=-2, std=0.5
        *[random.gauss(mu=0, sigma=1.0) for _ in range(n)],   # mean=0, std=1.0
        *[random.gauss(mu=2, sigma=0.7) for _ in range(n)]    # mean=2, std=0.7
    ]
})

# Show with stats
result = df_multi.group_by("group").agg(
    pl.col("values").polars_utils.create_histogram(show_stats=True).alias("distribution")
)
print("With min/max values:")
print(result)

# Show without stats
result = df_multi.group_by("group").agg(
    pl.col("values").polars_utils.create_histogram(show_stats=False).alias("distribution")
)
print("\nWithout min/max values:")
print(result)

# Example 3: Different bin widths for normal distribution
print("\n3. Different bin widths")
print("Default bins (20):")
print(df_normal.select(pl.col("values").polars_utils.create_histogram().alias("distribution")))
print("\nWide bins (10):")
print(df_normal.select(pl.col("values").polars_utils.create_histogram(max_width=10).alias("distribution")))
print("\nNarrow bins (50):")
print(df_normal.select(pl.col("values").polars_utils.create_histogram(max_width=50).alias("distribution")))
print("\nNarrow bins (50):")
print(df_normal.select(pl.col("values").polars_utils.create_histogram(max_width=50).alias("distribution")))

# Example 4: Mixture of Distributions
print("\n4. Mixture of Two Normal Distributions")
df_mixture = pl.DataFrame({
    "values": [
        *[random.gauss(mu=-2, sigma=0.5) for _ in range(n//2)],  # First peak
        *[random.gauss(mu=2, sigma=0.5) for _ in range(n//2)]    # Second peak
    ]
})
print(df_mixture.select(pl.col("values").polars_utils.create_histogram().alias("distribution")))

# Example 5: With and without stats
print("\n5. With and without stats")
df = pl.DataFrame({
    "values": [random.gauss(mu=0, sigma=1) for _ in range(100)]
})

print("With stats:")
print(df.select(
    pl.col("values").polars_utils.create_histogram(show_stats=True).alias("distribution")
))

print("\nWithout stats:")
print(df.select(
    pl.col("values").polars_utils.create_histogram(show_stats=False).alias("distribution")
))
