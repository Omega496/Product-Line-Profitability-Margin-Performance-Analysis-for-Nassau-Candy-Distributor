"""
Analytics module for Nassau Candy Distributor.

Provides business intelligence and diagnostic metrics including:
1. Pareto Concentration Analysis (80/20 profit drivers).
2. Product Quadrant Segmentation (Stars, Traps, Niches, Drains).
3. Division and Factory Aggregations (Sales, Cost, Gross Profit, Gross Margin %).
"""

import sys
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd

# Ensure project root is in sys.path for robust imports
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.data_loader import load_and_clean_data


def calculate_pareto_concentration(
    df: pd.DataFrame, threshold: float = 80.0
) -> pd.DataFrame:
    """
    Perform Pareto Concentration (80/20 rule) analysis on product SKUs.

    Sorts products by total Gross Profit descending, calculates cumulative
    profit contribution percentage, and tags products making up the top threshold%.

    Parameters
    ----------
    df : pd.DataFrame
        Transaction DataFrame output from load_and_clean_data.
    threshold : float, default=80.0
        Cumulative percentage threshold to classify top contributors.

    Returns
    -------
    pd.DataFrame
        Product-level table sorted by Gross Profit descending with cumulative
        metrics and top contributor flags.
    """
    pareto_df = (
        df.groupby(["Product ID", "Product Name", "Division", "Factory"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Cost=("Cost", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Order_Count=("Order ID", "count"),
        )
    )

    # Compute row KPIs with safe division guards
    pareto_df["Gross Margin (%)"] = np.where(
        pareto_df["Sales"] > 0, (pareto_df["Gross_Profit"] / pareto_df["Sales"]) * 100, 0.0
    )
    pareto_df["Profit per Unit"] = np.where(
        pareto_df["Units"] > 0, pareto_df["Gross_Profit"] / pareto_df["Units"], 0.0
    )

    # Sort products by total Gross Profit descending
    pareto_df = pareto_df.sort_values(by="Gross_Profit", ascending=False).reset_index(drop=True)

    total_profit = pareto_df["Gross_Profit"].sum()
    pareto_df["Profit Share (%)"] = np.where(
        total_profit != 0, (pareto_df["Gross_Profit"] / total_profit) * 100, 0.0
    )
    pareto_df["Cumulative Profit (%)"] = pareto_df["Profit Share (%)"].cumsum()

    # Identify SKUs required to attain the top threshold%
    pareto_df[f"Top {int(threshold)}% (Pareto)"] = (
        pareto_df["Cumulative Profit (%)"].shift(1, fill_value=0) < threshold
    )

    return pareto_df


def segment_product_quadrants(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Segment products into 4 strategic quadrants using median sales and
    median gross margin:
    - Stars: High Sales, High Margin
    - Traps: High Sales, Low Margin
    - Niches: Low Sales, High Margin
    - Drains: Low Sales, Low Margin

    Parameters
    ----------
    df : pd.DataFrame
        Transaction DataFrame output from load_and_clean_data.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, float]]
        (quadrant_df, thresholds_dict) where thresholds_dict contains
        median sales and median gross margin.
    """
    prod_df = (
        df.groupby(["Product ID", "Product Name", "Division", "Factory"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Cost=("Cost", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
        )
    )
    prod_df["Gross Margin (%)"] = np.where(
        prod_df["Sales"] > 0, (prod_df["Gross_Profit"] / prod_df["Sales"]) * 100, 0.0
    )
    prod_df["Profit per Unit"] = np.where(
        prod_df["Units"] > 0, prod_df["Gross_Profit"] / prod_df["Units"], 0.0
    )

    median_sales = float(prod_df["Sales"].median()) if not prod_df.empty else 0.0
    median_margin = float(prod_df["Gross Margin (%)"].median()) if not prod_df.empty else 0.0

    def assign_category(row: pd.Series) -> str:
        high_sales = row["Sales"] >= median_sales
        high_margin = row["Gross Margin (%)"] >= median_margin
        if high_sales and high_margin:
            return "Stars (High Sales, High Margin)"
        elif high_sales and not high_margin:
            return "Traps (High Sales, Low Margin)"
        elif not high_sales and high_margin:
            return "Niches (Low Sales, High Margin)"
        else:
            return "Drains (Low Sales, Low Margin)"

    prod_df["Quadrant"] = prod_df.apply(assign_category, axis=1)
    prod_df["Sales Tier"] = prod_df["Sales"].apply(
        lambda x: "High Sales" if x >= median_sales else "Low Sales"
    )
    prod_df["Margin Tier"] = prod_df["Gross Margin (%)"].apply(
        lambda x: "High Margin" if x >= median_margin else "Low Margin"
    )

    thresholds = {
        "median_sales": median_sales,
        "median_gross_margin_pct": median_margin,
    }

    return prod_df, thresholds


def calculate_division_factory_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary table of Sales, Cost, Gross Profit, and Gross Margin %
    grouped by Division and Factory.

    Parameters
    ----------
    df : pd.DataFrame
        Transaction DataFrame output from load_and_clean_data.

    Returns
    -------
    pd.DataFrame
        Aggregated summary grouped by Division and Factory.
    """
    summary = (
        df.groupby(["Division", "Factory"], as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Cost=("Cost", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Order_Count=("Order ID", "count"),
        )
    )
    summary["Gross Margin (%)"] = np.where(
        summary["Sales"] > 0, (summary["Gross_Profit"] / summary["Sales"]) * 100, 0.0
    )
    return summary.sort_values(by=["Division", "Sales"], ascending=[True, False]).reset_index(drop=True)


def calculate_division_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary table of Sales, Cost, Gross Profit, and Gross Margin %
    grouped by Division.

    Parameters
    ----------
    df : pd.DataFrame
        Transaction DataFrame output from load_and_clean_data.

    Returns
    -------
    pd.DataFrame
        Aggregated summary grouped by Division.
    """
    summary = (
        df.groupby("Division", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Cost=("Cost", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Order_Count=("Order ID", "count"),
        )
    )
    tot_sales = summary["Sales"].sum()
    tot_profit = summary["Gross_Profit"].sum()
    summary["Gross Margin (%)"] = np.where(
        summary["Sales"] > 0, (summary["Gross_Profit"] / summary["Sales"]) * 100, 0.0
    )
    summary["Revenue Share (%)"] = np.where(
        tot_sales > 0, (summary["Sales"] / tot_sales) * 100, 0.0
    )
    summary["Profit Share (%)"] = np.where(
        tot_profit != 0, (summary["Gross_Profit"] / tot_profit) * 100, 0.0
    )
    return summary.sort_values(by="Gross_Profit", ascending=False).reset_index(drop=True)


def calculate_factory_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary table of Sales, Cost, Gross Profit, and Gross Margin %
    grouped by Factory.

    Parameters
    ----------
    df : pd.DataFrame
        Transaction DataFrame output from load_and_clean_data.

    Returns
    -------
    pd.DataFrame
        Aggregated summary grouped by Factory.
    """
    summary = (
        df.groupby("Factory", as_index=False)
        .agg(
            Sales=("Sales", "sum"),
            Cost=("Cost", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Units=("Units", "sum"),
            Order_Count=("Order ID", "count"),
        )
    )
    tot_sales = summary["Sales"].sum()
    tot_profit = summary["Gross_Profit"].sum()
    summary["Gross Margin (%)"] = np.where(
        summary["Sales"] > 0, (summary["Gross_Profit"] / summary["Sales"]) * 100, 0.0
    )
    summary["Revenue Share (%)"] = np.where(
        tot_sales > 0, (summary["Sales"] / tot_sales) * 100, 0.0
    )
    summary["Profit Share (%)"] = np.where(
        tot_profit != 0, (summary["Gross_Profit"] / tot_profit) * 100, 0.0
    )
    return summary.sort_values(by="Gross_Profit", ascending=False).reset_index(drop=True)


def calculate_margin_volatility(
    df: pd.DataFrame, freq: str = "ME"
) -> pd.DataFrame:
    """
    Calculate margin volatility (variability of gross margin over time)
    grouped by Division and Product across specified time frequency.

    Parameters
    ----------
    df : pd.DataFrame
        Transaction DataFrame with Order Date, Sales, Cost, and Gross Profit.
    freq : str, default="ME"
        Time aggregation frequency (e.g., 'ME' for month-end).

    Returns
    -------
    pd.DataFrame
        Table summarizing mean margin, standard deviation (volatility),
        and active periods per product line.
    """
    monthly = (
        df.groupby(["Division", "Product Name", pd.Grouper(key="Order Date", freq=freq)])
        .agg(Sales=("Sales", "sum"), Gross_Profit=("Gross Profit", "sum"))
        .reset_index()
    )
    monthly["Gross Margin (%)"] = np.where(
        monthly["Sales"] > 0, (monthly["Gross_Profit"] / monthly["Sales"]) * 100, 0.0
    )
    vol = (
        monthly.groupby(["Division", "Product Name"])["Gross Margin (%)"]
        .agg(Mean_Margin="mean", Margin_Std="std", Active_Periods="count")
        .reset_index()
    )
    vol["Margin_Std"] = vol["Margin_Std"].fillna(0.0)
    return vol.sort_values(by="Margin_Std", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    print("Loading Nassau Candy Distributor transactions...")
    df = load_and_clean_data()

    # 1. Pareto Concentration
    pareto_df = calculate_pareto_concentration(df, threshold=80.0)

    print("\n" + "=" * 80)
    print("TOP 5 PROFIT-DRIVING SKUS (PARETO CONCENTRATION):")
    print("=" * 80)
    top_5 = pareto_df.head(5)[
        [
            "Product Name",
            "Division",
            "Sales",
            "Gross_Profit",
            "Gross Margin (%)",
            "Profit Share (%)",
            "Cumulative Profit (%)",
            "Top 80% (Pareto)",
        ]
    ]
    # Format nicely for console output
    formatted_top_5 = top_5.copy()
    formatted_top_5["Sales"] = formatted_top_5["Sales"].map("${:,.2f}".format)
    formatted_top_5["Gross_Profit"] = formatted_top_5["Gross_Profit"].map("${:,.2f}".format)
    formatted_top_5["Gross Margin (%)"] = formatted_top_5["Gross Margin (%)"].map("{:.2f}%".format)
    formatted_top_5["Profit Share (%)"] = formatted_top_5["Profit Share (%)"].map("{:.2f}%".format)
    formatted_top_5["Cumulative Profit (%)"] = formatted_top_5["Cumulative Profit (%)"].map("{:.2f}%".format)
    print(formatted_top_5.to_string(index=False))

    # 2. Division Summary
    div_summary = calculate_division_summary(df)
    print("\n" + "=" * 80)
    print("DIVISION PERFORMANCE SUMMARY:")
    print("=" * 80)
    formatted_div = div_summary.copy()
    formatted_div["Sales"] = formatted_div["Sales"].map("${:,.2f}".format)
    formatted_div["Cost"] = formatted_div["Cost"].map("${:,.2f}".format)
    formatted_div["Gross_Profit"] = formatted_div["Gross_Profit"].map("${:,.2f}".format)
    formatted_div["Gross Margin (%)"] = formatted_div["Gross Margin (%)"].map("{:.2f}%".format)
    formatted_div["Revenue Share (%)"] = formatted_div["Revenue Share (%)"].map("{:.2f}%".format)
    formatted_div["Profit Share (%)"] = formatted_div["Profit Share (%)"].map("{:.2f}%".format)
    print(formatted_div.to_string(index=False))

    # 3. Division & Factory Aggregations
    div_factory_summary = calculate_division_factory_summary(df)
    print("\n" + "=" * 80)
    print("DIVISION & FACTORY AGGREGATIONS:")
    print("=" * 80)
    formatted_df_fact = div_factory_summary.copy()
    formatted_df_fact["Sales"] = formatted_df_fact["Sales"].map("${:,.2f}".format)
    formatted_df_fact["Cost"] = formatted_df_fact["Cost"].map("${:,.2f}".format)
    formatted_df_fact["Gross_Profit"] = formatted_df_fact["Gross_Profit"].map("${:,.2f}".format)
    formatted_df_fact["Gross Margin (%)"] = formatted_df_fact["Gross Margin (%)"].map("{:.2f}%".format)
    print(formatted_df_fact.to_string(index=False))

    # 4. Product Quadrants
    quad_df, thresholds = segment_product_quadrants(df)
    print("\n" + "=" * 80)
    print(f"PRODUCT QUADRANT SEGMENTATION (Median Sales: ${thresholds['median_sales']:,.2f}, Median Margin: {thresholds['median_gross_margin_pct']:.2f}%):")
    print("=" * 80)
    quad_summary = (
        quad_df.groupby("Quadrant")
        .agg(
            Product_Count=("Product Name", "count"),
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Gross_Profit", "sum"),
        )
        .reset_index()
    )
    quad_summary["Total_Sales"] = quad_summary["Total_Sales"].map("${:,.2f}".format)
    quad_summary["Total_Profit"] = quad_summary["Total_Profit"].map("${:,.2f}".format)
    print(quad_summary.to_string(index=False))

    # 5. Margin Volatility
    vol_df = calculate_margin_volatility(df)
    print("\n" + "=" * 80)
    print("MARGIN VOLATILITY (VARIABILITY OF MARGIN OVER TIME):")
    print("=" * 80)
    formatted_vol = vol_df.copy()
    formatted_vol["Mean_Margin"] = formatted_vol["Mean_Margin"].map("{:.2f}%".format)
    formatted_vol["Margin_Std"] = formatted_vol["Margin_Std"].map("{:.4f}".format)
    print(formatted_vol.head(10).to_string(index=False))

