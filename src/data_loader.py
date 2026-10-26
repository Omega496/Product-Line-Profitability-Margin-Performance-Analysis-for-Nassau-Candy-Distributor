"""
Data loading and preprocessing module for Nassau Candy Distributor.

Loads transaction data, cleans and standardizes records, merges with
product-factory mapping and factory coordinates, and computes financial KPIs.
"""

from pathlib import Path
from typing import Union
import numpy as np
import pandas as pd


def load_and_clean_data(
    sales_file: Union[str, Path] = "Nassau Candy Distributor.csv",
    mapping_file: Union[str, Path] = "data/product_factory_mapping.csv",
    coords_file: Union[str, Path] = "data/factory_coordinates.csv",
    export_cleaned: bool = True,
    cleaned_output: Union[str, Path] = "data/cleaned_transactions.csv",
) -> pd.DataFrame:
    """
    Load raw transaction sales data, product-to-factory mapping, and factory
    coordinates, perform data validation and cleaning, merge the reference
    tables, and compute key performance indicators (KPIs) per transaction.

    Parameters
    ----------
    sales_file : Union[str, Path]
        Path to the Nassau Candy Distributor transaction CSV.
    mapping_file : Union[str, Path]
        Path to the product-to-factory mapping CSV.
    coords_file : Union[str, Path]
        Path to the factory coordinates CSV.

    Returns
    -------
    pd.DataFrame
        Cleaned, merged, and KPI-enriched transaction DataFrame.
    """
    sales_path = Path(sales_file)
    mapping_path = Path(mapping_file)
    coords_path = Path(coords_file)

    # Support relative paths whether run from repo root or src/
    project_root = Path(__file__).resolve().parent.parent
    if not sales_path.exists() and (project_root / sales_path).exists():
        sales_path = project_root / sales_path
    if not mapping_path.exists() and (project_root / mapping_path).exists():
        mapping_path = project_root / mapping_path
    if not coords_path.exists() and (project_root / coords_path).exists():
        coords_path = project_root / coords_path

    # Read datasets
    sales_df = pd.read_csv(sales_path)
    mapping_df = pd.read_csv(mapping_path)
    coords_df = pd.read_csv(coords_path)

    # Trim leading/trailing whitespace across object columns
    for df in [sales_df, mapping_df, coords_df]:
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].astype(str).str.strip()

    # Parse Order Date and Ship Date (format: DD-MM-YYYY)
    sales_df["Order Date"] = pd.to_datetime(
        sales_df["Order Date"], format="%d-%m-%Y", errors="coerce"
    )
    sales_df["Ship Date"] = pd.to_datetime(
        sales_df["Ship Date"], format="%d-%m-%Y", errors="coerce"
    )

    # Filter out records with invalid dates
    sales_df = sales_df.dropna(subset=["Order Date", "Ship Date"]).copy()

    # Enforce numeric types
    for col in ["Sales", "Cost", "Units", "Gross Profit"]:
        if col in sales_df.columns:
            sales_df[col] = pd.to_numeric(sales_df[col], errors="coerce")

    # Filter out rows with zero or missing sales, cost, or units
    valid_mask = (
        sales_df["Sales"].notna()
        & (sales_df["Sales"] > 0)
        & sales_df["Cost"].notna()
        & (sales_df["Cost"] > 0)
        & sales_df["Units"].notna()
        & (sales_df["Units"] > 0)
    )
    sales_df = sales_df[valid_mask].copy()

    # Standardize product and division labels
    # Fizzy Lifting Drinks (Product ID OTH-FIZ-56000) belongs to 'Other' division
    sales_df.loc[sales_df["Product Name"] == "Fizzy Lifting Drinks", "Division"] = "Other"

    # Merge transaction records with product-factory mapping
    merged = sales_df.merge(
        mapping_df, on=["Product Name", "Division"], how="left"
    )

    # Fallback to map Factory by Product Name if any row remains unmapped
    if merged["Factory"].isna().any():
        prod_factory_map = mapping_df.set_index("Product Name")["Factory"].to_dict()
        merged["Factory"] = merged["Factory"].fillna(
            merged["Product Name"].map(prod_factory_map)
        )

    # Merge with factory coordinates on Factory
    merged = merged.merge(coords_df, on="Factory", how="left")

    # Ensure Gross Profit consistency
    if "Gross Profit" not in merged.columns or merged["Gross Profit"].isna().any():
        merged["Gross Profit"] = merged["Sales"] - merged["Cost"]

    # Compute row-level KPIs with safe division guards
    # Gross Margin (%) = (Gross Profit / Sales) * 100
    merged["Gross Margin (%)"] = np.where(
        merged["Sales"] > 0, (merged["Gross Profit"] / merged["Sales"]) * 100, 0.0
    )

    # Profit per Unit = Gross Profit / Units
    merged["Profit per Unit"] = np.where(
        merged["Units"] > 0, merged["Gross Profit"] / merged["Units"], 0.0
    )

    # Export cleaned dataset artifact to data/
    if export_cleaned:
        out_path = Path(cleaned_output)
        if not out_path.is_absolute():
            out_path = project_root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        merged.to_csv(out_path, index=False)

    return merged


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    sales_file = base_dir / "Nassau Candy Distributor.csv"
    mapping_file = base_dir / "data" / "product_factory_mapping.csv"
    coords_file = base_dir / "data" / "factory_coordinates.csv"

    print("Loading and cleaning Nassau Candy Distributor dataset...")
    df = load_and_clean_data(sales_file, mapping_file, coords_file)

    print("\n" + "=" * 65)
    print("DATASET INFO:")
    print("=" * 65)
    df.info()

    total_revenue = df["Sales"].sum()
    total_gross_profit = df["Gross Profit"].sum()
    portfolio_gross_margin = (total_gross_profit / total_revenue) * 100

    print("\n" + "=" * 65)
    print("PORTFOLIO FINANCIAL SUMMARY:")
    print("=" * 65)
    print(f"Total Revenue:              ${total_revenue:,.2f}")
    print(f"Total Gross Profit:         ${total_gross_profit:,.2f}")
    print(f"Portfolio Gross Margin (%): {portfolio_gross_margin:.2f}%")

    print("\n" + "=" * 65)
    print("MISSING VALUES CHECK:")
    print("=" * 65)
    missing = df.isnull().sum()
    print(missing)
    if missing.sum() == 0:
        print("\n[SUCCESS] 0 missing values found across all columns.")
    else:
        print(f"\n[WARNING] Found {missing.sum()} missing values.")
