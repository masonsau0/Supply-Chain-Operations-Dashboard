# Tableau — Calculated Fields Reference

Tableau equivalents for the DAX measures in `DAX_measures.md`. Each
calculated field is created via **Analysis → Create Calculated Field**.
LOD (Level of Detail) expressions handle the same filter-context
manipulation that DAX uses `CALCULATE` for.

## Inventory & coverage

### Total Inventory Value

```
SUM([inventory_value])
```

### Inventory Value (Latest Week)

LOD expression — fixes to the most recent date in the dataset regardless
of view-level filters:

```
{ FIXED : SUM(IIF([date] = { MAX([date]) }, [inventory_value], 0)) }
```

### Avg Weekly Consumption (Trailing 4 Weeks)

Use a **table calculation** with a 4-week window:

```
WINDOW_AVG(SUM([consumption_qty]), -3, 0)
```

Then in **Analysis → Compute Using → Date** to make it a 4-week trailing
average.

### Days of Supply (per part)

Two-step approach. First a fixed LOD for current on-hand:

```
On Hand (Current) =
{ FIXED [part_id] :
    SUM(IIF([date] = { MAX([date]) }, [on_hand_qty], 0))
}
```

Then a fixed LOD for trailing-4-week average consumption:

```
Avg Consumption L4W =
{ FIXED [part_id] :
    AVG(IIF([date] >= { MAX([date]) } - 28, [consumption_qty], NULL))
}
```

Then the ratio:

```
Days of Supply =
([On Hand (Current)] / [Avg Consumption L4W]) * 7
```

## Stockouts

### Stockout Flag

```
IIF([backorder_qty] > 0, 1, 0)
```

### Stockout Weeks

```
SUM([Stockout Flag])
```

### Stockout Rate

```
SUM([Stockout Flag]) / COUNT([part_id])
```

### Active Stockouts (Distinct Parts in Latest Week)

```
{ FIXED :
    COUNTD(
        IIF([date] = { MAX([date]) } AND [backorder_qty] > 0, [part_id], NULL)
    )
}
```

## Trend / time intelligence

### Stockouts MoM

```
(SUM([Stockout Flag]) - LOOKUP(SUM([Stockout Flag]), -4))
/ LOOKUP(SUM([Stockout Flag]), -4)
```

(Use it on a view sorted by week.)

### 4-Week Rolling Avg Defects

```
WINDOW_AVG(SUM([defects_l4w]), -3, 0)
```

## Supplier metrics

### Supplier Defect Rate

```
SUM([defects_l4w]) / SUM([consumption_qty])
```

### High-Risk Supplier $

```
SUM(IIF([supplier_risk_class] = "High", [inventory_value], 0))
```

## Quality

### Total Defects

```
SUM([defects_l4w])
```

### Parts with Defects (Distinct Count)

```
COUNTD(IIF([defects_l4w] > 0, [part_id], NULL))
```

## Risk watch

### Critical Parts at Risk

```
{ FIXED :
    COUNTD(
        IIF(
            [criticality_class] = "A"
            AND [date] = { MAX([date]) }
            AND [backorder_qty] > 0,
            [part_id], NULL
        )
    )
}
```

### Risk Score (Composite)

```
(CASE [criticality_class]
    WHEN "A" THEN 3
    WHEN "B" THEN 2
    ELSE 1
 END)
+ IIF(SUM([backorder_qty]) > 0, 2, 0)
+ IIF(SUM([defects_l4w]) > 0, 1, 0)
+ IIF([supplier_risk_class] = "High", 2, 0)
```

Drop this on a part-list table coloured by **Risk Score** for the Risk
Watch page.

## Tableau-specific tips

- **Date filter** — drag `date` to Filters → choose **Relative Date** →
  set the default to "last 12 weeks" so dashboards open on a recent
  window.
- **Set actions** for cross-page drilling (e.g. click a supplier on the
  Supplier Performance page, see only their parts on Quality and Risk
  Watch).
- **Parameter** — create a `Top N` integer parameter (default 10) and
  use `RANK_DENSE(SUM([backorder_qty]))` plus a top-N filter for the
  "Top 10 stockouts" panel on page 2.
- **Dual-axis** — combine `SUM([inventory_value])` (bars) and
  `SUM([Stockout Flag])` (line) on the same time axis for the Inventory
  Health trend.
- **Alerts** (Tableau Server / Cloud only) — set a threshold alert on
  `Critical Parts at Risk > 0` so the operations team gets paged when a
  Class-A part stocks out.
