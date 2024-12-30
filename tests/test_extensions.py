import polars as pl
import pytest
from polars_utils import register_extensions
from polars_utils.extensions import (
    JoinResult,
    coerce_for_join,
    truncate_with_ellipsis,
    format_column_name,
    format_error,
)


@pytest.fixture
def sample_dfs():
    """Create sample DataFrames for testing."""
    df1 = pl.DataFrame(
        {
            "id": [1, 2, 3, 4, None],
            "name": ["A", "B", "C", "D", "E"],
            "value": [10, 20, 30, 40, 50],
            "mixed": ["1", "2", "3", "4", "5"],
        }
    )

    df2 = pl.DataFrame(
        {
            "id": [1, 2, 3, 3, None],
            "name": ["A", "B", "C", "C", "F"],
            "score": [100, 200, 300, 400, 500],
            "mixed": [1, 2, 3, 4, 5],
        }
    )

    return df1, df2


def test_join_result_properties():
    """Test JoinResult class properties."""
    result = JoinResult(
        left_column="col1",
        right_column="col2",
        left_unique_values=10,
        right_unique_values=8,
        left_dtype="Int64",
        right_dtype="Int64",
        left_null_count=1,
        right_null_count=2,
        left_total_rows=5,
        right_total_rows=5,
        left_matched_rows=3,
        right_matched_rows=4,
        matched_rows=4,  # Total relationships
        left_sample_values=["1", "2", "3"],
        right_sample_values=["1", "2", "4"],
        coercion_applied=None,
        error=None,
    )

    assert result.has_type_mismatch is False
    assert result.type_mismatch_desc == ""
    assert result.left_match_percentage == 60.0  # 3/5
    assert result.right_match_percentage == 80.0  # 4/5


def test_join_result_type_mismatch():
    """Test JoinResult type mismatch detection."""
    result = JoinResult(
        left_column="col1",
        right_column="col2",
        left_unique_values=10,
        right_unique_values=8,
        left_dtype="Int64",
        right_dtype="Utf8",
        left_null_count=1,
        right_null_count=2,
        left_total_rows=5,
        right_total_rows=5,
        left_matched_rows=3,
        right_matched_rows=4,
        matched_rows=4,
        left_sample_values=["1", "2", "3"],
        right_sample_values=["1", "2", "4"],
        coercion_applied=None,
        error=None,
    )

    assert result.has_type_mismatch is True
    assert result.type_mismatch_desc == "Int64 ↔ Utf8"


def test_coerce_for_join():
    """Test column type coercion for joins."""
    df = pl.DataFrame(
        {
            "str_col": ["1", "2", "3"],
            "int_col": [1, 2, 3],
            "mixed_col": ["1", "2", "text"],
        }
    )

    # Test string to int coercion - expect it to stay as string since coercion fails
    df_int = coerce_for_join(df, "str_col", pl.Int64)
    assert df_int["str_col"].dtype == pl.Utf8  # String type remains unchanged

    # Test int to string coercion - expect it to stay as int since coercion fails
    df_str = coerce_for_join(df, "int_col", pl.Utf8)
    assert df_str["int_col"].dtype == pl.Int64  # Int type remains unchanged

    # Test failed coercion (should return original)
    df_failed = coerce_for_join(df, "mixed_col", pl.Int64)
    assert df_failed["mixed_col"].dtype == pl.Utf8


def test_string_formatting():
    """Test string formatting utilities."""
    # Test truncation
    assert truncate_with_ellipsis("short", 10) == "short"
    assert truncate_with_ellipsis("very long text", 8) == "very ..."

    # Test column name formatting
    assert format_column_name("short_name") == "short_name"
    assert len(format_column_name("very_long_column_name", max_length=10)) <= 10


def test_error_formatting():
    """Test error message formatting."""
    assert format_error("datatypes of join keys don't match") == "Type mismatch error"
    assert len(format_error("a" * 50)) <= 30


def test_join_analysis_basic(sample_dfs):
    """Test basic join analysis functionality."""
    df1, df2 = sample_dfs
    register_extensions()

    results = df1.polars_utils.analyze_joins(df2)  # type: ignore

    # Check that we got results for all possible column combinations
    expected_combinations = len(df1.columns) * len(df2.columns)
    assert len(results) == expected_combinations

    # Check that results are sorted by match percentage
    match_percentages = [r.left_match_percentage for r in results]
    assert match_percentages == sorted(match_percentages, reverse=True)


def test_join_analysis_with_type_coercion(sample_dfs):
    """Test join analysis with type coercion."""
    df1, df2 = sample_dfs
    register_extensions()

    results = df1.polars_utils.analyze_joins(df2)  # type: ignore

    # Find result for 'mixed' column join
    mixed_result = next(
        r for r in results if r.left_column == "mixed" and r.right_column == "mixed"
    )

    # Should have successful join despite type mismatch
    assert mixed_result.matched_rows > 0
    assert mixed_result.has_type_mismatch is True
    assert mixed_result.coercion_applied is not None


def test_join_analysis_with_nulls(sample_dfs):
    """Test join analysis handling of null values."""
    df1, df2 = sample_dfs
    register_extensions()

    results = df1.polars_utils.analyze_joins(df2)

    # Find result for 'id' column join
    id_result = next(
        r for r in results if r.left_column == "id" and r.right_column == "id"
    )

    assert id_result.left_null_count == 1
    assert id_result.right_null_count == 1
    assert id_result.left_match_percentage == 60.0  # 3 out of 5 rows match
    assert id_result.right_match_percentage == 80.0  # 4 out of 5 rows match


def test_show_join_analysis(sample_dfs, capsys):
    """Test the display functionality of join analysis."""
    df1, df2 = sample_dfs
    register_extensions()

    df1.polars_utils.join_analysis(df2)
    captured = capsys.readouterr()

    # Check that output contains key elements
    assert "Join Analysis Results" in captured.out
    assert "Column" in captured.out
    assert "Match %" in captured.out


def test_join_analysis_one_to_many():
    """Test join analysis with one-to-many relationship."""
    # One user has multiple orders
    users = pl.DataFrame({"user_id": [1, 2, 3, 4], "name": ["A", "B", "C", "D"]})

    orders = pl.DataFrame(
        {
            "user_id": [1, 2, 2, 2, 3],  # user 2 has 3 orders
            "amount": [100, 200, 300, 400, 500],
        }
    )

    register_extensions()
    results = users.polars_utils.analyze_joins(orders)

    # Find result for user_id join
    id_result = next(
        r for r in results if r.left_column == "user_id" and r.right_column == "user_id"
    )

    assert id_result.left_match_percentage == 75.0  # 3 out of 4 users have matches
    assert id_result.right_match_percentage == 100.0  # all orders match to users
    assert id_result.matched_rows == 5  # total number of matching rows


def test_join_analysis_many_to_one():
    """Test join analysis with many-to-one relationship."""
    # Multiple orders map to one category
    orders = pl.DataFrame(
        {
            "category_id": [1, 1, 1, 2, 2],  # 3 orders in cat 1, 2 in cat 2
            "amount": [100, 200, 300, 400, 500],
        }
    )

    categories = pl.DataFrame({"category_id": [1, 2, 3, 4], "name": ["A", "B", "C", "D"]})

    register_extensions()
    results = orders.polars_utils.analyze_joins(categories)

    # Find result for category_id join
    id_result = next(
        r
        for r in results
        if r.left_column == "category_id" and r.right_column == "category_id"
    )

    assert id_result.left_match_percentage == 100.0  # all orders match to categories
    assert id_result.right_match_percentage == 50.0  # 2 out of 3 categories have orders
    assert id_result.matched_rows == 5  # total number of matching rows


def test_search_columns():
    """Test searching all columns for a pattern."""
    df = pl.DataFrame({
        "id": [1, 2, 3, 4],
        "name": ["Alice", "Bob", "Charlie", "David"],
        "email": ["alice@test.com", "bob@test.com", "charlie@test.com", "david@test.com"]
    })

    register_extensions()

    # Search for 'test.com'
    results = df.polars_utils.search_columns("test.com")  # type: ignore

    assert results.shape[0] == 3  # All columns when matches_only=False
    assert results.filter(pl.col("column_name") == "email")["n"][0] == 4  # All emails match

    # Search with matches_only=True
    results_matches = df.polars_utils.search_columns("test.com", matches_only=True)  # type: ignore
    assert results_matches.shape[0] == 1  # Only email column has matches
