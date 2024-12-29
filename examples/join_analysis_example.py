import polars as pl
from polars_utils import register_extensions
from pathlib import Path
from rich import print as rprint
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
from rich.table import Table


def create_section_header(title: str) -> Panel:
    text = Text()
    text.append("═══ ", style="blue")
    text.append(title, style="bold blue")
    text.append(" ═══", style="blue")
    return Panel(text, border_style="blue")


def main():
    console = Console(width=100)

    # Register the extensions
    register_extensions()

    # Get the data directory path
    data_dir = Path(__file__).parent / "data"

    # Load the datasets with explicit schema
    customers = pl.read_csv(
        data_dir / "customers.csv",
        schema={
            "customer_id": pl.Utf8,
            "first_name": pl.Utf8,
            "last_name": pl.Utf8,
            "email": pl.Utf8,
            "region_id": pl.Utf8,
        },
    ).with_columns(
        [pl.col("customer_id").cast(pl.Int64), pl.col("region_id").cast(pl.Int64)]
    )

    orders = pl.read_csv(data_dir / "orders.csv")

    regions = pl.read_csv(
        data_dir / "regions.csv",
        schema={
            "region_id": pl.Utf8,
            "region_name": pl.Utf8,
            "country": pl.Utf8,
            "timezone": pl.Utf8,
        },
    ).with_columns([pl.col("region_id").cast(pl.Int64)])

    # Set wider display options for Polars
    pl.Config.set_tbl_width_chars(120)

    # Dataset Overview
    console.print(create_section_header("Dataset Overview"))
    overview_table = Table(show_header=True, header_style="bold cyan")
    overview_table.add_column("Dataset")
    overview_table.add_column("Description")
    overview_table.add_row("Customers", "Customer information with region assignments")
    overview_table.add_row("Orders", "Customer order transactions")
    overview_table.add_row("Regions", "Lookup table of region details")
    console.print(overview_table)

    # Dataset Shapes
    console.print(create_section_header("Dataset Shapes"))
    shapes_table = Table(show_header=True, header_style="bold cyan")
    shapes_table.add_column("Dataset")
    shapes_table.add_column("Dimensions")
    shapes_table.add_row(
        "Customers", f"{customers.shape[0]} rows × {customers.shape[1]} columns"
    )
    shapes_table.add_row(
        "Orders", f"{orders.shape[0]} rows × {orders.shape[1]} columns"
    )
    shapes_table.add_row(
        "Regions", f"{regions.shape[0]} rows × {regions.shape[1]} columns"
    )
    console.print(shapes_table)

    # Sample Data
    console.print(create_section_header("Sample Data"))
    console.print("\n[bold cyan]Customers (first 3 rows):[/]")
    print(customers.head(3))
    console.print("\n[bold cyan]Orders (first 3 rows):[/]")
    print(orders.head(3))
    console.print("\n[bold cyan]Regions (all rows):[/]")
    print(regions)

    # Customers ↔ Orders Join Analysis
    title = Text()
    title.append("🔍 ", style="bold yellow")
    title.append("Analyzing Join Relationships", style="bold blue")
    title.append(" 🔍", style="bold yellow")

    subtitle = Text("\nCustomers ↔ Orders", style="bold cyan")

    console.print(
        Panel.fit(
            Text.assemble(title, "\n", subtitle), border_style="blue", padding=(1, 2)
        )
    )

    console.print(
        "[yellow]Expected:[/] [bold green]customer_id[/] should be the optimal join key"
    )
    customers.polars_utils.join_analysis(orders)

    # Customers ↔ Regions Join Analysis
    subtitle = Text("\nCustomers ↔ Regions", style="bold cyan")

    console.print(
        Panel.fit(
            Text.assemble(title, "\n", subtitle), border_style="blue", padding=(1, 2)
        )
    )

    console.print(
        "[yellow]Expected:[/] [bold green]region_id[/] should be the optimal join key"
    )
    customers.polars_utils.join_analysis(regions)

    # Detailed Analysis for Customers ↔ Orders
    results_orders = customers.polars_utils.analyze_joins(orders)

    console.print(create_section_header("Detailed Join Analysis - Customers ↔ Orders"))
    for match in results_orders[:3]:
        console.print(
            f"\n[bold cyan]Potential Join:[/] {match.left_column} = {match.right_column}"
        )
        console.print("[bold cyan]Match Statistics:[/]")
        console.print(
            f"  • Customers matching orders: [green]{match.left_match_percentage:.1f}%[/]"
        )
        console.print(
            f"  • Orders matching customers: [green]{match.right_match_percentage:.1f}%[/]"
        )
        console.print(f"  • Number of matching values: [green]{match.matched}[/]")

    # Join Demonstration - Customers ↔ Orders
    console.print(create_section_header("Demonstrating Customer Orders Join"))
    joined_orders = customers.join(
        orders, left_on="customer_id", right_on="customer_id", how="inner"
    )

    console.print("\n[bold cyan]Sample of joined order data (first 3 rows):[/]")
    print(
        joined_orders.select(
            [
                "customer_id",
                "first_name",
                "last_name",
                "order_id",
                "order_date",
                "amount",
            ]
        ).head(3)
    )

    # Order Coverage Analysis
    total_customers = customers.shape[0]
    customers_with_orders = joined_orders.select("customer_id").unique().shape[0]

    coverage_panel = Panel(
        f"""[bold cyan]Order Coverage Analysis[/]
Total customers: {total_customers}
Customers with orders: [green]{customers_with_orders}[/]
Coverage percentage: [green]{(customers_with_orders/total_customers)*100:.1f}%[/]""",
        border_style="blue",
    )
    console.print(coverage_panel)

    # Customer Order Distribution
    console.print(create_section_header("Orders per Customer"))
    order_distribution = (
        joined_orders.group_by(["customer_id", "first_name", "last_name"])
        .agg(pl.len().alias("order_count"))
        .sort("order_count", descending=True)
        .head(5)
    )
    print(order_distribution)


if __name__ == "__main__":
    main()
