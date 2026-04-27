# Dashboard Build Guide — Click-by-Click

Complete beginner's tutorial for building the Supply Chain Operations
Dashboard in **Power BI Desktop**. Assumes you've never opened Power BI
before. Total time: ~2 hours of focused work.

The guide covers, in order:

1. [Install Power BI Desktop](#1-install-power-bi-desktop)
2. [Load and prepare the data](#2-load-and-prepare-the-data)
3. [Tour of the Power BI interface](#3-tour-of-the-power-bi-interface)
4. [Set up the base measures (one-time setup)](#4-set-up-the-base-measures-one-time-setup)
5. [Page 1 — Executive Summary](#5-page-1--executive-summary)
6. [Page 2 — Inventory Health](#6-page-2--inventory-health)
7. [Page 3 — Supplier Performance](#7-page-3--supplier-performance)
8. [Page 4 — Quality](#8-page-4--quality)
9. [Page 5 — Risk Watch](#9-page-5--risk-watch)
10. [Cross-page filtering and drill-through](#10-cross-page-filtering-and-drill-through)
11. [Save and commit your `.pbix` file](#11-save-and-commit-your-pbix-file)
12. [Common gotchas](#12-common-gotchas)

For Tableau users, see [`Tableau_calc_fields.md`](Tableau_calc_fields.md) —
the calculations are the same, only the UI differs.

---

## 1. Install Power BI Desktop

1. Go to **https://aka.ms/pbiSingleInstaller** in your browser.
2. The page auto-detects your OS and offers an `.exe` installer.
3. Click **Download**, then run the installer. Accept the defaults
   (install path, language).
4. When done, find **Power BI Desktop** in your Start Menu and open it.
5. On first launch you'll see a **welcome dialog** asking you to sign in
   — you can dismiss this with the small "X" in the top right. You don't
   need a Microsoft account to build dashboards locally.

> **Note.** Power BI Desktop is **Windows-only and free**. There's no
> Mac version — if you're on Mac, use a Windows VM (Parallels) or skip
> to Tableau Public, which is cross-platform.

---

## 2. Load and prepare the data

### 2a. Get the CSV into Power BI

1. With Power BI Desktop open and the welcome dialog closed, look at the
   **Home** tab in the ribbon at the top.
2. Click **Get data** (left side of the ribbon, has a small database
   icon).
3. A dialog opens listing data sources. The most common ones are pinned
   at the top — click **Text/CSV**.
4. Click **Connect** in the bottom right of the dialog.
5. A file-browser opens. Navigate to your repo folder and select
   `supply_chain_flat.csv`. Click **Open**.
6. A preview window appears showing the first 200 rows of the CSV.
7. **Don't click Load yet.** Instead click **Transform Data** (next
   button to the right). This opens **Power Query Editor** so we can
   verify the column types before loading.

### 2b. Verify column types in Power Query Editor

Power BI auto-detects types but sometimes gets dates or numbers wrong.
Take 30 seconds to verify.

1. The Power Query Editor opens in a new window. You'll see the data in
   a grid, with column names at the top and small **type icons** next to
   each name (`123` for whole number, `1.2` for decimal, calendar icon
   for date, `ABC` for text).
2. Verify each column matches this list (most should be auto-detected
   correctly):

| Column | Should be type |
|---|---|
| `date` | Date |
| `site_id`, `part_id`, `part_family`, `criticality_class`, `supplier_id_primary`, `supplier_risk_class`, `is_repairable`, `forecast_type` | Text |
| `unit_cost`, `inventory_value`, `forecast_uplift_pct` | Decimal Number |
| `lead_time_days`, `on_hand_qty`, `consumption_qty`, `backorder_qty`, `blocked_qty`, `forecast_qty`, `pending_po_qty`, `defects_l4w` | Whole Number |
| `planned_maintenance` | True/False (Boolean) |

3. **To fix a wrong type:** click the type icon next to the column name
   → choose the correct type from the dropdown. If it asks "Replace
   current" vs "Add new step", choose **Replace current**.

### 2c. Load the data

1. Top-left of Power Query Editor, click **Close & Apply** (the icon
   shows a checkmark over a closing folder).
2. Power BI returns to the main window. You'll see a small loading
   indicator briefly, then the data is available.
3. Look at the **Data pane** on the right side of the screen. You should
   see a table called **`supply_chain_flat`** with all 21 columns
   listed below it. Click the small triangle next to the table name to
   expand and confirm.

> **If you don't see the Data pane:** click **View** in the ribbon →
> verify **Data** is checked in the "Show panes" group.

---

## 3. Tour of the Power BI interface

Take 60 seconds to orient yourself. There's a lot on screen but only
a few zones matter for this build.

```
+-------------------------------------------------------------+
|  Ribbon (Home, Insert, Modeling, View, Help)                |
+-------------------------------------------------------------+
|                                              | Filters     |
|                                              |             |
|        Canvas                                | Visualizations
|        (where visuals go)                    |             |
|                                              | Data        |
|                                              |             |
|                                              |             |
+-------------------------------------------------------------+
|  Page tabs:  [ Page 1 ]  [ + ]                              |
+-------------------------------------------------------------+
```

### Key zones

- **Ribbon (top)** — like Excel/Word ribbon. Most-used commands here:
  **Get data**, **New measure**, **Save**.
- **Canvas (middle)** — where you place visuals. Each "page" of the
  dashboard is a separate canvas.
- **Page tabs (bottom)** — switch between pages. Click the **+** to
  add a new page; right-click any tab to rename.
- **Filters pane (right, top)** — drop fields here to filter visuals.
- **Visualizations pane (right, middle)** — grid of icons, one per
  chart type. Click an icon to add that visual to the canvas. Below
  the icons are the **field wells** (Axis, Values, Legend, etc.) —
  drag fields here to populate the visual.
- **Data pane (right, bottom)** — your tables and fields. Drag from
  here onto visuals or canvas.

### Three things to know

1. **To add a visual:** click an empty area on the canvas, then click
   a chart icon in the Visualizations pane. A blank visual appears.
   Drag fields from the Data pane into the field wells.
2. **To format a visual:** click the visual to select it. In the
   Visualizations pane, click the **paint roller** icon (Format).
   You'll see all formatting options: title, colors, axes, etc.
3. **To save:** **File → Save** (or **Ctrl+S**). Pick a location and
   name (e.g. `Supply_Chain_Dashboard.pbix`). Save often.

---

## 4. Set up the base measures (one-time setup)

DAX measures are reusable formulas. Build them once, reference them
anywhere. We need 8 measures for this dashboard. **Do this before
building any visuals.**

### 4a. How to create a measure

1. In the **Data pane** (right side, bottom), right-click the
   **`supply_chain_flat`** table name.
2. From the menu, choose **New measure**.
3. The **formula bar** appears at the top of the canvas (just below
   the ribbon). It looks like an Excel formula bar.
4. Replace the placeholder text with your measure (name and formula).
5. Press **Enter** or click the **checkmark** at the left of the
   formula bar to commit.
6. The new measure appears under the table in the Data pane with a
   small **calculator icon** (different from regular fields, which
   show a small icon based on type).

> **Tip.** The formula bar autocompletes as you type. Press **Tab** to
> accept a suggestion. If you see red squiggly underline, there's a
> syntax error — hover for the explanation.

### 4b. Create these 8 measures, one at a time

For each one: right-click `supply_chain_flat` → **New measure** →
paste the entire block (the first line is the measure name, everything
after `=` is the formula) → press Enter.

**Measure 1 — Latest Week**

```dax
Latest Week = CALCULATE ( MAX ( supply_chain_flat[date] ), ALL ( supply_chain_flat ) )
```

This is the most recent date in the dataset, ignoring any filters. Used
as an anchor for "as of latest" measures.

**Measure 2 — Total Inventory Value**

```dax
Total Inventory Value = SUM ( supply_chain_flat[inventory_value] )
```

**Measure 3 — Inventory Value (Latest)**

```dax
Inventory Value (Latest) =
CALCULATE ( [Total Inventory Value], supply_chain_flat[date] = [Latest Week] )
```

**Measure 4 — Stockout Weeks**

```dax
Stockout Weeks =
CALCULATE ( COUNTROWS ( supply_chain_flat ), supply_chain_flat[backorder_qty] > 0 )
```

**Measure 5 — Active Stockouts**

```dax
Active Stockouts =
CALCULATE (
    DISTINCTCOUNT ( supply_chain_flat[part_id] ),
    supply_chain_flat[backorder_qty] > 0,
    supply_chain_flat[date] = [Latest Week]
)
```

**Measure 6 — Total Defects**

```dax
Total Defects = SUM ( supply_chain_flat[defects_l4w] )
```

**Measure 7 — Defect Rate**

```dax
Defect Rate =
DIVIDE ( [Total Defects], SUM ( supply_chain_flat[consumption_qty] ), 0 )
```

**Measure 8 — Critical at Risk**

```dax
Critical at Risk =
CALCULATE (
    DISTINCTCOUNT ( supply_chain_flat[part_id] ),
    supply_chain_flat[criticality_class] = "A",
    supply_chain_flat[backorder_qty] > 0,
    supply_chain_flat[date] = [Latest Week]
)
```

### 4c. Verify measures work

1. Click an empty area of the canvas.
2. In the Visualizations pane, click the **Card** icon (small icon
   that looks like `123` — usually in the 4th or 5th row).
3. A blank card appears on the canvas.
4. From the Data pane, drag **Inventory Value (Latest)** onto the
   blank card (drop it directly on the card, or onto the **Fields**
   well in the Visualizations pane).
5. The card should display a large number (around **$13.5 billion**).
6. If you see the number, measures are working. If you see "blank" or
   an error, double-check the measure formula above.
7. **Delete this test card** — click the card to select it, press
   **Delete** on your keyboard. We'll add the real cards in Page 1.

> **Reference for more measures.** [`DAX_measures.md`](DAX_measures.md)
> has 18 measures total. The 8 above are enough for this build; you can
> add more for advanced pages.

---

## 5. Page 1 — Executive Summary

The first page a VP / GM opens. KPIs at top, trend charts in the middle,
detail table at the bottom.

### 5a. Set up the page

1. The page at the bottom is named **Page 1** by default.
2. **Right-click** that tab → **Rename Page** → type **Executive
   Summary** → press Enter.
3. To control the page background color (optional, makes the dashboard
   look polished):
   - Click an empty area of the canvas.
   - In the Visualizations pane, click the **paint roller** icon at
     the top (Format).
   - Find **Page background** → expand → set color to a light grey
     (`#F5F5F5` works well).

### 5b. Add 4 KPI cards across the top

Each card displays a single big number. We'll add them one at a time.

#### Card 1 — Inventory Value (Latest)

1. **Click an empty area** of the canvas (so nothing else is
   selected). This is important — if a visual is selected, your
   click will target *that* visual instead of creating a new one.
2. In the **Visualizations pane**, click the **Card** icon (it's the
   simple `123` icon, not "Multi-row card", not "KPI"). Look for it
   in the lower rows of the Visualizations grid.
3. A blank card appears on the canvas. **Resize it** by dragging the
   corner handles to make it about a quarter of the page width.
   Drag it to the upper-left.
4. **From the Data pane**, click and drag the measure **Inventory
   Value (Latest)** onto the card. (Drag it onto the card directly,
   or into the "Fields" well in the Visualizations pane after
   selecting the card.)
5. The card now shows the inventory-value number. To format:
   - With card selected, click the **paint roller** (Format) icon.
   - Expand **Callout value** → set **Display units** to **Billions**
     and **Value decimal places** to 2. The card now shows
     "$13.55B" instead of "$13,550,835,083".
   - Expand **Title** → toggle on → type **"Inventory Value (latest
     week)"** in the Title text box.
   - Expand **Effects** → **Background** → set fill color to white;
     **Border** → toggle on, set color to light grey.

#### Card 2 — Active Stockouts

1. Click an empty area of the canvas.
2. Click the **Card** icon in Visualizations pane.
3. Drag the **Active Stockouts** measure onto the card.
4. Resize and position to the right of Card 1.
5. Format: **Title** → toggle on → "Active Stockouts (parts)".
6. **Callout value** → no display units (it's already a small whole
   number).

#### Card 3 — Total Defects

1. Repeat the steps above with the **Total Defects** measure.
2. Title: "Defects (4-week rolling, latest)".

#### Card 4 — Critical at Risk

1. Repeat with **Critical at Risk**.
2. Title: "Critical Parts at Risk".
3. **Optional polish:** with the card selected, **Format** →
   **Callout value** → **Color** → set conditional color so values >
   0 turn red. Click the **fx** button next to Color → "Format
   style: Field value" or "Rules": when value > 0, red.

### 5c. Add the weekly stockouts line chart

1. Click an empty area of the canvas (below the cards).
2. In Visualizations pane, click the **Line chart** icon (looks like a
   zigzag line).
3. A blank line chart appears. Resize it to about half the page width
   and place it on the left below the cards.
4. **Drag fields**:
   - Drag **`date`** from the Data pane into the **X-axis** well.
   - Drag the **Stockout Weeks** measure into the **Y-axis** well.
5. Power BI auto-aggregates `date` to a hierarchy (Year → Quarter →
   Month → Day). Click the **down-arrow** next to `date` in the
   X-axis well → choose **Date** instead of "Date Hierarchy". This
   makes the X-axis a continuous date instead of drilling levels.
6. Filter to recent weeks: in the **Filters pane** (right side, top),
   look for **Filters on this visual** at the top. Drag **`date`**
   from the Data pane into that section. Set **Filter type** to
   **Relative date**, **Show items when value is in the last 26
   weeks**.
7. Format: **Title** → "Weekly stockout count (last 26 weeks)".
   **Y-axis** → **Title** → "Part-weeks with backorder".
   **X-axis** → **Title** → "Week ending".

### 5d. Add the monthly defect bar chart

1. Click an empty area of the canvas (right of the line chart).
2. Click the **Stacked column chart** icon (third or fourth row of
   Visualizations, vertical bars stacked).
3. Drag **`date`** to the **X-axis** well. Click its dropdown arrow
   → choose **Date Hierarchy**. Then in the X-axis well, click the
   small **drill-down icon** (looks like 2 down arrows) until the
   level shows **Month**.
4. Drag the **Total Defects** measure to the **Y-axis** well.
5. Format: **Title** → "Monthly defect count". **X-axis** → format
   the date as "MMM YYYY" if needed via **X-axis** → **Type** →
   **Categorical**.

### 5e. Add the top-10 active stockouts table

1. Click an empty area below the two charts (the bottom half of the
   page).
2. Click the **Table** icon (looks like a small grid; in the lower
   rows of Visualizations).
3. Drag these fields into the **Columns** well, in this order:
   - `part_id`
   - `part_family`
   - `criticality_class`
   - `backorder_qty`
   - `pending_po_qty`
4. Add filters in the **Filters on this visual** section:
   - Drag `date` → set "Show items when value is" → **is** →
     pick the latest available date from the dropdown.
   - Drag `backorder_qty` → set "Show items when value is" →
     **greater than** → 0.
5. Sort the table: click the **`backorder_qty`** column header in
   the table itself — clicking once sorts ascending, twice
   descending. Set it to descending.
6. Limit to top 10: in the Filters pane, on the visual filters,
   click `backorder_qty` → change filter type to **Top N** →
   **Top 10** → **By value** → drop `backorder_qty` into the "By
   value" slot.
7. Format: **Title** → "Top 10 active stockouts (latest week)".
   **Style preset** → **Bold header** for readability.

> **You're done with Page 1.** Save your file (**Ctrl+S**) before
> moving on. If you haven't yet, save as
> `Supply_Chain_Dashboard.pbix` in the project folder.

---

## 6. Page 2 — Inventory Health

Materials manager's daily view: where is inventory thinning?

### 6a. Add the page and a Days-of-Supply measure

1. At the bottom, click the **+** to add a new page. Right-click the
   new tab → **Rename** → **Inventory Health**.
2. We need a **Days of Supply** measure. Right-click `supply_chain_flat`
   → **New measure**:

```dax
Avg Consumption L4W =
VAR _latest = [Latest Week]
RETURN
    CALCULATE (
        AVERAGE ( supply_chain_flat[consumption_qty] ),
        DATESINPERIOD ( supply_chain_flat[date], _latest, -4, WEEK )
    )
```

3. Then add another measure:

```dax
Days of Supply =
DIVIDE (
    AVERAGE ( supply_chain_flat[on_hand_qty] ),
    [Avg Consumption L4W],
    BLANK ()
) * 7
```

### 6b. Build the heat-map matrix (rows = part family, cols = criticality)

1. Click an empty area of the canvas.
2. In Visualizations pane, click the **Matrix** icon (looks like a
   grid with a header row, distinct from "Table"). Resize to about
   half the page width.
3. Drag the fields:
   - **`part_family`** → **Rows** well.
   - **`criticality_class`** → **Columns** well.
   - **`Days of Supply`** measure → **Values** well.
4. Now the conditional-formatting (the heat map):
   - With matrix selected, click the **paint roller** (Format).
   - Find **Cell elements** in the format options.
   - In the dropdown labelled **Apply to values**, choose **Days of
     Supply** (only one option since it's the only Values field).
   - Toggle **Background color** → **On**.
   - Click **fx** (advanced controls) just to the right.
   - In the dialog: **Format style** = **Gradient**.
   - **Minimum** color = **red**, **Maximum** = **green**.
   - Toggle **Diverging** → **On** if you want a middle colour;
     otherwise leave off.
   - **IMPORTANT**: low days-of-supply is *bad*, so we want low
     values to appear red, high to appear green. The defaults
     usually do this; if you see green-for-low, swap the colours.
   - Click **OK**.
5. The matrix now shows colored cells — green = healthy inventory
   coverage, red = at risk.
6. Format the matrix title: **Title** → "Days of Supply by Family
   × Criticality (lower = at risk)".

### 6c. Add a stockout-rate-by-family bar chart

1. Click an empty area to the right of the matrix.
2. Click the **Stacked bar chart** icon (horizontal bars).
3. Drag **`part_family`** → **Y-axis** well.
4. Drag **Stockout Weeks** measure → **X-axis** well.
5. Sort: hover over the visual, click the **three-dot menu (...)** in
   the top-right of the visual → **Sort by** → **Stockout Weeks**.
   Then **Sort descending**.
6. Format: **Title** → "Stockout part-weeks by family".

### 6d. Add a forecast-vs-actual line chart at the bottom

1. Click an empty area at the bottom of the page.
2. Click the **Line chart** icon.
3. Drag **`date`** → **X-axis**. Set to **Date** (not Date Hierarchy)
   like before.
4. Drag **`forecast_qty`** to **Y-axis**. By default it sums.
5. Drag **`consumption_qty`** to **Y-axis** as a second field.
6. Power BI shows both as lines. Format the legend so it's clearly
   labeled: **Title** → "Forecast vs Actual Consumption".
7. Filter to last 52 weeks via **Filters on this visual** with
   **Relative date** = **last 52 weeks**.

### 6e. Add the parts-at-risk table

1. Click an empty area of the canvas (use the remaining space).
2. Click **Table** icon.
3. Drag these columns into the table:
   - `part_id`
   - `criticality_class`
   - `on_hand_qty`
   - `Days of Supply` (your new measure)
   - `pending_po_qty`
   - `lead_time_days`
4. **Filters on this visual**:
   - Drag `date` → "is on or after" → 8 weeks ago (or just "latest week").
   - Drag `Days of Supply` → "less than" → 14.
5. Sort by `Days of Supply` ascending (the most at-risk parts at top).
6. Format: **Title** → "Parts at risk: Days of Supply < 14".

Save (**Ctrl+S**) and move on.

---

## 7. Page 3 — Supplier Performance

Procurement's view: which suppliers are missing PO due dates?

### 7a. Add the page

Click **+** at bottom → rename to **Supplier Performance**.

### 7b. Defects per supplier (bar chart)

1. Click empty canvas.
2. **Stacked bar chart** icon.
3. Drag `supplier_id_primary` → **Y-axis**.
4. Drag **Total Defects** measure → **X-axis**.
5. Sort by Total Defects descending (three-dot menu → Sort by → Total
   Defects → Descending).
6. Title: "Defects per supplier".
7. Optionally: filter to top 10 worst — Filters → Top N → 10 → By
   Total Defects.

### 7c. High-risk supplier $ exposure (table)

1. Click empty canvas.
2. **Table** icon.
3. Drag fields:
   - `supplier_id_primary`
   - `supplier_risk_class`
   - **Inventory Value (Latest)** measure
   - **Active Stockouts** measure
   - **Total Defects** measure
4. **Filters on this visual** → drag `supplier_risk_class` → set to
   **High** only.
5. Title: "High-risk suppliers — \$ exposure and active issues".

### 7d. Lead time distribution (column chart)

1. Click empty canvas.
2. **Clustered column chart** icon.
3. Drag `supplier_id_primary` → **X-axis**.
4. Drag `lead_time_days` → **Y-axis** — change aggregation to
   **Average** (click the dropdown next to the field in the Y-axis
   well → **Average**).
5. Sort by average lead time descending.
6. Title: "Avg baseline lead time per supplier (days)".

Save.

---

## 8. Page 4 — Quality

Defect concentration and Pareto.

### 8a. Add the page

Click **+** at bottom → rename to **Quality**.

### 8b. Defects 13-week trend (line)

1. Click empty canvas.
2. **Line chart** icon.
3. `date` → X-axis (Date, not Hierarchy).
4. **Total Defects** → Y-axis.
5. Filter to last 13 weeks via Relative date filter.
6. Title: "Defect trend (last 13 weeks)".

### 8c. Defects by criticality class (bar)

1. Click empty canvas.
2. **Stacked column chart** icon.
3. `criticality_class` → X-axis.
4. **Total Defects** → Y-axis.
5. Title: "Total defects by criticality class".

### 8d. Pareto chart — top 20 defective parts

The Pareto chart is bar (per-part defects) + line (cumulative %).
Power BI doesn't have a native Pareto visual, but you can fake it
with a **Line and stacked column chart**.

1. First create a measure: right-click table → New measure:

```dax
Cumulative Defects % =
VAR _curr_part = SELECTEDVALUE ( supply_chain_flat[part_id] )
VAR _curr_def =
    CALCULATE ( [Total Defects], supply_chain_flat[part_id] = _curr_part )
VAR _ranked =
    ADDCOLUMNS (
        ALL ( supply_chain_flat[part_id] ),
        "@def", CALCULATE ( [Total Defects] )
    )
VAR _bigger_or_equal =
    SUMX ( FILTER ( _ranked, [@def] >= _curr_def ), [@def] )
VAR _total = SUMX ( _ranked, [@def] )
RETURN
    DIVIDE ( _bigger_or_equal, _total )
```

This gives you the cumulative share of defects accounted for by each
part and all higher-defect parts.

2. Click empty canvas.
3. **Line and stacked column chart** icon.
4. Drag `part_id` → **X-axis**.
5. Drag **Total Defects** → **Column y-axis** (the bars).
6. Drag **Cumulative Defects %** → **Line y-axis** (the line).
7. Sort by **Total Defects** descending. Filter to **Top 20** parts.
8. Format the line y-axis as percentage. Add reference line at 80%
   to show where the Pareto cutoff falls.
9. Title: "Defect Pareto — top 20 parts".

Save.

---

## 9. Page 5 — Risk Watch

What needs intervention this week?

### 9a. Add the page

Click **+** at bottom → rename to **Risk Watch**.

### 9b. Big-number card — Critical at Risk

1. Click empty canvas.
2. **Card** icon.
3. Drag **Critical at Risk** measure to the card.
4. Make it large (top of page, full-width).
5. Format → **Callout value** → set color to red.
   Title: "CRITICAL PARTS AT RISK (Class A, latest week)".

### 9c. Composite Risk Score table

1. Create the measure first:

```dax
Risk Score =
VAR _crit_weight =
    SWITCH (
        SELECTEDVALUE ( supply_chain_flat[criticality_class] ),
        "A", 3,
        "B", 2,
        1
    )
VAR _stockout = IF ( SUM ( supply_chain_flat[backorder_qty] ) > 0, 2, 0 )
VAR _defects  = IF ( SUM ( supply_chain_flat[defects_l4w] ) > 0, 1, 0 )
VAR _supplier =
    IF ( SELECTEDVALUE ( supply_chain_flat[supplier_risk_class] ) = "High", 2, 0 )
RETURN _crit_weight + _stockout + _defects + _supplier
```

2. Click empty canvas.
3. **Table** icon.
4. Columns:
   - `part_id`
   - `criticality_class`
   - `supplier_risk_class`
   - **Risk Score** (measure)
   - `backorder_qty`
   - `pending_po_qty`
5. **Filters on this visual** → drag `date` → latest week only.
6. **Visual filters** → drag **Risk Score** → "is greater than or
   equal to" → 5.
7. Sort by **Risk Score** descending.
8. **Conditional formatting on Risk Score column:**
   - Select the table → **Format** (paint roller) → **Cell elements**.
   - In the **Apply to values** dropdown, choose **Risk Score**.
   - Toggle **Background color** → **On**.
   - Click **fx** → **Format style: Gradient** → Min = white, Max =
     red.
9. Title: "Risk Score ≥ 5 (latest week)".

### 9d. Action recommendations (text panel)

1. Click empty canvas.
2. In the ribbon, **Insert** tab → **Text box**.
3. Type:

```
Action playbook
- Risk Score >= 7 → Daily standup escalation; expedite freight.
- Risk Score 5-6  → Procurement to confirm PO status; review safety
                    stock.
- Score 3-4       → Watch list; review next sprint.
```

4. Format the text box font and add a coloured border for emphasis.

Save.

---

## 10. Cross-page filtering and drill-through

### 10a. Add a global date slicer (every page)

Slicers control filtering interactively. We'll add one to Page 1 and
copy to other pages.

1. Go to **Page 1 — Executive Summary**.
2. Click empty canvas (top right corner of page).
3. Click the **Slicer** icon in Visualizations.
4. Drag `date` → the slicer **Field** well.
5. By default it shows a date range. Click the small dropdown in the
   top-right of the slicer → choose **Relative**. Set default to
   **Last 12 weeks**.
6. To copy the slicer to every page: select it → **Ctrl+C** → go to
   each other page → **Ctrl+V**. Adjust position so it's in the
   same spot on every page.

### 10b. Add a site-filter slicer

Same as above but with `site_id` field. Place next to the date
slicer.

### 10c. Set up drill-through (advanced — optional)

Drill-through lets the user right-click a supplier in the Risk Watch
page and "drill through" to the Supplier Performance page filtered
to that supplier.

1. Go to **Page 3 — Supplier Performance**.
2. In the **Visualizations** pane, scroll down to **Drillthrough**
   field wells (below the chart wells).
3. Drag `supplier_id_primary` from the Data pane into the
   **Drillthrough** "Add drill-through fields here" slot.
4. Power BI auto-adds a "back" arrow in the top-left corner of this
   page.
5. Now go to **Page 5 — Risk Watch**. Right-click any row in the Risk
   Score table → **Drill through** → **Supplier Performance**. The
   Supplier Performance page opens, filtered to that part's supplier.

### 10d. Edit interactions (which visual filters which)

By default, clicking on one visual filters every other visual on the
same page. Sometimes you want some visuals to *not* be filtered.

1. Click any visual.
2. In the ribbon, go to the **Format** tab → **Edit interactions**.
3. Now clicking the visual shows small filter/none icons on every
   other visual. Click **None** on visuals that shouldn't be
   filtered.
4. Click **Edit interactions** again to exit edit mode.

---

## 11. Save and commit your `.pbix` file

1. **File → Save As** → name it `Supply_Chain_Dashboard.pbix`. Save
   it in your `Supply-Chain-Operations-Dashboard/` repo folder.
2. Close Power BI.
3. Open a terminal in the repo folder:

```bash
cd "d:/UWaterloo/Management Eng/GitHub_Portfolio/Supply-Chain-Operations-Dashboard"
git add Supply_Chain_Dashboard.pbix
git commit -m "Add Power BI dashboard build"
git push
```

> **Heads-up.** `.pbix` files are binary (a zipped collection of
> JSON/XML internally), so they can be a few MB. GitHub handles them
> fine. The repo's `.gitignore` already excludes `.pbix` by default
> for safety; if your `git add` fails, open `.gitignore` and remove
> the `*.pbix` line.

4. Open the repo on github.com and verify the file is there.

5. Optional polish: take a screenshot of each page (Win+Shift+S),
   save them as PNGs in the repo, and reference them from the README
   so a recruiter can see the dashboard without opening Power BI.

---

## 12. Common gotchas

**Q: I dropped a field on a visual but nothing shows up.**
A: Check the field type. If you dropped a **text** field into a
**Y-axis** (which expects numbers), Power BI implicitly counts the
distinct values, which might not be what you want. Click the
field's dropdown in the field well → choose the right aggregation
(or convert the field type).

**Q: My measure shows BLANK when I expect a number.**
A: 90% of the time it's a **filter context** issue. If you wrap the
measure in `CALCULATE(..., supply_chain_flat[date] = [Latest
Week])`, but the visual is also filtered to a different date, you
get blank. Either (a) remove the date filter from the visual, or
(b) use `ALL()` to clear context: `CALCULATE([X], ALL(supply_chain_flat[date]),
supply_chain_flat[date] = [Latest Week])`.

**Q: My date X-axis shows a weird hierarchy with year/quarter/month
levels.**
A: In the field well, click the dropdown next to `date` → choose
**Date** instead of **Date Hierarchy**.

**Q: My conditional formatting is reversed (red for high, green for
low).**
A: In the conditional formatting dialog (paint roller → Cell
elements → fx), swap the **Minimum** and **Maximum** colours.

**Q: My visual is empty even though I dropped fields.**
A: Look at the **Filters pane**. There may be a filter from a
previous step that's eliminating all rows. Click each filter and
check its scope.

**Q: Power BI is slow when refreshing.**
A: The 30 MB CSV imports in ~10 seconds. If it's slower, you might
have inadvertently created a calculated column instead of a measure
(calculated columns multiply data size). Right-click your custom
field — if it shows "Calculated column", delete it and re-create it
as a measure.

**Q: How do I undo a mistake?**
A: **Ctrl+Z** like everywhere else. Power BI's undo history is
deep — you can undo dozens of steps.

**Q: The matrix shows numbers in the cells when I want a heat-map
look.**
A: That's the default. Heat-map look comes from the conditional
formatting (background colour gradient) — it doesn't replace the
numbers. If you want to **hide** the numbers and show only colour,
you can shrink the column width and reduce the value font size — but
most ops dashboards keep both visible.

**Q: I want to add a new measure but right-clicking the table doesn't
show "New measure".**
A: Make sure you're right-clicking the **table name itself** in the
Data pane (not a field below it, not a measure under it). The table
name is at the top of the dropdown, with a small icon next to it.

---

## Tableau equivalents

If you're using Tableau Public instead of Power BI, the **structure of
each page is identical** — same visuals, same field placements. The
calculations differ in syntax. See
[`Tableau_calc_fields.md`](Tableau_calc_fields.md) for the Tableau
equivalents of every DAX measure used here.

The high-level mapping:

| Power BI | Tableau |
|---|---|
| Card visual | Big-number sheet (drag a measure to Text mark) |
| Matrix | Crosstab (rows + columns shelves + Marks pane) |
| Slicer | Filter (drag field to Filters → "Show Filter") |
| `CALCULATE` with filter | `{ FIXED dim : aggregation }` LOD |
| Stacked column | Bars mark (column) |
| Line chart | Line mark |
| Drill-through | Action → Filter (Dashboard menu) |
