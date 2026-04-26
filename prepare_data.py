"""Flatten the four-table supply-chain dataset into one BI-ready CSV.

Joins:
  - supply_chain_history.csv (the fact table — one row per part-week)
  - parts_master.csv          (dimension — adds family, criticality, cost, supplier)
  - purchase_orders.csv       (computes pending_po_qty as-of each week)
  - quality_incidents.csv     (computes defects_l4w as-of each week)

Output: supply_chain_flat.csv — one row per (date, site_id, part_id) with
all the dimensions and a few pre-computed numeric measures (inventory_value,
pending_po_qty, defects_l4w). The rest is left for the BI tool to compute
as DAX measures or Tableau calculated fields — see DAX_measures.md and
Tableau_calc_fields.md.

Source CSVs are read from a sibling repo on disk; if you don't have them,
adjust SOURCE_DIR or copy them into ./source_data/.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

SOURCE_DIR = Path("../Supplier-Risk-Lead-Time-Predictor")
LOCAL_SOURCE_DIR = Path("source_data")
OUT_PATH = Path("supply_chain_flat.csv")


def find_source_dir() -> Path:
    for p in (SOURCE_DIR, LOCAL_SOURCE_DIR):
        if (p / "supply_chain_history.csv").exists():
            return p
    raise FileNotFoundError(
        "Could not find source CSVs. Place them in ../Supplier-Risk-Lead-Time-Predictor/ "
        "or in ./source_data/. Required files: parts_master.csv, supply_chain_history.csv, "
        "purchase_orders.csv, quality_incidents.csv."
    )


def main():
    src = find_source_dir()
    print(f"Reading source data from {src.resolve()}")

    parts = pd.read_csv(src / "parts_master.csv")
    history = pd.read_csv(src / "supply_chain_history.csv", parse_dates=["date"])
    pos = pd.read_csv(src / "purchase_orders.csv",
                      parse_dates=["order_date", "promised_date", "receipt_date"])
    qis = pd.read_csv(src / "quality_incidents.csv", parse_dates=["incident_date"])

    print(f"  history: {len(history):,} rows")
    print(f"  parts:   {len(parts):,} rows")
    print(f"  POs:     {len(pos):,} rows")
    print(f"  QIs:     {len(qis):,} rows")

    # ----------------------------------------------- join part dimension
    df = history.merge(
        parts[["part_id", "part_family", "criticality_class", "unit_cost",
               "lead_time_days", "supplier_id_primary", "supplier_risk_class",
               "is_repairable"]],
        on="part_id", how="left",
    )

    # Inventory value at each part-week.
    df["inventory_value"] = df["on_hand_qty"] * df["unit_cost"]

    # ----------------------------------------------- pending PO qty as-of each week
    # A PO is "pending" if it was placed but not yet received by the week's date.
    print("Computing pending_po_qty per (part-week)...")
    pending = pos.copy()
    # For each (part_id, site_id), sum ordered_qty for POs where order_date <= date
    # AND (receipt_date > date OR receipt_date IS NULL).
    pending = pending[["part_id", "site_id", "order_date", "receipt_date", "ordered_qty"]]

    # Strategy: for each unique date in history, compute pending_qty per (part, site).
    # Vectorised approach — merge on part-site and filter by date conditions.
    history_keys = df[["date", "part_id", "site_id"]].drop_duplicates()
    merged = history_keys.merge(pending, on=["part_id", "site_id"], how="left")
    mask = (merged["order_date"] <= merged["date"]) & (
        merged["receipt_date"].isna() | (merged["receipt_date"] > merged["date"])
    )
    pending_agg = (
        merged[mask]
        .groupby(["date", "part_id", "site_id"], as_index=False)["ordered_qty"]
        .sum()
        .rename(columns={"ordered_qty": "pending_po_qty"})
    )
    df = df.merge(pending_agg, on=["date", "part_id", "site_id"], how="left")
    df["pending_po_qty"] = df["pending_po_qty"].fillna(0).astype(int)

    # ----------------------------------------------- defects_l4w (last 4 weeks)
    print("Computing defects_l4w per (part-week)...")
    qi_per_part = qis.groupby(["part_id", "incident_date"]).size().reset_index(name="defects")

    # For each row in df, sum defects in [date - 28 days, date]
    # Vectorise with a per-part merge_asof-style approach.
    defects_per_partweek = []
    for part_id, group in df[["date", "part_id"]].drop_duplicates().groupby("part_id"):
        part_qi = qi_per_part[qi_per_part["part_id"] == part_id]
        if part_qi.empty:
            continue
        for _, row in group.iterrows():
            window_start = row["date"] - pd.Timedelta(days=28)
            count = part_qi[
                (part_qi["incident_date"] > window_start)
                & (part_qi["incident_date"] <= row["date"])
            ]["defects"].sum()
            if count > 0:
                defects_per_partweek.append({
                    "date": row["date"], "part_id": part_id,
                    "defects_l4w": int(count),
                })

    if defects_per_partweek:
        defects_df = pd.DataFrame(defects_per_partweek)
        df = df.merge(defects_df, on=["date", "part_id"], how="left")
    df["defects_l4w"] = df.get("defects_l4w", 0)
    df["defects_l4w"] = df["defects_l4w"].fillna(0).astype(int)

    # ----------------------------------------------- output
    keep = [
        "date", "site_id", "part_id", "part_family", "criticality_class",
        "supplier_id_primary", "supplier_risk_class", "is_repairable",
        "unit_cost", "lead_time_days",
        "on_hand_qty", "consumption_qty", "backorder_qty", "blocked_qty",
        "forecast_qty", "forecast_type", "forecast_uplift_pct",
        "planned_maintenance",
        "inventory_value", "pending_po_qty", "defects_l4w",
    ]
    df = df[keep].sort_values(["date", "site_id", "part_id"])
    df.to_csv(OUT_PATH, index=False)

    print(f"\nWrote {OUT_PATH}")
    print(f"  {len(df):,} rows")
    print(f"  Date range: {df.date.min().date()} → {df.date.max().date()}")
    print(f"  Sites: {df.site_id.nunique()}")
    print(f"  Parts: {df.part_id.nunique()}")
    print(f"  Total inventory value: ${df.inventory_value.sum():,.0f}")
    print(f"  Total stockout-weeks (backorder > 0): {(df.backorder_qty > 0).sum():,}")
    print(f"  File size: {OUT_PATH.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
