"""
Streamlit Web Application: Product Line Profitability & Margin Performance Analysis
for Nassau Candy Distributor.

Interactive business intelligence dashboard providing:
- Top-level financial KPI cards
- Product profitability leaderboard, contribution analysis, and quadrant segmentation
- Division performance and margin distribution analytics
- Cost vs Margin diagnostics and low-margin threshold flagging
- Pareto concentration curve (80/20 profit driver analysis)
"""

import sys
from pathlib import Path
from typing import Tuple
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Configure wide layout and page metadata
st.set_page_config(
    page_title="Nassau Candy Profitability Analysis",
    page_icon=":material/candlestick_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure project root is accessible for module imports
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_and_clean_data
from src.analytics import (
    calculate_pareto_concentration,
    segment_product_quadrants,
    calculate_division_summary,
    calculate_division_factory_summary,
)


@st.cache_data(ttl="1h", max_entries=5)
def get_cached_data() -> pd.DataFrame:
    """Load and preprocess dataset with Streamlit caching."""
    sales_csv = PROJECT_ROOT / "Nassau Candy Distributor.csv"
    mapping_csv = PROJECT_ROOT / "data" / "product_factory_mapping.csv"
    coords_csv = PROJECT_ROOT / "data" / "factory_coordinates.csv"
    return load_and_clean_data(sales_csv, mapping_csv, coords_csv)


def main():
    # Load cached dataset
    raw_df = get_cached_data()

    # -------------------------------------------------------------
    # SIDEBAR CONTROLS
    # -------------------------------------------------------------
    with st.sidebar:
        st.image(
            "https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?w=300&auto=format&fit=crop&q=80",
            width="stretch",
            alt="Assorted colorful candies and confections",
        )
        st.header("Control panel", divider=True)

        # 1. Division filter multiselect
        all_divisions = sorted(raw_df["Division"].dropna().unique().tolist())
        selected_divisions = st.multiselect(
            "Filter by division",
            options=all_divisions,
            default=all_divisions,
            help="Select one or more product divisions to evaluate.",
        )

        # 2. Date range selector (Order Date)
        min_order_date = raw_df["Order Date"].min().date()
        max_order_date = raw_df["Order Date"].max().date()

        selected_date_range = st.date_input(
            "Order date range",
            value=(min_order_date, max_order_date),
            min_value=min_order_date,
            max_value=max_order_date,
            help="Filter orders by customer purchase date.",
        )

        # 3. Gross Margin threshold slider
        margin_threshold = st.slider(
            "Gross margin threshold (%)",
            min_value=0,
            max_value=100,
            value=60,
            step=1,
            help="Flag and isolate products with gross margin below this threshold.",
        )

        st.divider()
        st.caption(
            "**Nassau Candy Analytics**  \n"
            "Evaluates profit concentration, high-volume / low-margin risk SKUs, "
            "and operational profitability across divisions and production facilities."
        )

    # -------------------------------------------------------------
    # FILTER DATASET
    # -------------------------------------------------------------
    filtered_df = raw_df.copy()

    # Apply division filter
    if selected_divisions:
        filtered_df = filtered_df[filtered_df["Division"].isin(selected_divisions)]
    else:
        st.warning(
            "Please select at least one division to display dashboard analytics.",
            title="No division selected",
            icon=":material/warning:",
        )
        st.stop()

    # Apply date range filter
    if isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 2:
        start_date, end_date = selected_date_range
        filtered_df = filtered_df[
            (filtered_df["Order Date"].dt.date >= start_date)
            & (filtered_df["Order Date"].dt.date <= end_date)
        ]
    elif isinstance(selected_date_range, (list, tuple)) and len(selected_date_range) == 1:
        start_date = selected_date_range[0]
        filtered_df = filtered_df[filtered_df["Order Date"].dt.date >= start_date]

    if filtered_df.empty:
        st.error(
            "No data matches the selected filters. Please expand your date or division selection.",
            title="No records found",
            icon=":material/error:",
        )
        st.stop()

    # -------------------------------------------------------------
    # HEADER & TOP-LEVEL METRIC CARDS
    # -------------------------------------------------------------
    st.title("Nassau Candy distributor: Product line profitability & margin performance")
    st.caption(
        "Executive analytics dashboard | Profit concentration, strategic quadrants, and cost diagnostics"
    )

    # Top-Level KPIs
    tot_revenue = float(filtered_df["Sales"].sum())
    tot_profit = float(filtered_df["Gross Profit"].sum())
    overall_margin = (tot_profit / tot_revenue * 100) if tot_revenue > 0 else 0.0
    tot_units = int(filtered_df["Units"].sum())

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total revenue", f"${tot_revenue:,.2f}", border=True, height="stretch")
    kpi2.metric("Total gross profit", f"${tot_profit:,.2f}", border=True, height="stretch")
    kpi3.metric("Portfolio gross margin", f"{overall_margin:.2f}%", border=True, height="stretch")
    kpi4.metric("Total units sold", f"{tot_units:,}", border=True, height="stretch")

    st.divider()

    # -------------------------------------------------------------
    # 4 TABBED DASHBOARD MODULES
    # -------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            ":material/leaderboard: Product profitability overview",
            ":material/domain: Division performance dashboard",
            ":material/troubleshoot: Cost vs margin diagnostics",
            ":material/pie_chart: Profit concentration analysis",
        ]
    )

    # =============================================================
    # TAB 1: Product Profitability Overview
    # =============================================================
    with tab1:
        st.subheader("Product margin leaderboard")
        st.caption(
            "Comprehensive product-level financial performance. Flagged rows denote SKUs below the margin threshold."
        )

        # Aggregate product metrics
        prod_table = (
            filtered_df.groupby(["Product Name", "Division", "Factory"], as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Cost=("Cost", "sum"),
                Gross_Profit=("Gross Profit", "sum"),
                Units=("Units", "sum"),
            )
        )
        prod_table["Gross Margin (%)"] = np.where(
            prod_table["Sales"] > 0, (prod_table["Gross_Profit"] / prod_table["Sales"]) * 100, 0.0
        )
        prod_table["Profit per Unit"] = np.where(
            prod_table["Units"] > 0, prod_table["Gross_Profit"] / prod_table["Units"], 0.0
        )
        prod_table["Revenue Contribution (%)"] = np.where(
            tot_revenue > 0, (prod_table["Sales"] / tot_revenue) * 100, 0.0
        )
        prod_table["Profit Contribution (%)"] = np.where(
            tot_profit != 0, (prod_table["Gross_Profit"] / tot_profit) * 100, 0.0
        )

        # Sort by Gross Profit descending
        prod_table = prod_table.sort_values(by="Gross_Profit", ascending=False).reset_index(drop=True)

        # Status badge column
        prod_table["Status"] = prod_table["Gross Margin (%)"].apply(
            lambda x: f"⚠️ Alert (< {margin_threshold}%)" if x < margin_threshold else "✅ Healthy"
        )

        st.dataframe(
            prod_table[
                [
                    "Product Name",
                    "Division",
                    "Factory",
                    "Sales",
                    "Cost",
                    "Gross_Profit",
                    "Gross Margin (%)",
                    "Profit per Unit",
                    "Profit Contribution (%)",
                    "Revenue Contribution (%)",
                    "Status",
                ]
            ],
            column_config={
                "Product Name": st.column_config.TextColumn("Product name"),
                "Division": st.column_config.TextColumn("Division"),
                "Factory": st.column_config.TextColumn("Factory"),
                "Sales": st.column_config.NumberColumn("Sales", format="$%.2f"),
                "Cost": st.column_config.NumberColumn("Cost", format="$%.2f"),
                "Gross_Profit": st.column_config.NumberColumn("Gross profit", format="$%.2f"),
                "Gross Margin (%)": st.column_config.NumberColumn("Gross margin", format="%.2f%%"),
                "Profit per Unit": st.column_config.NumberColumn("Profit / unit", format="$%.2f"),
                "Profit Contribution (%)": st.column_config.NumberColumn("Profit share", format="%.2f%%"),
                "Revenue Contribution (%)": st.column_config.NumberColumn("Revenue share", format="%.2f%%"),
                "Status": st.column_config.TextColumn("Threshold status"),
            },
            hide_index=True,
            width="stretch",
            height=320,
            alt="Product margin leaderboard sorted by total gross profit",
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Profit vs revenue contribution (%)")
            st.caption(
                "Comparison of each product's share of company revenue versus its share of gross profit."
            )

            fig_contrib = go.Figure()
            fig_contrib.add_trace(
                go.Bar(
                    name="Profit Contribution (%)",
                    x=prod_table["Product Name"],
                    y=prod_table["Profit Contribution (%)"],
                    marker_color="#10B981",
                    hovertemplate="<b>%{x}</b><br>Profit Contribution: %{y:.2f}%<extra></extra>",
                )
            )
            fig_contrib.add_trace(
                go.Bar(
                    name="Revenue Contribution (%)",
                    x=prod_table["Product Name"],
                    y=prod_table["Revenue Contribution (%)"],
                    marker_color="#3B82F6",
                    hovertemplate="<b>%{x}</b><br>Revenue Contribution: %{y:.2f}%<extra></extra>",
                )
            )
            fig_contrib.update_layout(
                barmode="group",
                template="plotly_white",
                height=450,
                xaxis_tickangle=-45,
                xaxis_title="Product Name",
                yaxis_title="Contribution (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=40, r=40, t=50, b=120),
            )
            st.plotly_chart(
                fig_contrib,
                width="stretch",
                alt="Bar chart comparing profit contribution percentage versus revenue contribution percentage per product",
            )

        with col2:
            st.subheader("Strategic product quadrant analysis")
            st.caption(
                "Segmenting SKUs using median sales and median gross margin into Stars, Traps, Niches, and Drains."
            )

            quad_df, thresholds = segment_product_quadrants(filtered_df)
            med_s = thresholds["median_sales"]
            med_m = thresholds["median_gross_margin_pct"]

            quad_colors = {
                "Stars (High Sales, High Margin)": "#10B981",
                "Traps (High Sales, Low Margin)": "#F59E0B",
                "Niches (Low Sales, High Margin)": "#6366F1",
                "Drains (Low Sales, Low Margin)": "#EF4444",
            }

            fig_quad = px.scatter(
                quad_df,
                x="Sales",
                y="Gross Margin (%)",
                color="Quadrant",
                color_discrete_map=quad_colors,
                size="Units",
                hover_name="Product Name",
                hover_data={
                    "Division": True,
                    "Factory": True,
                    "Sales": ":$,.2f",
                    "Gross_Profit": ":$,.2f",
                    "Gross Margin (%)": ":.2f%",
                    "Profit per Unit": ":$,.2f",
                    "Units": True,
                },
                template="plotly_white",
                height=450,
            )

            fig_quad.add_vline(
                x=med_s,
                line_dash="dash",
                line_color="#94a3b8",
                annotation_text=f"Median Sales (${med_s:,.0f})",
                annotation_position="top left",
            )
            fig_quad.add_hline(
                y=med_m,
                line_dash="dash",
                line_color="#94a3b8",
                annotation_text=f"Median Margin ({med_m:.1f}%)",
                annotation_position="bottom right",
            )

            fig_quad.update_layout(
                xaxis_title="Total Sales ($)",
                yaxis_title="Gross Margin (%)",
                legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
                margin=dict(l=40, r=40, t=30, b=80),
            )
            st.plotly_chart(
                fig_quad,
                width="stretch",
                alt="Scatter plot of sales versus gross margin percentage segmenting products into four quadrants",
            )

    # =============================================================
    # TAB 2: Division Performance Dashboard
    # =============================================================
    with tab2:
        st.subheader("Division financial performance")
        st.caption(
            "Evaluating revenue versus profit imbalance and structural margin variations across business units."
        )

        div_summary = calculate_division_summary(filtered_df)

        # Overview cards per division
        if len(div_summary) > 0:
            div_cols = st.columns(len(div_summary))
            for idx, row in div_summary.iterrows():
                with div_cols[idx]:
                    st.metric(
                        f"{row['Division']} division",
                        f"${row['Gross_Profit']:,.2f}",
                        delta=f"{row['Gross Margin (%)']:.2f}% margin",
                        border=True,
                        height="stretch",
                        help=f"Revenue: ${row['Sales']:,.2f} | Units: {row['Units']:,}",
                    )

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.subheader("Revenue vs gross profit by division")
            fig_div = go.Figure()
            fig_div.add_trace(
                go.Bar(
                    x=div_summary["Division"],
                    y=div_summary["Sales"],
                    name="Total Revenue ($)",
                    marker_color="#2563EB",
                    text=div_summary["Sales"].apply(lambda x: f"${x:,.0f}"),
                    textposition="auto",
                )
            )
            fig_div.add_trace(
                go.Bar(
                    x=div_summary["Division"],
                    y=div_summary["Gross_Profit"],
                    name="Gross Profit ($)",
                    marker_color="#10B981",
                    text=div_summary["Gross_Profit"].apply(lambda x: f"${x:,.0f}"),
                    textposition="auto",
                )
            )
            fig_div.update_layout(
                barmode="group",
                template="plotly_white",
                height=420,
                xaxis_title="Division",
                yaxis_title="Amount ($)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=40, r=40, t=50, b=40),
            )
            st.plotly_chart(
                fig_div,
                width="stretch",
                alt="Grouped bar chart comparing total revenue versus gross profit across divisions",
            )

        with col_d2:
            st.subheader("Gross margin (%) distribution by division")
            fig_box = px.box(
                filtered_df,
                x="Division",
                y="Gross Margin (%)",
                color="Division",
                points="outliers",
                color_discrete_sequence=["#2563EB", "#10B981", "#F59E0B"],
                template="plotly_white",
                height=420,
            )
            fig_box.update_layout(
                xaxis_title="Division",
                yaxis_title="Transaction Gross Margin (%)",
                showlegend=False,
                margin=dict(l=40, r=40, t=50, b=40),
            )
            st.plotly_chart(
                fig_box,
                width="stretch",
                alt="Box plot showing gross margin percentage distribution across divisions",
            )

        # Division & Factory Aggregations Table
        st.subheader("Division and manufacturing facility breakdown")
        div_fact_df = calculate_division_factory_summary(filtered_df)
        st.dataframe(
            div_fact_df,
            column_config={
                "Division": st.column_config.TextColumn("Division"),
                "Factory": st.column_config.TextColumn("Manufacturing facility"),
                "Sales": st.column_config.NumberColumn("Sales", format="$%.2f"),
                "Cost": st.column_config.NumberColumn("Cost", format="$%.2f"),
                "Gross_Profit": st.column_config.NumberColumn("Gross profit", format="$%.2f"),
                "Units": st.column_config.NumberColumn("Units", format="%,d"),
                "Order_Count": st.column_config.NumberColumn("Orders", format="%,d"),
                "Gross Margin (%)": st.column_config.NumberColumn("Gross margin", format="%.2f%%"),
            },
            hide_index=True,
            width="stretch",
            alt="Division and manufacturing facility aggregation summary",
        )

    # =============================================================
    # TAB 3: Cost vs Margin Diagnostics
    # =============================================================
    with tab3:
        st.subheader("Cost structure diagnostics")
        st.caption(
            f"Identify cost-heavy and margin-diluting products. The active threshold is set to {margin_threshold}%."
        )

        col_c1, col_c2 = st.columns([3, 2])

        with col_c1:
            st.subheader("Cost vs sales scatter plot")
            prod_diag = (
                filtered_df.groupby(["Product Name", "Division", "Factory"], as_index=False)
                .agg(
                    Sales=("Sales", "sum"),
                    Cost=("Cost", "sum"),
                    Gross_Profit=("Gross Profit", "sum"),
                    Units=("Units", "sum"),
                )
            )
            prod_diag["Gross Margin (%)"] = np.where(
                prod_diag["Sales"] > 0, (prod_diag["Gross_Profit"] / prod_diag["Sales"]) * 100, 0.0
            )
            prod_diag["Cost Ratio (%)"] = np.where(
                prod_diag["Sales"] > 0, (prod_diag["Cost"] / prod_diag["Sales"]) * 100, 0.0
            )

            max_val = max(prod_diag["Sales"].max(), prod_diag["Cost"].max()) * 1.05 if not prod_diag.empty else 100.0

            fig_cost = px.scatter(
                prod_diag,
                x="Cost",
                y="Sales",
                color="Gross Margin (%)",
                size="Units",
                hover_name="Product Name",
                hover_data={
                    "Division": True,
                    "Factory": True,
                    "Sales": ":$,.2f",
                    "Cost": ":$,.2f",
                    "Gross Margin (%)": ":.2f%",
                    "Cost Ratio (%)": ":.2f%",
                },
                color_continuous_scale="RdYlGn",
                range_color=[0, 100],
                template="plotly_white",
                height=480,
            )

            # Break-even line: y = x (Sales = Cost, 0% margin)
            fig_cost.add_shape(
                type="line",
                x0=0,
                y0=0,
                x1=max_val,
                y1=max_val,
                line=dict(color="#DC2626", dash="dot", width=2),
            )
            fig_cost.add_annotation(
                x=max_val * 0.7,
                y=max_val * 0.7,
                text="Zero Profit Line (Sales = Cost)",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#DC2626",
                font=dict(color="#DC2626", size=11),
            )

            fig_cost.update_layout(
                xaxis_title="Total Manufacturing Cost ($)",
                yaxis_title="Total Sales ($)",
                coloraxis_colorbar=dict(title="Margin (%)"),
                margin=dict(l=40, r=40, t=30, b=40),
            )
            st.plotly_chart(
                fig_cost,
                width="stretch",
                alt="Scatter plot of manufacturing cost versus sales color-coded by gross margin percentage",
            )

        with col_c2:
            st.subheader(f"Flagged SKUs (< {margin_threshold}% margin)")
            flagged_skus = prod_diag[prod_diag["Gross Margin (%)"] < margin_threshold].sort_values(
                by="Gross Margin (%)", ascending=True
            )

            if not flagged_skus.empty:
                st.error(
                    f"{len(flagged_skus)} product(s) fail to meet the {margin_threshold}% gross margin threshold.",
                    title="Low-margin alert",
                    icon=":material/warning:",
                )
                st.dataframe(
                    flagged_skus[
                        ["Product Name", "Division", "Gross Margin (%)", "Cost Ratio (%)", "Sales", "Cost"]
                    ],
                    column_config={
                        "Product Name": st.column_config.TextColumn("Product name"),
                        "Division": st.column_config.TextColumn("Division"),
                        "Gross Margin (%)": st.column_config.NumberColumn("Gross margin", format="%.2f%%"),
                        "Cost Ratio (%)": st.column_config.NumberColumn("Cost ratio", format="%.2f%%"),
                        "Sales": st.column_config.NumberColumn("Sales", format="$%.2f"),
                        "Cost": st.column_config.NumberColumn("Cost", format="$%.2f"),
                    },
                    hide_index=True,
                    width="stretch",
                    height=350,
                    alt=f"Products with gross margin below {margin_threshold}%",
                )
            else:
                st.success(
                    f"All products in the selected view achieve at least {margin_threshold}% gross margin.",
                    title="Healthy portfolio",
                    icon=":material/check_circle:",
                )

    # =============================================================
    # TAB 4: Profit Concentration Analysis
    # =============================================================
    with tab4:
        st.subheader("Pareto profit concentration (80/20 rule)")
        st.caption(
            "Evaluate portfolio dependency on top products and recognize profit concentration risk."
        )

        pareto_data = calculate_pareto_concentration(filtered_df, threshold=80.0)
        top_80_skus = pareto_data[pareto_data["Top 80% (Pareto)"]]
        total_skus = len(pareto_data)
        top_80_count = len(top_80_skus)
        top_80_pct = (top_80_count / total_skus * 100) if total_skus > 0 else 0
        actual_profit_share = top_80_skus["Profit Share (%)"].sum()

        st.info(
            f"{top_80_count} of {total_skus} SKUs ({top_80_pct:.1f}% of catalog) account for "
            f"{actual_profit_share:.2f}% of company gross profit.",
            title="Pareto insight",
            icon=":material/pie_chart:",
        )

        # Plotly Pareto Chart (Bar on primary Y, Line on secondary Y)
        fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])

        fig_pareto.add_trace(
            go.Bar(
                x=pareto_data["Product Name"],
                y=pareto_data["Gross_Profit"],
                name="Gross Profit ($)",
                marker_color="#3B82F6",
                hovertemplate="<b>%{x}</b><br>Gross Profit: $%{y:,.2f}<extra></extra>",
            ),
            secondary_y=False,
        )

        fig_pareto.add_trace(
            go.Scatter(
                x=pareto_data["Product Name"],
                y=pareto_data["Cumulative Profit (%)"],
                name="Cumulative Profit (%)",
                mode="lines+markers",
                line=dict(color="#EF4444", width=3),
                marker=dict(size=8, color="#DC2626"),
                hovertemplate="<b>%{x}</b><br>Cumulative Profit: %{y:.2f}%<extra></extra>",
            ),
            secondary_y=True,
        )

        fig_pareto.add_hline(
            y=80,
            line_dash="dash",
            line_color="#DC2626",
            line_width=2,
            secondary_y=True,
            annotation_text="80% Profit Benchmark",
            annotation_position="top left",
            annotation_font=dict(color="#DC2626", size=12),
        )

        fig_pareto.update_layout(
            template="plotly_white",
            height=480,
            xaxis_tickangle=-45,
            xaxis_title="Product Name",
            yaxis_title="Gross Profit ($)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=50, r=50, t=50, b=120),
        )
        fig_pareto.update_yaxes(title_text="Gross Profit ($)", secondary_y=False)
        fig_pareto.update_yaxes(title_text="Cumulative Profit (%)", range=[0, 105], secondary_y=True)

        st.plotly_chart(
            fig_pareto,
            width="stretch",
            alt="Dual-axis Pareto chart showing descending product gross profit and cumulative profit percentage",
        )

        # Top 80% Contributors Table
        st.subheader("Primary profit generators (top 80% cutoff)")
        st.dataframe(
            top_80_skus[
                [
                    "Product Name",
                    "Division",
                    "Factory",
                    "Sales",
                    "Gross_Profit",
                    "Gross Margin (%)",
                    "Profit Share (%)",
                    "Cumulative Profit (%)",
                ]
            ],
            column_config={
                "Product Name": st.column_config.TextColumn("Product name"),
                "Division": st.column_config.TextColumn("Division"),
                "Factory": st.column_config.TextColumn("Factory"),
                "Sales": st.column_config.NumberColumn("Sales", format="$%.2f"),
                "Gross_Profit": st.column_config.NumberColumn("Gross profit", format="$%.2f"),
                "Gross Margin (%)": st.column_config.NumberColumn("Gross margin", format="%.2f%%"),
                "Profit Share (%)": st.column_config.NumberColumn("Profit share", format="%.2f%%"),
                "Cumulative Profit (%)": st.column_config.NumberColumn("Cumulative profit", format="%.2f%%"),
            },
            hide_index=True,
            width="stretch",
            alt="Primary profit generating SKUs making up the top 80% cutoff",
        )


if __name__ == "__main__":
    main()
