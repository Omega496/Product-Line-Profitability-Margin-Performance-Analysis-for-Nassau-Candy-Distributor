# Nassau Candy Distributor: Product Line Profitability & Margin Performance

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/streamlit-1.66.0-red.svg)](https://streamlit.io/)

An institutional-grade quantitative business intelligence suite and interactive dashboard analyzing SKU profitability, margin performance, cost structures, and manufacturing dependencies across 10,194 wholesale transactions.

---

## Architecture & Project Structure

```
├── app.py                         # Interactive Streamlit 4-module dashboard
├── src/
│   ├── __init__.py                # Source package init
│   ├── data_loader.py             # Relational joins, date parsing, cleaning & KPI enrichment
│   └── analytics.py               # Pareto 80/20, 4-Quadrant segmentation, rollups & volatility
├── data/
│   ├── cleaned_transactions.csv   # Cleaned, validated, and KPI-enriched dataset (10,194 rows)
│   ├── factory_coordinates.csv    # Geographic coordinates of 5 manufacturing hubs
│   └── product_factory_mapping.csv # Relational mapping of 15 SKUs to factories
├── research_paper.md              # 27KB forensic analytical research paper
├── executive_summary.md           # Concise decision memo for executive stakeholders
├── pyproject.toml                 # Project build configuration and dependencies
└── requirements.txt               # Pip dependencies
```

---

## Quickstart & Installation

1. **Environment Setup:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Generate Cleaned Dataset Artifact:**
   ```bash
   python src/data_loader.py
   ```

3. **Run Analytics & Validation Engine:**
   ```bash
   python src/analytics.py
   ```

4. **Launch Streamlit Web Application:**
   ```bash
   streamlit run app.py
   ```

---

## Executive Benchmark Metrics
- **Total Revenue:** \$141,783.63
- **Total Cost (COGS):** \$48,340.83
- **Total Gross Profit:** \$93,442.80
- **Portfolio Gross Margin:** 65.91%
- **Total Units Shipped:** 38,654
- **Pareto Concentration:** Top 5 SKUs generate 95.06% of total profit (\$88,824.62).

---

## Deliverables Summary
- **Streamlit Application (`app.py`):** Interactive BI dashboard featuring 4 analytical modules, dynamic margin threshold sliders, multi-division filtering, and date-range slicing.
- **Analytical Engine (`src/analytics.py`):** Vectorized calculation of Gross Margin, Profit per Unit, Pareto 80/20 curve, 4-Quadrant classification (Stars, Traps, Niches, Drains), and temporal Margin Volatility.
- **Research Paper (`research_paper.md`):** Complete exploratory data analysis, mathematical formulations, forensic cost diagnostics, and catalog rationalization strategies.
- **Executive Summary (`executive_summary.md`):** Decision memo detailing financial exposure and an actionable 3-phase transformation roadmap.
