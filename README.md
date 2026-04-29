# Supply Chain Operations Dashboard

A **5-page Power BI dashboard** for an aerospace MRO supply chain — 300
parts × 6 sites × 156 weeks of inventory, purchase order, and quality
data, ~$13.5B in inventory under management. Built on a single denormalised
fact table joined and rolled up in Python (`pandas`).

The five pages cover the full operations review:

| Page | Key questions answered |
|---|---|
| **Executive Summary** | Inventory at risk? Stockouts trending up? |
| **Inventory Health** | Which part-families are running thin? |
| **Supplier Performance** | Which suppliers are missing PO due dates? |
| **Quality** |  Where are defects concentrated? |
| **Risk Watch** | Which critical parts need intervention now? |

## What's demonstrated

| Concept | Used in |
|---|---|
| **Time-intelligence functions** (rolling 4-week, MoM, YoY) | Pages 1, 2, 4 |
| **Filter-context manipulation** (`CALCULATE`, `ALL`, `DATESINPERIOD`) | KPI cards, latest-week measures |
| **Conditional aggregation** | Stockout counts, critical-at-risk counts |
| **Heat-map matrix** with conditional colour by Days-of-Supply | Page 2 |
| **Pareto / 80-20 analysis** with cumulative-share line | Page 4 |
| **Composite risk score** combining criticality, stockout, defects, supplier risk | Page 5 |
| **Cross-page filtering and drill-through** | Pages 3, 5 |
| **Forecast vs actuals overlay** | Page 2 |

## The data

`supply_chain_flat.csv`: one row per (date, site, part) with all
dimensions and pre-computed measures.

| Column | Type | Description |
|---|---|---|
| date | date | ISO week-ending date (Mondays) |
| site_id | string | One of 6 sites |
| part_id | string | One of 300 parts |
| part_family | string | 8 product families (Electrical, Cabin, …) |
| criticality_class | string | A (most critical) / B / C |
| supplier_id_primary | string | 36 suppliers |
| supplier_risk_class | string | Low / Medium / High |
| is_repairable | string | Yes / No |
| unit_cost | numeric | Per-unit cost |
| lead_time_days | int | Baseline supplier lead time |
| on_hand_qty | int | Units in inventory at week-end |
| consumption_qty | int | Units consumed during the week |
| backorder_qty | int | Units short of demand |
| blocked_qty | int | Units quarantined / on hold |
| forecast_qty | int | Forecasted weekly demand |
| forecast_type | string | Baseline / Adjusted |
| forecast_uplift_pct | numeric | Adjustment factor applied to forecast |
| planned_maintenance | bool | True if scheduled maintenance week |
| inventory_value | numeric | on_hand_qty × unit_cost |
| pending_po_qty | int | Outstanding POs not yet received as-of date |
| defects_l4w | int | Quality incidents in last 4 weeks |

## Open the dashboard

Install Power BI Desktop (free, Windows) from `aka.ms/pbiSingleInstaller`,
then open [`Supply_Chain_Dashboard.pbix`](Supply_Chain_Dashboard.pbix).
The `.pbix` ships with the data embedded; click **Home → Refresh** to
re-read `supply_chain_flat.csv` from disk.

## Repository layout

```
.
├── Supply_Chain_Dashboard.pbix    ← the 5-page dashboard
├── supply_chain_flat.csv          ← 280,800-row BI-ready dataset
├── prepare_data.py                ← regenerates the CSV from source CSVs
├── enhance_for_demo.py            ← injects demo-friendly values into the latest 4 weeks
├── requirements.txt
├── LICENSE
└── README.md
```

## Regenerating the data

The flattened CSV is derived from the four-table source dataset that
ships with the [Aerospace Supplier Risk &amp; Lead Time
Predictor](https://github.com/masonsau0/Aerospace-Supplier-Risk-Lead-Time-Predictor)
project.

```bash
pip install -r requirements.txt
python prepare_data.py
```

The script joins the four source tables, computes `inventory_value`,
`pending_po_qty` (POs outstanding as-of each week), and `defects_l4w`
(rolling 4-week quality-incident count), and writes
`supply_chain_flat.csv`.

## Stack

**Power BI Desktop** (DAX, time-intelligence, conditional formatting) ·
**Python** (`pandas`) for the data preparation pipeline · the underlying
ML risk scoring lives in the sibling [Aerospace Supplier Risk
Predictor](https://github.com/masonsau0/Aerospace-Supplier-Risk-Lead-Time-Predictor)
repo.
