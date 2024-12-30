import polars as pl
from itertools import product
from typing import List, Dict, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich import box
from rich.progress import track


@dataclass
class JoinResult:
    left_column: str
    right_column: str
    left_unique_values: int
    right_unique_values: int
    left_dtype: str
    right_dtype: str
    left_null_count: int
    right_null_count: int
    left_total_rows: int
    right_total_rows: int
    left_matched_rows: int
    right_matched_rows: int
    matched_rows: int  # Total number of relationships
    left_sample_values: List[str]
    right_sample_values: List[str]
    coercion_applied: Optional[str] = None
    error: Optional[str] = None

    @property
    def has_type_mismatch(self) -> bool:
        return self.left_dtype != self.right_dtype

    @property
    def type_mismatch_desc(self) -> str:
        if not self.has_type_mismatch:
            return ""
        return f"{self.left_dtype} ↔ {self.right_dtype}"

    @property
    def left_match_percentage(self) -> float:
        """Percentage of rows in left column that have matches"""
        if self.left_total_rows == 0:
            return 0.0
        return (self.left_matched_rows / self.left_total_rows) * 100

    @property
    def right_match_percentage(self) -> float:
        """Percentage of rows in right column that have matches"""
        if self.right_total_rows == 0:
            return 0.0
        return (self.right_matched_rows / self.right_total_rows) * 100


def coerce_for_join(
    df: pl.DataFrame, column: str, target_type: pl.DataType
) -> pl.DataFrame:
    """
    Attempts to coerce a column to a target type in a safe way for joining.
    """
    current_type = df.select(column).schema[column]

    # If types already match, return original
    if current_type == target_type:
        return df

    # Make a copy to avoid modifying original
    df = df.clone()

    try:
        # String to numeric conversion
        if isinstance(target_type, (pl.Int64, pl.Int32, pl.Int16, pl.Int8)):
            if isinstance(current_type, pl.Utf8):
                # Strip whitespace and remove any non-numeric characters
                df = df.with_columns(
                    [
                        pl.col(column)
                        .str.replace(r"[^0-9-]", "")
                        .cast(target_type, strict=False)
                        .alias(column)
                    ]
                )
            else:
                df = df.with_columns(
                    [pl.col(column).cast(target_type, strict=False).alias(column)]
                )

        # Numeric to string conversion
        elif isinstance(target_type, pl.Utf8):
            df = df.with_columns([pl.col(column).cast(str, strict=False).alias(column)])

    except Exception as e:
        print(f"Warning: Failed to coerce {column} to {target_type}: {e}")
        return df

    # Verify the coercion worked
    new_type = df.select(column).schema[column]
    if not isinstance(new_type, type(target_type)):
        print(
            f"Warning: Coercion failed - column is still {new_type} instead of {target_type}"
        )

    return df


def truncate_with_ellipsis(text: str, max_length: int) -> str:
    """Truncate text and add ellipsis if longer than max_length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_column_name(name: str, max_length: int = 25) -> str:
    """Format column names to be more readable and properly truncated."""
    return truncate_with_ellipsis(name, max_length)


def display_results(results: List[JoinResult]):
    """Display join analysis results in a formatted table."""
    table = Table(title="Join Analysis Results", box=box.DOUBLE)

    # Add columns
    table.add_column("Left Column")
    table.add_column("Right Column")
    table.add_column("Types")
    table.add_column("Left Match %")
    table.add_column("Right Match %")
    table.add_column("Matched Rows")
    table.add_column("Coercion Applied")

    # Add rows
    for result in results:
        left_match_pct = (
            f"{result.left_match_percentage:.1f}%"
            if result.left_match_percentage > 0
            else "-"
        )
        right_match_pct = (
            f"{result.right_match_percentage:.1f}%"
            if result.right_match_percentage > 0
            else "-"
        )

        table.add_row(
            result.left_column,
            result.right_column,
            result.type_mismatch_desc
            if result.has_type_mismatch
            else str(result.left_dtype),
            left_match_pct,
            right_match_pct,
            str(result.matched_rows) if result.matched_rows > 0 else "-",
            result.coercion_applied or "-",
        )

    console = Console()
    console.print(table)


def format_error(error: str) -> str:
    """Format error messages to be more concise and readable."""
    if "datatypes of join keys don't match" in error:
        return "Type mismatch error"
    if len(error) > 30:
        return error[:27] + "..."
    return error


@pl.api.register_dataframe_namespace("polars_utils")
class PolarsUtils:
    def __init__(self, df: pl.DataFrame):
        self._df = df

    def analyze_joins(
        self, other_df: pl.DataFrame, exclude_dtypes: Optional[List[type]] = None
    ) -> List[JoinResult]:
        """
        Analyze potential join relationships between two DataFrames and return results.

        Parameters
        ----------
        other_df : pl.DataFrame
            The DataFrame to analyze joins with
        exclude_dtypes : List[type], optional
            List of dtypes to exclude from analysis

        Returns
        -------
        List[JoinResult]
            List of join analysis results
        """
        results = []
        exclude_dtypes = exclude_dtypes or []

        # Get all column combinations
        column_pairs = list(product(self._df.columns, other_df.columns))

        for left_col, right_col in track(
            column_pairs, description="Analyzing joins..."
        ):
            # Skip excluded dtypes
            left_dtype = self._df[left_col].dtype
            right_dtype = other_df[right_col].dtype

            if (
                type(left_dtype) in exclude_dtypes
                or type(right_dtype) in exclude_dtypes
            ):
                continue

            try:
                # Try coercing types if they don't match
                left_df = self._df
                right_df = other_df
                coercion_note = None

                if left_dtype != right_dtype:
                    # Try coercing right to left type first
                    try:
                        right_df = coerce_for_join(other_df, right_col, left_dtype)
                        coercion_note = f"R → {left_dtype}"
                    except:
                        # If that fails, try coercing left to right type
                        try:
                            left_df = coerce_for_join(self._df, left_col, right_dtype)
                            coercion_note = f"L → {right_dtype}"
                        except:
                            pass

                # Get unique values from both columns
                left_unique = set(left_df[left_col].unique().drop_nulls())
                right_unique = set(right_df[right_col].unique().drop_nulls())

                # Find matching values
                matched_values = left_unique & right_unique

                if matched_values:
                    # Count matching rows for both sides
                    left_matched_rows = left_df.filter(
                        pl.col(left_col).is_in(matched_values)
                    ).shape[0]
                    right_matched_rows = right_df.filter(
                        pl.col(right_col).is_in(matched_values)
                    ).shape[0]

                    # Total matched rows is the larger of the two (shows total relationships)
                    matched_rows = max(left_matched_rows, right_matched_rows)
                else:
                    left_matched_rows = right_matched_rows = matched_rows = 0

                result = JoinResult(
                    left_column=left_col,
                    right_column=right_col,
                    left_unique_values=len(left_unique),
                    right_unique_values=len(right_unique),
                    left_dtype=left_dtype,
                    right_dtype=right_dtype,
                    left_null_count=self._df[left_col].null_count(),
                    right_null_count=other_df[right_col].null_count(),
                    left_total_rows=len(self._df),
                    right_total_rows=len(other_df),
                    left_matched_rows=left_matched_rows,
                    right_matched_rows=right_matched_rows,
                    matched_rows=matched_rows,
                    left_sample_values=[
                        str(x)
                        for x in self._df[left_col].drop_nulls().head(3).to_list()
                    ],
                    right_sample_values=[
                        str(x)
                        for x in other_df[right_col].drop_nulls().head(3).to_list()
                    ],
                    coercion_applied=coercion_note,
                )

            except Exception as e:
                # Even if join fails, try to get diagnostics
                try:
                    left_dtype = str(self._df.select(left_col).schema[left_col])
                    right_dtype = str(other_df.select(right_col).schema[right_col])
                    left_null_count = self._df[left_col].null_count()
                    right_null_count = other_df[right_col].null_count()
                    left_sample = self._df[left_col].drop_nulls().head(3).to_list()
                    right_sample = other_df[right_col].drop_nulls().head(3).to_list()
                    left_sample_values = [str(x) for x in left_sample]
                    right_sample_values = [str(x) for x in right_sample]
                except Exception:
                    left_dtype = "unknown"
                    right_dtype = "unknown"
                    left_null_count = -1
                    right_null_count = -1
                    left_sample_values = []
                    right_sample_values = []

                result = JoinResult(
                    left_column=left_col,
                    right_column=right_col,
                    left_unique_values=self._df[left_col].n_unique(),
                    right_unique_values=other_df[right_col].n_unique(),
                    left_dtype=left_dtype,
                    right_dtype=right_dtype,
                    left_null_count=left_null_count,
                    right_null_count=right_null_count,
                    left_total_rows=len(self._df),
                    right_total_rows=len(other_df),
                    left_matched_rows=0,
                    right_matched_rows=0,
                    matched_rows=0,
                    left_sample_values=left_sample_values,
                    right_sample_values=right_sample_values,
                    coercion_applied=None,
                    error=str(e),
                )

            results.append(result)

        return sorted(
            results,
            key=lambda x: (x.left_match_percentage + x.right_match_percentage) / 2,
            reverse=True,
        )

    def join_analysis(
        self, other_df: pl.DataFrame, exclude_dtypes: Optional[List[type]] = None
    ):
        """
        Display join analysis results in a formatted table.

        Parameters
        ----------
        other_df : pl.DataFrame
            The DataFrame to analyze joins with
        exclude_dtypes : List[type], optional
            List of dtypes to exclude from analysis
        """
        results = self.analyze_joins(other_df, exclude_dtypes)
        display_results(results)

    def search_columns(self, regex: str, matches_only: bool = False) -> pl.DataFrame:
        """
        Search all columns for a regex pattern.

        Parameters
        ----------
        regex : str
            Regular expression pattern to search for
        matches_only : bool, default False
            If True, only show columns with matches

        Returns
        -------
        pl.DataFrame
            DataFrame containing search results with columns:
            - column_name: Name of the column
            - matches: List of matching values
            - n: Number of matches
            - percent: Percentage of rows with matches
        """
        dfs = []
        row_count = self._df.shape[0]

        for col in self._df.columns:
            row_df = (
                self._df.select(pl.col(col).cast(pl.Utf8()))
                .filter(pl.col(col).str.contains(regex))
                .group_by(pl.lit(col).alias("column_name"))
                .agg(
                    pl.col(col).alias("matches"),
                    pl.col(col).len().alias("n")
                )
            )

            # Create an empty row if there are no matches
            if (len(row_df) == 0) and (not matches_only):
                row_df = pl.DataFrame(
                    {
                        "column_name": col,
                        "matches": pl.Series("empty lists", [[]], dtype=pl.List),
                        "n": 0,
                    }
                )

            # Append the row with casted types
            dfs.append(
                row_df.select(
                    pl.col("column_name").cast(pl.Utf8()),
                    pl.col("matches").cast(pl.List(pl.Utf8())),
                    pl.col("n").cast(pl.UInt32()),
                    (pl.col("n")/pl.lit(row_count)).cast(pl.Float64).alias("percent")
                )
            )

        return pl.concat(dfs, how="vertical")


def register_extensions():
    """
    Register all Polars extensions.
    This function is called to activate the extensions.
    """
    # The decorators automatically register the extensions
    # This function exists to provide a clear entry point
