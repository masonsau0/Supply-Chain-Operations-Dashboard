# Power BI — DAX Measures Reference

All measures below assume the flat table has been loaded as `supply_chain`.
Copy-paste each into a new measure (right-click the table → New measure).

## Inventory & coverage

### M01 — Total Inventory Value

```dax
Total Inventory Value =
SUM ( supply_chain[inventory_value] )
```

### M02 — Avg Inventory Value per Part-Week

```dax
Avg Inventory Value =
AVERAGE ( supply_chain[inventory_value] )
```

### M03 — Latest Week Snapshot

```dax
Latest Week =
CALCULATE (
    MAX ( supply_chain[date] ),
    ALL ( supply_chain )
)
```

### M04 — Inventory Value (Latest Week)

```dax
Inventory Value (Latest) =
CALCULATE (
    [Total Inventory Value],
    supply_chain[date] = [Latest Week]
)
```

### M05 — Avg Weekly Consumption (Trailing 4 Weeks)

```dax
Avg Consumption L4W =
VAR _latest = [Latest Week]
RETURN
    CALCULATE (
        AVERAGE ( supply_chain[consumption_qty] ),
        DATESINPERIOD ( supply_chain[date], _latest, -4, WEEK )
    )
```

### M06 — Days of Supply (Per Part)

```dax
Days of Supply =
DIVIDE (
    SUM ( supply_chain[on_hand_qty] ),
    [Avg Consumption L4W] * SUM ( supply_chain[on_hand_qty] ) / SUM ( supply_chain[on_hand_qty] ),
    BLANK ()
) * 7
```

> Note: simplified version — `(on_hand / avg_weekly_consumption) × 7`. In a
> real model you'd want this per part, not aggregated.

## Stockouts

### M07 — Stockout Weeks

```dax
Stockout Weeks =
CALCULATE (
    COUNTROWS ( supply_chain ),
    supply_chain[backorder_qty] > 0
)
```

### M08 — Stockout Rate

```dax
Stockout Rate =
DIVIDE ( [Stockout Weeks], COUNTROWS ( supply_chain ), 0 )
```

### M09 — Active Stockouts (Latest Week)

```dax
Active Stockouts =
CALCULATE (
    DISTINCTCOUNT ( supply_chain[part_id] ),
    supply_chain[backorder_qty] > 0,
    supply_chain[date] = [Latest Week]
)
```

### M10 — Active Stockout Backorder Qty

```dax
Backorder Qty (Active) =
CALCULATE (
    SUM ( supply_chain[backorder_qty] ),
    supply_chain[date] = [Latest Week]
)
```

## Trend / time intelligence

### M11 — Stockouts vs 4 Weeks Ago

```dax
Stockouts MoM =
VAR _now = [Stockout Weeks]
VAR _prev =
    CALCULATE (
        [Stockout Weeks],
        DATEADD ( supply_chain[date], -4, WEEK )
    )
RETURN DIVIDE ( _now - _prev, _prev, BLANK () )
```

### M12 — 4-Week Rolling Avg Defects

```dax
Defects (4W Rolling) =
VAR _curr = MAX ( supply_chain[date] )
RETURN
    CALCULATE (
        AVERAGE ( supply_chain[defects_l4w] ),
        DATESINPERIOD ( supply_chain[date], _curr, -4, WEEK )
    )
```

## Supplier metrics

### M13 — Supplier Defect Rate

```dax
Supplier Defect Rate =
DIVIDE (
    SUM ( supply_chain[defects_l4w] ),
    SUM ( supply_chain[consumption_qty] ),
    0
)
```

### M14 — Inventory by Supplier Risk Class

```dax
High-Risk Supplier $ =
CALCULATE (
    [Total Inventory Value],
    supply_chain[supplier_risk_class] = "High"
)
```

## Quality

### M15 — Total Defects

```dax
Total Defects =
SUM ( supply_chain[defects_l4w] )
```

### M16 — Parts with Defects

```dax
Parts with Defects =
CALCULATE (
    DISTINCTCOUNT ( supply_chain[part_id] ),
    supply_chain[defects_l4w] > 0
)
```

## Risk watch

### M17 — Critical Parts at Risk

```dax
Critical at Risk =
CALCULATE (
    DISTINCTCOUNT ( supply_chain[part_id] ),
    supply_chain[criticality_class] = "A",
    supply_chain[backorder_qty] > 0,
    supply_chain[date] = [Latest Week]
)
```

### M18 — Risk Score (Composite Flag)

```dax
Risk Score =
VAR _crit_weight =
    SWITCH (
        TRUE (),
        SELECTEDVALUE ( supply_chain[criticality_class] ) = "A", 3,
        SELECTEDVALUE ( supply_chain[criticality_class] ) = "B", 2,
        1
    )
VAR _stockout = IF ( SUM ( supply_chain[backorder_qty] ) > 0, 2, 0 )
VAR _defects = IF ( SUM ( supply_chain[defects_l4w] ) > 0, 1, 0 )
VAR _supplier = IF ( SELECTEDVALUE ( supply_chain[supplier_risk_class] ) = "High", 2, 0 )
RETURN _crit_weight + _stockout + _defects + _supplier
```

## Conditional formatting tips

For the **Risk Watch** page, use measure-driven conditional formatting on
the part-list table:

1. Select the table → **Format** pane → **Cell elements** → toggle on
   **Background color** for the `Risk Score` column.
2. Choose **Format style: Gradient**, set min = 0 / max = 8, white →
   amber → red.
3. Apply identical formatting to **Backorder Qty (Active)** for visual
   consistency.

For the **Inventory Health** heat map (page 2):

1. Build a matrix with `part_family` on rows, `criticality_class` on
   columns, **Avg Days of Supply** as values.
2. **Format** → **Cell elements** → **Background color** → green for
   high values, red for low — invert the scale because *low* days of
   supply = bad.
