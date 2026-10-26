# Product Line Profitability & Margin Performance Analysis for Nassau Candy Distributor

**Author:** Business Intelligence & Quantitative Analytics Group  
**Target Entity:** Nassau Candy Distributor Executive Leadership  
**Publication Classification:** Executive Working Paper / Quantitative Distribution Analytics  
**Date:** October 2026  

---

## 1. Abstract

This study delivers an empirical investigation into product-line profitability, cost dynamics, and margin performance across the commercial catalog of Nassau Candy Distributor. Analyzing a longitudinal transaction dataset comprising 10,194 validated wholesale order records, the business generated **\$141,783.63 in gross revenue**, **\$48,340.83 in direct manufacturing costs**, and **\$93,442.80 in total gross profit**, yielding an aggregate portfolio gross margin of **65.91%** across 38,654 units shipped spanning 15 stock-keeping units (SKUs). 

Despite strong headline financial margins, granular forensic accounting reveals acute structural vulnerabilities:
1. **Severe Pareto Concentration Risk:** The top 5 SKUs—exclusively comprising the Chocolate division's Wonka Bar product lines—generate **\$88,824.62 (95.06%)** of total corporate gross profit and **92.88%** of total revenue.
2. **Operational and Margin Dilution in Non-Chocolate Lines:** The Other and Sugar divisions generate sub-scale commercial returns while exhibiting severe margin leakage. Most notably, *Kazookles* exhibits a catastrophic gross margin of **7.69%** (a **92.31% cost-to-sales ratio**), consuming \$1,113.00 in production cost to return a negligible \$92.75 in profit. Concurrently, the Sugar division accounts for only 34 order lines (0.33% of company order volume), indicating that high-touch administrative overhead likely erodes its nominal 68.10% margin.
3. **Geographic Manufacturing Bottlenecks:** Production output is heavily concentrated in two facilities (*Lot's O' Nuts* in Arizona and *Wicked Choccy's* in Georgia), which collectively account for **95.06% of total profit**, leaving the firm vulnerable to single-point facility disruptions.

This paper establishes an empirical framework integrating Pareto analysis, 4-quadrant strategic product segmentation (Stars, Traps, Niches, Drains), cost-curve diagnostics, and facility-level capacity evaluation to construct an actionable SKU rationalization roadmap.

---

## 2. Background & Problem Statement

### 2.1 Confectionery Distribution Dynamics
In large-scale specialty food and confectionery distribution, sales volume is often a misleading indicator of enterprise health. Standard operational practice frequently incentivizes gross top-line expansion, obscuring the reality that high-volume product lines may carry disproportionate cost-of-goods-sold (COGS), aggressive promotional allowances, or manufacturing inefficiencies. For Nassau Candy Distributor, maintaining catalog breadth has historically served to deepen retail shelf presence and fulfill diversified vendor agreements. However, without granular SKU-level margin visibility, uncurated catalog expansion dilutes operating margins and diverts working capital away from high-yield core lines.

### 2.2 Core Business Risks
The organization faces three principal strategic and financial risks:
- **Margin Dilution & Hidden Subsidy:** High-margin chocolate lines effectively subsidize loss-making or structurally defective non-chocolate confectioneries. Products with inadequate margins absorb warehouse square footage, freight handling, and working capital without generating compensatory enterprise value.
- **Manufacturing Cost Misallocation:** Nassau Candy sources products across five dedicated manufacturing hubs. Sourcing disparities create wide margin variances, where identical packaging sizes exhibit divergent cost baselines due to localized raw material costs, labor contracts, or sub-optimal batch scheduling.
- **Supply Chain Over-Concentration:** Because the company's financial viability depends almost entirely on five premium chocolate SKUs manufactured across two primary plants, any localized operational outage (e.g., equipment breakdown, ingredient shortages, regional labor disputes) represents an existential revenue risk.

---

## 3. Dataset Architecture & Analytical Methodology

### 3.1 Data Schema and Hygiene
The empirical analysis is based on 10,194 order line items spanning multi-year wholesale operations across the United States. Data integrity was established through rigorous audit routines:
- **Transaction Validation:** Parsing and chronological verification of `Order Date` and `Ship Date` across all records.
- **Anomaly Detection & Cleaning:** Filtering of non-positive records (`Sales <= 0`, `Cost <= 0`, `Units <= 0`). The baseline data demonstrated zero missing fields across all attributes.
- **Entity Resolution & Label Standardization:** Resolving catalog anomalies, specifically reconciling *Fizzy Lifting Drinks* (Product ID `OTH-FIZ-56000`), which was historically misclassified under the Sugar division, into the Other division to achieve 100% relational integrity with production manifests.

```
+-----------------------------------------------------------------------------------------------+
|                                    TRANSACTION DATA PIPELINE                                   |
|                                                                                               |
|  [Raw Sales Transactions]         [Product-Factory Manifest]        [Factory Coordinates]    |
|      10,194 Orders                    15 Catalog SKUs                  5 Manufacturing Hubs   |
|            │                                  │                                  │            |
|            └──────────────────────┬───────────┴──────────────────────────────────┘            |
|                                   ▼                                                           |
|                     [Relational Validation & Joins]                                           |
|                     - Standardized Division Keys                                              |
|                     - Format: DD-MM-YYYY Dates                                                |
|                     - Zero-Missing Cross-Table Parity                                         |
|                                   │                                                           |
|                                   ▼                                                           |
|                      [Financial KPI Computations]                                             |
|                      - Gross Margin (%) = (Gross Profit / Sales) * 100                        |
|                      - Profit per Unit = Gross Profit / Units                                 |
|                      - Pareto Cumulative Contribution (%)                                     |
|                      - Strategic Quadrant Classification                                      |
+-----------------------------------------------------------------------------------------------+
```

### 3.2 Key Performance Indicators (KPIs)
To evaluate product and divisional health, the following quantitative metrics were established:
- **Gross Profit ($):** Defined per transaction as:
  $$\text{Gross Profit} = \text{Sales} - \text{Cost}$$
- **Gross Margin (%):** Ratio of gross margin realized per dollar of gross sales:
  $$\text{Gross Margin (\%)} = \left(\frac{\text{Gross Profit}}{\text{Sales}}\right) \times 100$$
- **Unit Margin Realization ($/unit):** Gross profit contribution normalized per unit sold:
  $$\text{Profit per Unit} = \frac{\text{Gross Profit}}{\text{Units}}$$
- **Pareto Concentration Ratio:** Cumulative contribution of SKUs sorted in descending order of absolute gross profit:
  $$\text{Cumulative Share}_k = \frac{\sum_{i=1}^k \text{Gross Profit}_i}{\sum_{i=1}^N \text{Gross Profit}_i} \times 100$$
- **Cost-to-Sales Ratio (%):** Measure of direct production burden:
  $$\text{Cost Ratio (\%)} = \left(\frac{\text{Cost}}{\text{Sales}}\right) \times 100$$

### 3.3 Strategic 4-Quadrant Matrix
Products are categorized along orthogonal axes representing commercial volume and pricing efficiency using median thresholds ($\text{Median Sales} = \$597.50$, $\text{Median Gross Margin} = 62.31\%$):
- **Stars (High Sales, High Margin):** Primary commercial engines; command strong market pricing with healthy gross margins.
- **Traps (High Sales, Low Margin):** High revenue volume that consumes significant working capital while returning subpar financial margins.
- **Niches (Low Sales, High Margin):** Highly profitable on a per-unit basis but constrained by low sales volume or limited market penetration.
- **Drains (Low Sales, Low Margin):** Value-destroying lines characterized by low sales volumes, poor pricing leverage, and high unit manufacturing costs.

### 3.4 Facility Supply Chain Integration
Each SKU is mapped to its dedicated manufacturing plant:

| Factory Name | Latitude | Longitude | Primary Division Alignment | SKUs Produced |
| :--- | :---: | :---: | :--- | :---: |
| **Lot's O' Nuts** | 32.881893 | -111.768036 | Chocolate | 3 Premium Wonka Bars |
| **Wicked Choccy's** | 32.076176 | -81.088371 | Chocolate | 2 Core Wonka Bars |
| **Secret Factory** | 41.446333 | -90.565487 | Other / Sugar | Lickable Wallpaper, Wonka Gum, Everlasting Gobstopper |
| **The Other Factory** | 35.117500 | -89.971107 | Other / Sugar | Kazookles, Hair Toffee |
| **Sugar Shack** | 48.119140 | -96.181150 | Sugar / Other | Laffy Taffy, SweeTARTS, Nerds, Fun Dip, Fizzy Lifting Drinks |

---

## 4. Empirical Findings & Financial Performance

### 4.1 Enterprise Portfolio Performance
During the audited timeframe, Nassau Candy achieved the following top-level performance:

| Portfolio Metric | Audited Value |
| :--- | :---: |
| **Total Gross Revenue** | \$141,783.63 |
| **Total Cost of Goods Sold (COGS)** | \$48,340.83 |
| **Total Gross Profit** | \$93,442.80 |
| **Aggregate Gross Margin (%)** | 65.91% |
| **Total Units Shipped** | 38,654 units |
| **Total Order Transactions** | 10,194 records |
| **Average Order Value (AOV)** | \$13.91 |
| **Average Profit per Order** | \$9.17 |

### 4.2 Divisional Financial Breakdown
Aggregating transactions by product division illustrates extreme performance disparity:

| Division | Sales (\$) | Cost (\$) | Gross Profit (\$) | Units | Orders | Gross Margin (%) | Revenue Share (%) | Profit Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Chocolate** | \$131,692.90 | \$42,868.28 | \$88,824.62 | 37,275 | 9,844 | 67.45% | 92.88% | 95.06% |
| **Other** | \$9,742.00 | \$5,361.30 | \$4,380.70 | 1,263 | 316 | 44.97% | 6.87% | 4.69% |
| **Sugar** | \$348.73 | \$111.25 | \$237.48 | 116 | 34 | 68.10% | 0.25% | 0.25% |
| **Total** | **\$141,783.63** | **\$48,340.83** | **\$93,442.80** | **38,654** | **10,194** | **65.91%** | **100.00%** | **100.00%** |

#### Key Divisional Takeaways:
1. **Chocolate Dominance:** The Chocolate division represents the core business, capturing 92.88% of sales and 95.06% of profit, operating at an enviable 67.45% gross margin.
2. **Other Division Margin Lag:** Generating \$9,742.00 in revenue, the Other division suffers from a compressed gross margin of 44.97%, driven down by disproportionately expensive contract manufacturing.
3. **Sugar Division Sub-Scale Activity:** While the Sugar division reflects a healthy gross margin percentage (68.10%), its commercial volume (\$348.73 across only 34 orders) indicates that it is virtually dormant in the marketplace.

```
DIVISIONAL REVENUE VS. PROFIT IMBALANCE
Chocolate: [████████████████████████████████████████] 92.88% Rev | 95.06% Profit ($88,824.62)
Other:     [███] 6.87% Rev | 4.69% Profit ($4,380.70)
Sugar:     [▏] 0.25% Rev | 0.25% Profit ($237.48)
```

### 4.3 Pareto Concentration Analysis (The 80/20 Rule)
A granular SKU-level Pareto decomposition proves that Nassau Candy operates under an extreme concentration pattern. While the classical Pareto principle anticipates that 20% of catalog items generate 80% of profits, here **33.3% of SKUs (5 out of 15) generate 95.06% of all gross profits**:

| Rank | Product Name | Division | Factory | Sales (\$) | Profit (\$) | Margin (%) | Profit Share (%) | Cumulative Profit (%) | Top 80% Cutoff |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **Wonka Bar - Scrumdiddlyumptious** | Chocolate | Lot's O' Nuts | \$27,874.80 | \$19,357.50 | 69.44% | 20.72% | 20.72% | Yes |
| 2 | **Wonka Bar - Triple Dazzle Caramel** | Chocolate | Wicked Choccy's | \$28,485.00 | \$18,610.20 | 65.33% | 19.92% | 40.63% | Yes |
| 3 | **Wonka Bar - Milk Chocolate** | Chocolate | Wicked Choccy's | \$26,867.75 | \$17,443.37 | 64.92% | 18.67% | 59.30% | Yes |
| 4 | **Wonka Bar - Nutty Crunch Surprise** | Chocolate | Lot's O' Nuts | \$23,574.95 | \$16,819.95 | 71.35% | 18.00% | 77.30% | Yes |
| 5 | **Wonka Bar - Fudge Mallows** | Chocolate | Lot's O' Nuts | \$24,890.40 | \$16,593.60 | 66.67% | 17.76% | 95.06% | Yes |
| 6 | Lickable Wallpaper | Other | Secret Factory | \$7,860.00 | \$3,930.00 | 50.00% | 4.21% | 99.26% | No |
| 7 | Wonka Gum | Other | Secret Factory | \$597.50 | \$310.70 | 52.00% | 0.33% | 99.60% | No |
| 8 | Everlasting Gobstopper | Sugar | Secret Factory | \$130.00 | \$104.00 | 80.00% | 0.11% | 99.71% | No |
| 9 | Kazookles | Other | The Other Factory | \$1,205.75 | \$92.75 | 7.69% | 0.10% | 99.81% | No |
| 10 | Hair Toffee | Sugar | The Other Factory | \$76.50 | \$59.50 | 77.78% | 0.06% | 99.87% | No |
| 11 | Fizzy Lifting Drinks | Other | Sugar Shack | \$78.75 | \$47.25 | 60.00% | 0.05% | 99.92% | No |
| 12 | Laffy Taffy | Sugar | Sugar Shack | \$53.73 | \$33.48 | 62.31% | 0.04% | 99.96% | No |
| 13 | SweeTARTS | Sugar | Sugar Shack | \$61.50 | \$28.70 | 46.67% | 0.03% | 99.99% | No |
| 14 | Nerds | Sugar | Sugar Shack | \$15.00 | \$7.00 | 46.67% | 0.01% | 99.99% | No |
| 15 | Fun Dip | Sugar | Sugar Shack | \$12.00 | \$4.80 | 40.00% | 0.01% | 100.00% | No |

The bottom 10 products combined represent two-thirds of catalog complexity yet generate only **4.94% (\$4,618.18)** of cumulative gross profit.

### 4.4 Strategic Quadrant Classification
Evaluating SKUs against median commercial benchmarks yields the following four-quadrant distribution:

```
               HIGH GROSS MARGIN (>= 62.31%)
                     │
         NICHES      │      STARS
   - Everlasting Gob │ - Wonka Bar Scrumdiddlyumptious
   - Hair Toffee     │ - Wonka Bar Triple Dazzle Caramel
   - Laffy Taffy     │ - Wonka Bar Milk Chocolate
                     │ - Wonka Bar Nutty Crunch Surprise
                     │ - Wonka Bar Fudge Mallows
─────────────────────┼─────────────────────
   LOW SALES         │         HIGH SALES (>= $597.50)
         DRAINS      │      TRAPS
   - Fizzy Lifting D │ - Lickable Wallpaper
   - SweeTARTS       │ - Wonka Gum
   - Nerds           │ - Kazookles
   - Fun Dip         │
                     │
               LOW GROSS MARGIN (< 62.31%)
```

- **Stars (5 SKUs):** All 5 Wonka Bars. Combine high sales (each exceeding \$23,000) with superior margins (64.92% to 71.35%).
- **Traps (3 SKUs):** *Lickable Wallpaper* (\$7,860 sales, 50.00% margin), *Wonka Gum* (\$597.50 sales, 52.00% margin), and *Kazookles* (\$1,205.75 sales, 7.69% margin). They absorb significant inventory capital while failing to achieve the corporate target margin.
- **Niches (3 SKUs):** *Everlasting Gobstopper* (80.00% margin), *Hair Toffee* (77.78% margin), and *Laffy Taffy* (62.31% margin). Products with strong pricing efficiency but virtually non-existent sales volume (\$53 to \$130 total).
- **Drains (4 SKUs):** *Fizzy Lifting Drinks* (60.00% margin, \$78.75 sales), *SweeTARTS* (46.67% margin, \$61.50 sales), *Nerds* (46.67% margin, \$15.00 sales), and *Fun Dip* (40.00% margin, \$12.00 sales). Suffer from both low sales volume and sub-standard margins.

### 4.5 Manufacturing Facility Dependency
Evaluating performance by manufacturing hub highlights acute operational centralization:

| Manufacturing Hub | Sales (\$) | COGS (\$) | Gross Profit (\$) | Units | Orders | Gross Margin (%) | Revenue Share (%) | Profit Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lot's O' Nuts** | \$76,340.15 | \$23,569.10 | \$52,771.05 | 21,412 | 5,692 | 69.13% | 53.84% | 56.47% |
| **Wicked Choccy's** | \$55,352.75 | \$19,299.18 | \$36,053.57 | 15,863 | 4,152 | 65.13% | 39.04% | 38.58% |
| **Secret Factory** | \$8,587.50 | \$4,242.80 | \$4,344.70 | 884 | 217 | 50.59% | 6.06% | 4.65% |
| **The Other Factory** | \$1,282.25 | \$1,130.00 | \$152.25 | 388 | 100 | 11.87% | 0.90% | 0.16% |
| **Sugar Shack** | \$220.98 | \$99.75 | \$121.23 | 107 | 33 | 54.86% | 0.16% | 0.13% |
| **Total** | **\$141,783.63** | **\$48,340.83** | **\$93,442.80** | **38,654** | **10,194** | **65.91%** | **100.00%** | **100.00%** |

Together, *Lot's O' Nuts* and *Wicked Choccy's* account for **92.88% of revenue** and **95.06% of company gross profit**. Conversely, *The Other Factory* generates an aggregate facility margin of only **11.87%**, dragged down by the severe structural imbalance of the *Kazookles* production contract.

---

## 5. Cost Structure Diagnostics & Margin Leakage

### 5.1 Deep-Dive Forensic Case Study: The "Kazookles" Dilemma
The most critical vulnerability identified in Nassau Candy's catalog is *Kazookles* (Product ID `OTH-KAZ-38000`), produced at *The Other Factory*.

| Diagnostic Metric | Kazookles Value | Catalog Median | Portfolio Benchmark | Variance / Status |
| :--- | :---: | :---: | :---: | :---: |
| **Gross Margin (%)** | **7.69%** | 62.31% | 65.91% | -58.22% (Severe Deficit) |
| **Cost-to-Sales Ratio** | **92.31%** | 37.69% | 34.09% | +58.22% (Excessive COGS) |
| **Gross Revenue** | \$1,205.75 | \$597.50 | \$9,452.24 | Above median volume |
| **Manufacturing Cost** | \$1,113.00 | \$286.80 | \$3,222.72 | 3.9x median cost |
| **Realized Gross Profit** | **\$92.75** | \$104.00 | \$6,229.52 | Negligible return |
| **Units Produced / Sold** | 371 | 371 | 2,576 | High physical burden |
| **Average Unit Price** | \$3.25 | \$3.49 | \$3.67 | Standard retail tier |
| **Average Unit Cost** | \$3.00 | \$1.10 | \$1.25 | **2.7x typical cost baseline** |
| **Realized Profit / Unit** | **\$0.25** | \$2.25 | \$2.42 | Marginal unit yield |

```
KAZOOKLES COST VS. REVENUE BREAKDOWN
[████████████████████████████████████████████████░]
Manufacturing Cost: $1,113.00 (92.31%)
Realized Profit:     $92.75 (7.69%)
Total Revenue:      $1,205.75 (100.00%)
```

#### Financial Consequences of Kazookles:
1. **Inefficient Working Capital Allocation:** The company tied up \$1,113.00 in direct cash to manufacture 371 units of Kazookles across 96 individual orders.
2. **Unaccounted Operating Losses:** The \$0.25 unit margin considers only direct COGS. When factoring in standard packaging, picker labor, pallet staging, and shipping line allocation (which averages \$0.75–\$1.50 per unit in typical confectionery distribution), **Kazookles operates at a substantial net operating loss**.
3. **Contract Failure:** Sourced from *The Other Factory*, Kazookles suffers from an unfavorable tolling or production contract with unit manufacturing costs of \$3.00 against a wholesale realization of \$3.25.

### 5.2 Sugar Division Margin Erosion and Sub-Scale Overhead
The Sugar division exhibits two distinct structural problems:
1. **Sub-Threshold Margins in Heritage Lines:** *Fun Dip* (40.00%), *Nerds* (46.67%), and *SweeTARTS* (46.67%) fall significantly below the corporate 60% margin hurdle.
2. **Micro-Order Overhead:** The entire Sugar division produced only 34 orders yielding \$237.48 in gross profit over the analyzed multi-year timeframe:
   - *Fun Dip:* 3 total orders, \$12.00 gross revenue, \$4.80 profit.
   - *Nerds:* 4 total orders, \$15.00 gross revenue, \$7.00 profit.
   - *Everlasting Gobstopper:* 3 total orders, \$130.00 gross revenue, \$104.00 profit.
   - *Hair Toffee:* 4 total orders, \$76.50 gross revenue, \$59.50 profit.

In commercial wholesale distribution, the fully loaded cost to process, invoice, pick, pack, and reconcile an individual purchase order typically ranges from \$15.00 to \$35.00. Consequently, generating \$4.80 of gross profit from three orders of Fun Dip represents a severe operational drain.

---

## 6. Strategic Recommendations & SKU Rationalization

Based on the quantitative findings, Nassau Candy Distributor should execute a three-phase optimization roadmap:

```
+───────────────────────────────────────────────────────────────────────────────────────────────+
|                           THREE-PHASE TRANSFORMATION ROADMAP                                  |
|                                                                                               |
|  PHASE 1: Immediate Triage (Days 1–30)                                                       |
|  ├─ Re-negotiate Kazookles manufacturing contract or terminate SKU immediately.               |
|  ├─ Establish a strict 60% gross margin floor across all active product lines.                |
|  └─ Enforce Minimum Order Quantities (MOQ) on all Sugar SKUs ($250 order minimum).            |
|                                                                                               |
|  PHASE 2: Commercial Re-Alignment (Days 31–90)                                                |
|  ├─ Reprice sub-threshold lines (Fun Dip +35%, SweeTARTS +25%, Nerds +25%).                   |
|  ├─ Formalize long-term supply and capacity agreements with Lot's O' Nuts & Wicked Choccy's.  |
|  └─ Re-evaluate Secret Factory contract terms on Lickable Wallpaper (target >60% margin).     |
|                                                                                               |
|  PHASE 3: Catalog & Supply Chain Optimization (Days 91–180)                                  |
|  ├─ Consolidate production away from The Other Factory and Sugar Shack.                      |
|  ├─ Reallocate working capital into core Wonka Bar Chocolate line extensions.                 |
|  └─ Implement real-time automated gross margin tracking dashboards in Streamlit.             |
+───────────────────────────────────────────────────────────────────────────────────────────────+
```

### 6.1 Phase 1: Immediate SKU Triage (Days 1–30)
- **Eliminate or Restructure Kazookles:** 
  - Immediately demand a contract cost reduction from *The Other Factory* from \$3.00/unit to under \$1.25/unit (matching catalog benchmarks).
  - If the manufacturer refuses, **de-list Kazookles immediately**. Terminating Kazookles will instantly liberate \$1,113.00 in working capital and eliminate 96 low-value fulfillment touches, improving total company return on capital.
- **Enforce Strict Wholesale Minimums for Sugar Lines:**
  - Implement a mandatory minimum order quantity (MOQ) of full case packs (minimum 24 units) and an aggregate order threshold of \$250.00. Customers seeking single-unit purchases of Fun Dip, SweeTARTS, or Nerds must be transitioned to third-party retail channels.

### 6.2 Phase 2: Pricing & Commercial Restructuring (Days 31–90)
- **Margin Reset for Sub-60% Products:**
  - Increase list wholesale pricing on *Fun Dip* from \$1.50 to \$2.05 (+36.7%), lifting gross margin from 40.00% to 56.10%.
  - Increase *SweeTARTS* and *Nerds* pricing by 25.0%, bringing both lines to 57.33% gross margin.
  - Re-negotiate pricing on *Lickable Wallpaper* (currently yielding 50.00% on \$7,860.00 sales) with *Secret Factory* to lower unit production costs from \$10.00 to \$7.50, capturing an incremental \$982.50 in gross profit without altering retail pricing.
- **Factory Capacity Guarantees:**
  - Execute multi-year service-level agreements (SLAs) with *Lot's O' Nuts* (Arizona) and *Wicked Choccy's* (Georgia). Given that these two hubs generate 95.06% of corporate gross profit, establishing contractual price locks on cocoa, sugar, and nut paste inputs is vital to preserving the portfolio's 67.45% chocolate margin.

### 6.3 Phase 3: Long-Term Supply Chain & Catalog Realignment (Days 91–180)
- **Facility Consolidation:**
  - *The Other Factory* generates a net facility gross margin of only 11.87% on \$1,282.25 in sales. *Sugar Shack* generates only \$220.98 in total revenue. Sourcing operations from these two plants should be audited for full consolidation into *Secret Factory* or transitioned to co-packing partners, eliminating vendor management overhead.
- **Reinvestment into Chocolate Core:**
  - Nassau Candy's core competitive advantage lies unequivocally in its Wonka Bar franchises. Working capital freed up from rationalized SKUs should be redeployed into expanding flavor extensions, seasonal formats, and bulk retail displays for the top-performing *Scrumdiddlyumptious* and *Triple Dazzle Caramel* lines.

---

## 7. Conclusion

Nassau Candy Distributor exhibits robust high-level financial fundamentals, characterized by a **65.91% portfolio gross margin** and healthy cash generation of **\$93,442.80 in gross profit**. However, granular empirical analysis demonstrates that this performance is entirely driven by an elite cluster of five chocolate Wonka Bar SKUs, while non-chocolate divisions introduce acute margin dilution and operational complexity.

Products such as *Kazookles* erode financial efficiency by absorbing substantial capital (\$1,113.00) at an unsustainable 7.69% gross margin, while sub-scale Sugar lines burden order-processing workflows. Furthermore, over-dependence on two production facilities creates supply chain fragility.

By executing the strategic recommendations outlined herein—delisting or restructuring *Kazookles*, enforcing minimum order thresholds on low-volume lines, renegotiating sub-scale co-manufacturing contracts, and safeguarding chocolate capacity—Nassau Candy Distributor can insulate itself against margin erosion, streamline warehouse operations, and secure a resilient foundation for long-term profitable expansion.

---

## References & Data Sources
1. Nassau Candy Distributor Commercial Wholesale Transaction Repository (10,194 records, 2024–2026).
2. Nassau Candy Technical Manufacturing Catalog & Facility Specification Manifest (`docs/project_instructions.md`).
3. Core Analytical Computation Engine & Diagnostics Suite (`src/data_loader.py`, `src/analytics.py`).
