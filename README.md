# Supply Chain Operations Dashboard

A **Power BI / Tableau dashboard project** built on top of a pre-flattened
aerospace-supply-chain dataset (300 parts × 6 sites × 156 weeks, ~13.5
billion in inventory at risk). The repo ships everything you need to
build a 5-page operations dashboard in **under 2 hours** in either tool:

- A **single denormalized CSV** (`supply_chain_flat.csv`, ~30 MB,
  280,800 rows): joins are pre-done, dimensions and measures are
  side-by-side, no data-model modelling required at import time.
- A **page-by-page build guide** ([`DASHBOARD_BUILD_GUIDE.md`](DASHBOARD_BUILD_GUIDE.md)):
  exactly which fields go where on each of 5 pages.
- A **DAX measures reference** ([`DAX_measures.md`](DAX_measures.md)) for
  Power BI, with copy-paste-ready code for 18 measures.
- A **Tableau calculated-fields reference**
  ([`Tableau_calc_fields.md`](Tableau_calc_fields.md)): equivalent
  formulas for Tableau Desktop / Tableau Public.

The five pages cover the full operations review:

| Page | Audience | Key questions answered |
|---|---|---|
| **Executive Summary** | VP / GM | Inventory at risk? Stockouts trending up? |
| **Inventory Health** | Materials manager | Which part-families are running thin? |
| **Supplier Performance** | Procurement | Which suppliers are missing PO due dates? |
| **Quality** | Quality engineering | Where are defects concentrated? |
| **Risk Watch** | Operations leadership | Which critical parts need intervention now? |

## What's actually demonstrated

| Concept | Used in |
|---|---|
| **Time-intelligence functions** (rolling 4-week, MoM, YoY) | Pages 1, 2, 4 |
| **Filter-context manipulation** (CALCULATE / FIXED / LOD) | DAX measures M03, M07, M12 |
| **Conditional aggregation** | M01, M04, M09 |
| **Heat maps** with conditional colour by criticality | Page 2 |
| **Pareto / 80-20 analysis** | Page 4 |
| **KPI cards with trend sparklines** | Page 1 |
| **Cross-page filtering / drill-through** | Pages 3, 5 |
| **Variance-of-actuals vs forecast** | Page 2 |

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

## Get it running

### Power BI Desktop (free, Windows-only)

1. Download Power BI Desktop from `aka.ms/pbiSingleInstaller`.
2. Open Power BI → **Get Data** → **Text/CSV** → select
   `supply_chain_flat.csv`.
3. Click **Transform Data** → confirm types (`date` should be Date, the
   numerics should be Decimal/Whole, booleans are Text).
4. Click **Close & Apply**.
5. Follow [`DASHBOARD_BUILD_GUIDE.md`](DASHBOARD_BUILD_GUIDE.md) page by
   page.

### Tableau Public (free, cross-platform)

1. Download Tableau Public from `public.tableau.com/en-us/s/download`.
2. **Connect** → **Text File** → select `supply_chain_flat.csv`.
3. Confirm column types in the Data Source pane.
4. Follow the Tableau notes inside
   [`DASHBOARD_BUILD_GUIDE.md`](DASHBOARD_BUILD_GUIDE.md) and use the
   formulas in [`Tableau_calc_fields.md`](Tableau_calc_fields.md).

## Repository layout

```
.
├── supply_chain_flat.csv          ← 280,800-row BI-ready dataset
├── prepare_data.py                ← regenerates the CSV from source CSVs
├── DASHBOARD_BUILD_GUIDE.md       ← page-by-page build instructions
├── DAX_measures.md                ← 18 Power BI measures, copy-paste-ready
├── Tableau_calc_fields.md         ← Tableau equivalents
├── requirements.txt
├── LICENSE
└── README.md
```

## Regenerating the data

The flattened CSV is derived from the four-table source dataset that
ships with the [Supplier Risk & Lead Time
Predictor](https://github.com/masonsau0/Supplier-Risk-Lead-Time-Predictor)
project. To regenerate:

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
**Tableau Public** (LOD expressions, calculated fields) · **Python**
(`pandas`) for the data preparation pipeline · the underlying ML risk
scoring lives in the sibling [Supplier Risk
Predictor](https://github.com/masonsau0/Supplier-Risk-Lead-Time-Predictor)
repo.
