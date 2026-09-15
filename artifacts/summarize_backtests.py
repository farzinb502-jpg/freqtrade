#!/usr/bin/env python3
"""Extract strategy × pair comparison tables from Freqtrade backtest zip files."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from zipfile import ZipFile


def load_stats(path: Path) -> dict | None:
    with ZipFile(path) as zf:
        json_names = [
            n
            for n in zf.namelist()
            if n.endswith(".json") and "_config" not in n
        ]
        if not json_names:
            return None
        with zf.open(json_names[0]) as fh:
            return json.loads(fh.read().decode("utf-8"))


def pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def extract_rows(results_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(results_dir.glob("*.zip")):
        stats = load_stats(path)
        if not stats or "strategy" not in stats:
            continue
        for strat_name, payload in stats["strategy"].items():
            if not isinstance(payload, dict) or "results_per_pair" not in payload:
                continue
            pair_keys = [
                r.get("key")
                for r in payload["results_per_pair"]
                if r.get("key") and r.get("key") != "TOTAL"
            ]
            run_kind = "combined" if len(pair_keys) > 1 else "isolated"
            timeframe = payload.get("timeframe") or ""
            timerange = ""
            if payload.get("backtest_start") and payload.get("backtest_end"):
                timerange = f"{payload['backtest_start']} → {payload['backtest_end']}"
            for pair_row in payload["results_per_pair"]:
                key = pair_row.get("key")
                if not key:
                    continue
                rows.append(
                    {
                        "source": path.name,
                        "run_kind": run_kind,
                        "strategy": strat_name,
                        "pair": key,
                        "timeframe": timeframe,
                        "timerange": timerange,
                        "trades": pair_row.get("trades", 0),
                        "winrate": pair_row.get("winrate"),
                        "profit_total_pct": pair_row.get("profit_total_pct"),
                        "profit_total_abs": pair_row.get("profit_total_abs"),
                        "profit_factor": pair_row.get("profit_factor"),
                        "max_drawdown_account": pair_row.get("max_drawdown_account"),
                        "max_drawdown_abs": pair_row.get("max_drawdown_abs"),
                        "expectancy": pair_row.get("expectancy"),
                        "expectancy_ratio": pair_row.get("expectancy_ratio"),
                    }
                )
    return rows


def markdown_table(rows: list[dict], title: str) -> str:
    headers = [
        "Strategy",
        "Pair",
        "Trades",
        "Win rate",
        "Total profit %",
        "Total profit USDT",
        "Profit factor",
        "Max DD % (acct)",
        "Expectancy",
        "Expectancy ratio",
    ]
    lines = [
        f"### {title}",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    ranked = sorted(
        rows,
        key=lambda r: (
            -(r.get("profit_total_abs") or 0),
            r["strategy"],
            1 if r["pair"] == "TOTAL" else 0,
            r["pair"],
        ),
    )
    for r in ranked:
        profit_pct = r["profit_total_pct"]
        profit_pct_s = f"{profit_pct:.2f}%" if profit_pct is not None else "n/a"
        lines.append(
            "| "
            + " | ".join(
                [
                    r["strategy"],
                    r["pair"],
                    str(r["trades"]),
                    pct(r["winrate"]),
                    profit_pct_s,
                    fmt(r["profit_total_abs"]),
                    fmt(r["profit_factor"]),
                    pct(r["max_drawdown_account"]),
                    fmt(r["expectancy"], 4),
                    fmt(r["expectancy_ratio"], 4),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="artifacts/backtest_results")
    parser.add_argument("--out", default="artifacts/comparison_table.md")
    parser.add_argument("--csv", default="artifacts/comparison_table.csv")
    args = parser.parse_args()
    results_dir = Path(args.results_dir)
    rows = extract_rows(results_dir)

    iso_15 = [
        r
        for r in rows
        if r["run_kind"] == "isolated" and r["timeframe"] == "15m" and r["pair"] != "TOTAL"
    ]
    comb_15 = [r for r in rows if r["run_kind"] == "combined" and r["timeframe"] == "15m"]
    comb_5 = [r for r in rows if r["run_kind"] == "combined" and r["timeframe"] == "5m"]

    chunks = [
        "# Backtest comparison tables",
        "",
        "Starting wallet 1000 USDT. Spot only. Fees 0.10% per side (Binance.US worst-case tier).",
        "Timerange 2026-06-15 → 2026-09-14 unless noted. Isolated runs use `max_open_trades=1`.",
        "",
    ]
    if iso_15:
        chunks.append(
            markdown_table(
                iso_15,
                "15m isolated pair runs (strategy × pair), ranked by absolute profit",
            )
        )
        chunks.append("")
    if comb_15:
        chunks.append(
            markdown_table(
                comb_15,
                "15m combined 3-pair runs (max_open_trades=3)",
            )
        )
        chunks.append("")
    if comb_5:
        chunks.append(
            markdown_table(
                comb_5,
                "5m combined 3-pair runs (sensitivity; SampleStrategy native timeframe)",
            )
        )
        chunks.append("")

    Path(args.out).write_text("\n".join(chunks), encoding="utf-8")

    fieldnames = [
        "run_kind",
        "timeframe",
        "strategy",
        "pair",
        "trades",
        "winrate",
        "profit_total_pct",
        "profit_total_abs",
        "profit_factor",
        "max_drawdown_account",
        "max_drawdown_abs",
        "expectancy",
        "expectancy_ratio",
        "timerange",
        "source",
    ]
    with Path(args.csv).open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in sorted(
            rows,
            key=lambda r: (r["timeframe"], r["run_kind"], r["strategy"], r["pair"]),
        ):
            writer.writerow(row)
    print(f"Wrote {args.out} and {args.csv} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
