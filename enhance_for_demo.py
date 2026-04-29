"""Inject a realistic 'story' into the last 4 weeks of supply_chain_flat.csv
so the dashboard cards and tables have non-trivial values for an interview
demo. Original file is backed up to supply_chain_flat.csv.original on first
run; subsequent runs restore from the backup before re-applying, so the
script is idempotent.

Changes (latest week only, except where noted):
  - 4 Class A parts -> backorder (drives Critical at Risk = 4)
  - 5 Class B parts -> backorder (raises Active Stockouts to ~17)
  - 2 suppliers used by Class A parts -> promoted to High risk class
    (Page 3 high-risk supplier table goes from 1 row to 3)
  - Defects spread across ~12 parts over last 4 weeks (mix of A/B/C) so
    the criticality bar chart and Pareto have meaningful shape

After running: in Power BI, click Home -> Refresh.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

CSV = Path("supply_chain_flat.csv")
BACKUP = Path("supply_chain_flat.csv.original")


def main() -> None:
    if not BACKUP.exists():
        print(f"Creating backup: {BACKUP}")
        BACKUP.write_bytes(CSV.read_bytes())
    else:
        print(f"Backup exists -> restoring from {BACKUP} for clean re-apply")
        CSV.write_bytes(BACKUP.read_bytes())

    df = pd.read_csv(CSV, parse_dates=["date"])
    latest = df["date"].max()
    last4 = sorted(df[df["date"] > latest - pd.Timedelta(days=28)]["date"].unique())
    print(f"Latest week: {latest.date()}; injecting into {len(last4)} weeks")

    target_site = "SITE01"

    # --- 1. Pick Class A / B parts to backorder ----------------------------
    parts_a = sorted(df[df["criticality_class"] == "A"]["part_id"].unique())
    parts_b = sorted(df[df["criticality_class"] == "B"]["part_id"].unique())
    target_a = parts_a[:4]
    target_b = parts_b[:5]

    a_qtys = [12, 8, 5, 3]
    b_qtys = [15, 10, 7, 4, 2]

    for part, qty in zip(target_a + target_b, a_qtys + b_qtys):
        m = (df["part_id"] == part) & (df["date"] == latest) & (df["site_id"] == target_site)
        df.loc[m, "backorder_qty"] = qty
        df.loc[m, "on_hand_qty"] = 0
        df.loc[m, "inventory_value"] = 0.0

    print(f"Backordered Class A parts at {target_site}: {target_a}")
    print(f"Backordered Class B parts at {target_site}: {target_b}")

    # --- 2. Promote two suppliers used by Class A parts to High risk ------
    promote: list[str] = []
    for p in target_a:
        sup = df.loc[df["part_id"] == p, "supplier_id_primary"].iloc[0]
        if sup != "SUP033" and sup not in promote:
            promote.append(sup)
        if len(promote) == 2:
            break

    sup_mask = df["supplier_id_primary"].isin(promote)
    df.loc[sup_mask, "supplier_risk_class"] = "High"
    print(f"Promoted to High supplier risk: {promote} ({sup_mask.sum():,} rows)")

    # --- 3. Spread defects across last 4 weeks ----------------------------
    # Pick parts across all three classes so the criticality bar chart shows
    # a meaningful spread, with A leaning higher (the "story" is critical
    # parts driving quality issues).
    defect_plan = [
        # (part_id, week_offset_from_latest, defects_l4w)
        (target_a[0], 0, 6),
        (target_a[1], 0, 4),
        (target_a[2], 0, 3),
        (target_a[3], 0, 2),
        (target_a[0], 1, 4),
        (target_a[1], 1, 3),
        (target_b[0], 0, 5),
        (target_b[1], 0, 3),
        (target_b[2], 0, 2),
        (target_b[0], 2, 3),
        (parts_b[6], 0, 4),
        (parts_b[7], 1, 2),
        (parts_b[8], 0, 2),
    ]
    weeks_desc = sorted(last4, reverse=True)
    for part, offset, count in defect_plan:
        if offset >= len(weeks_desc):
            continue
        wk = weeks_desc[offset]
        m = (df["part_id"] == part) & (df["date"] == wk) & (df["site_id"] == target_site)
        df.loc[m, "defects_l4w"] = count

    # --- 4. Save and report ----------------------------------------------
    df.to_csv(CSV, index=False)

    last = df[df["date"] == latest]
    print("\n=== After enhancement (latest week) ===")
    print(f"Active stockouts (distinct parts): "
          f"{last[last['backorder_qty'] > 0]['part_id'].nunique()}")
    print(f"  by class: {last[last['backorder_qty'] > 0].groupby('criticality_class')['part_id'].nunique().to_dict()}")
    print(f"Critical at Risk (A in backorder): "
          f"{last[(last['backorder_qty'] > 0) & (last['criticality_class'] == 'A')]['part_id'].nunique()}")
    print(f"High-risk suppliers (distinct): "
          f"{df[df['supplier_risk_class'] == 'High']['supplier_id_primary'].nunique()}")
    print(f"Defects sum (latest week): {last['defects_l4w'].sum()}")
    print(f"Defects sum by class (latest week): "
          f"{last.groupby('criticality_class')['defects_l4w'].sum().to_dict()}")

    # Risk score check
    def risk(row: pd.Series) -> int:
        crit = {"A": 3, "B": 2}.get(row["criticality_class"], 1)
        so = 2 if row["backorder_qty"] > 0 else 0
        de = 1 if row["defects_l4w"] > 0 else 0
        sup = 2 if row["supplier_risk_class"] == "High" else 0
        return crit + so + de + sup

    last_scored = last.assign(risk=last.apply(risk, axis=1))
    print(f"Risk Score >= 7 rows: {(last_scored['risk'] >= 7).sum()}")
    print(f"Risk Score >= 5 rows: {(last_scored['risk'] >= 5).sum()}")


if __name__ == "__main__":
    main()
