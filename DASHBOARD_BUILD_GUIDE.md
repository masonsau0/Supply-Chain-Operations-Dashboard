# Dashboard Build Guide

Step-by-step build for the 5-page Supply Chain Operations Dashboard, in
either Power BI Desktop or Tableau Public.

Each page lists: **purpose**, **layout sketch**, **fields/measures used**,
and **build steps**. Total build time ~2 hours per tool.

---

## Page 1 — Executive Summary

**Purpose.** One-glance health of the supply-chain operation. The first
panel a VP / GM opens.

**Layout** (4 KPI cards across the top, 2 trend charts below, 1 table at
the bottom):

```
+----------+----------+----------+----------+
| Inv $    | Active   | Avg DoS  | Defect   |
| (latest) | Stockouts|          | Rate     |
+----------+----------+----------+----------+
|  Weekly stockout count (line, last 26 wks)|
+-------------------------------------------+
|  Monthly defect count by severity (stacked bar)
+-------------------------------------------+
|  Top-10 active stockouts table             |
+-------------------------------------------+
```

### Build steps

1. **KPI cards** (4 of them):
   - Inventory $ — measure `Inventory Value (Latest)` formatted as
     currency, large card visual.
   - Active Stockouts — measure `Active Stockouts`, large card visual.
   - Avg Days of Supply — measure `Days of Supply` averaged.
   - Defect Rate — `Total Defects / SUM(consumption_qty)`.

2. **Weekly stockout line**:
   - X-axis: `date` (continuous, week granularity).
   - Y-axis: `Stockout Weeks` measure.
   - Filter: last 26 weeks.

3. **Monthly defect stacked bar**:
   - X-axis: `date` (month).
   - Y-axis: `defects_l4w`.
   - Series: `defect_severity` (would need to bring this in from the
     source `quality_incidents.csv` if you want full severity breakdown
     — optional enhancement).

4. **Top-10 stockouts table**:
   - Filter: `date` = latest week.
   - Filter: `backorder_qty > 0`.
   - Columns: `part_id`, `part_family`, `criticality_class`,
     `backorder_qty`, `pending_po_qty`.
   - Sort: `backorder_qty` desc, top 10.

---

## Page 2 — Inventory Health

**Purpose.** Materials manager's daily view: where is inventory thinning?

**Layout**:

```
+----------------------------------+----------------+
| Days of Supply heat map          | Stockout %     |
| (rows: part_family,              | by family      |
|  cols: criticality_class)        | (bar chart)    |
+----------------------------------+----------------+
| Forecast vs Actual Consumption (line, last 52 wks)|
+----------------------------------------------------+
| Parts at risk: DoS < 14 days (table, top 25)      |
+----------------------------------------------------+
```

### Build steps

1. **Days-of-supply heat map**:
   - Rows: `part_family`.
   - Columns: `criticality_class`.
   - Values: `Days of Supply` (or use `Avg Consumption L4W` then divide
     in tooltip).
   - Conditional format: green = high (good), red = low (bad). Invert
     the gradient since low DoS is the problem.

2. **Stockout % by family** (horizontal bar):
   - Y-axis: `part_family`.
   - X-axis: `Stockout Rate`.
   - Sort descending — biggest offender at top.

3. **Forecast vs actual line**:
   - X-axis: `date`.
   - Two lines: `SUM(forecast_qty)` and `SUM(consumption_qty)`.
   - Use a dual-axis or overlay; legend tells the story.

4. **Parts at risk table**:
   - Filter: `Days of Supply < 14`.
   - Columns: `part_id`, `criticality_class`, `on_hand_qty`,
     `Avg Consumption L4W`, `Days of Supply`, `pending_po_qty`,
     `lead_time_days`.
   - Sort: `Days of Supply` ascending.

---

## Page 3 — Supplier Performance

**Purpose.** Procurement view: which suppliers are missing PO due dates?

**Layout**:

```
+--------------------------------+------------------+
| Lead time variance distribution| Defects per     |
| (box plot per supplier)        | supplier (bar)  |
+--------------------------------+------------------+
| On-time PO % by supplier (bar, sorted asc)        |
+----------------------------------------------------+
| High-risk supplier $ exposure (table)             |
+----------------------------------------------------+
```

### Build steps

1. **Lead time variance** — box plot or bar:
   - X-axis: `supplier_id_primary`.
   - Y-axis: `lead_time_days`.
   - For full variance, you'd want PO-level `actual_lead_time = receipt_date - order_date`,
     which means joining the source `purchase_orders.csv` directly. The
     flat CSV ships only the *baseline* lead time per part.

2. **Defects per supplier**:
   - X-axis: `supplier_id_primary`.
   - Y-axis: `Total Defects`.
   - Sort descending.

3. **On-time PO %**:
   - This requires PO-level data; in the flat CSV use `pending_po_qty`
     as a proxy ("how many POs are still outstanding past their
     promised date").

4. **High-risk supplier $ exposure**:
   - Table filtered to `supplier_risk_class = "High"`.
   - Columns: `supplier_id_primary`, `Inventory Value (Latest)`,
     `Active Stockouts`, `Total Defects`.

---

## Page 4 — Quality

**Purpose.** Defect concentration and Pareto analysis.

**Layout**:

```
+---------------------------------+------------------+
| Defects 13-week trend (line)    | Defect rate vs  |
|                                 | criticality (bar)|
+---------------------------------+------------------+
| Top 20 defective parts (Pareto chart)             |
+----------------------------------------------------+
```

### Build steps

1. **Defects 13-week trend**:
   - X-axis: `date` (week).
   - Y-axis: `Defects (4W Rolling)` or raw `defects_l4w`.

2. **Defect rate vs criticality**:
   - X-axis: `criticality_class`.
   - Y-axis: `Total Defects / SUM(consumption_qty)`.

3. **Pareto chart** (top 20 defective parts):
   - Sort `part_id` by `Total Defects` descending.
   - Bar = `Total Defects` per part.
   - Line on dual-axis = cumulative % of total defects.
   - In Tableau: use a running-total table calc divided by overall
     total. In Power BI: use a `Pareto Cumulative %` measure with
     `EARLIER` or table-context tricks.

---

## Page 5 — Risk Watch

**Purpose.** What needs intervention this week?

**Layout**:

```
+----------------------------------------------------+
| Critical parts at risk (filter: A-class + stockout)|
| Big number + flag list                             |
+----------------------------------------------------+
| Composite Risk Score table                         |
| (sortable list of all parts with score >= 5)       |
+----------------------------------------------------+
| Action recommendations                             |
| (text panel - documented playbook)                 |
+----------------------------------------------------+
```

### Build steps

1. **Critical parts at risk card**:
   - Big-number visual showing `Critical at Risk` measure.
   - Below it, a small table:
     - Filter: `criticality_class = "A"`, `backorder_qty > 0`,
       `date = MAX(date)`.
     - Columns: `part_id`, `supplier_id_primary`, `backorder_qty`,
       `pending_po_qty`, `lead_time_days`.
     - Conditional format: red row background.

2. **Composite risk score table**:
   - Filter: `Risk Score >= 5`.
   - Columns: `part_id`, `criticality_class`, `supplier_risk_class`,
     `Risk Score`, current backorder, pending PO.
   - Sort: `Risk Score` descending.
   - Conditional format: gradient on `Risk Score`.

3. **Action recommendations** — static text panel:
   ```
   - Risk Score >= 7 → Daily standup escalation; expedite freight.
   - Risk Score 5-6  → Procurement to confirm PO status; trigger
                       safety-stock review.
   - Score 3-4       → Watch list; review next sprint.
   ```

---

## Cross-page interactivity

- **Date slicer** at top of every page — `Relative Date: Last 13 weeks`
  by default.
- **Site filter** — dropdown on every page so the regional director can
  view their site only.
- **Drill-through** from Page 5 (Risk Watch) → Page 3 (Supplier
  Performance) preserving the supplier filter.
- **Drill-through** from Page 5 → Page 4 (Quality) preserving the part
  filter.

In Power BI: **Page 1 ribbon → Edit interactions** to control which
visual filters which.
In Tableau: **Dashboard → Actions → Filter** with target sheets.

---

## Final polish

- **Title page** with a 1-line description, last-refresh timestamp, and
  data-source disclaimer.
- **Tooltips** for each measure briefly explaining what it shows.
- **Mobile layout** (Power BI: View → Mobile layout) — at minimum, KPI
  cards rearranged vertically.
- **Theme** — pick the Power BI / Tableau corporate theme matching the
  template you'd expect at your target employer (or just go with the
  default + a clean colour palette).
