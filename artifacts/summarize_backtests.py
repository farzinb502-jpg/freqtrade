#!/usr/bin/env python3
"""Extract a strategy × pair comparison table from Freqtrade backtest JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_meta(path: Path) -> dict:
    with path.open() as fh:
        return json.load(fh)


def pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.{digits}f}%"


def fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}f}"


def iter_strategy_payloads(meta: dict) -> list[tuple[str, dict]]:
    """Freqtrade wraps one or more strategy blobs under strategy / strategy_comparison."""
    rows: list[tuple[str, dict]] = []
    if "strategy" in meta and isinstance(meta["strategy"], dict):
        for name, payload in meta["strategy"].items():
            if isinstance(payload, dict) and "results_per_pair" in payload:
                rows.append((name, payload))
    return rows


def extract_rows(results_dir: Path) -> list[dict]:
    rows: list[dict] = []
    for meta_path in sorted(results_dir.glob("*.json")):
        if meta_path.name.endswith(".last_result.json") or meta_path.name == ".last_result.json":
            continue
        # Skip zip sidecars / config dumps if any
        try:
            meta = load_meta(meta_path)
        except json.JSONDecodeError:
            continue
        if not isinstance(meta, dict):
            continue
        notes = ""
        if "strategy" in meta:
            # notes live on each strategy payload too
            pass
        for strat_name, payload in iter_strategy_payloads(meta):
            notes = payload.get("notes") or meta.get("notes") or ""
            timerange = ""
            if payload.get("backtest_start") and payload.get("backtest_end"):
                timerange = f"{payload['backtest_start']} → {payload['backtest_end']}"
            timeframe = payload.get("timeframe") or ""
            for pair_row in payload.get("results_per_pair", []):
                key = pair_row.get("key")
                if not key or key == "TOTAL":
                    continue
                rows.append(
                    {
                        "source": meta_path.name,
                        "notes": notes,
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
            # Also keep the TOTAL line as an overall row
            for pair_row in payload.get("results_per_pair", []):
                if pair_row.get("key") == "TOTAL":
                    rows.append(
                        {
                            "source": meta_path.name,
                            "notes": notes,
                            "strategy": strat_name,
                            "pair": "TOTAL",
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
    lines = [f"### {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    ranked = sorted(
        rows,
        key=lambda r: (
            r["strategy"],
            1 if r["pair"] == "TOTAL" else 0,
            r["pair"],
        ),
    )
    for r in ranked:
        lines.append(
            "| "
            + " | ".join(
                [
                    r["strategy"],
                    r["pair"],
                    str(r["trades"]),
                    pct(r["winrate"]),
                    fmt(r["profit_total_pct"] / 100 if r["profit_total_pct"] is not None and abs(r["profit_total_pct"]) > 1 else (r["profit_total_pct"] or 0) / 100)
                    if False
                    else (f"{r['profit_total_pct']:.2f}%" if r["profit_total_pct"] is not None else "n/a"),
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
    args = parser.parse_args()
    results_dir = Path(args.results_dir)
    rows = extract_rows(results_dir)
    isolated = [r for r in rows if "isolated" in str(r.get("notes", "")).lower() and r["pair"] != "TOTAL"]
    combined = [r for r in rows if "combined" in str(r.get("notes", "")).lower()]
    # Fallback: if notes missing, dump everything
    chunks = ["# Backtest comparison tables", ""]
    if isolated:
        # Rank isolated pair rows by total profit desc for a ranked view
        ranked_iso = sorted(isolated, key=lambda r: (r.get("profit_total_abs") or 0), reverse=True)
        chunks.append(markdown_table(ranked_iso, "Isolated pair runs (max_open_trades=1), ranked by absolute profit"))
        chunks.append("")
    if combined:
        chunks.append(markdown_table(combined, "Combined 3-pair runs (max_open_trades=3)"))
        chunks.append("")
    if not isolated and not combined:
        chunks.append(markdown_table(rows, "All exported pair rows"))
    Path(args.out).write_text("\n".join(chunks), encoding="utf-8")
    print(f"Wrote {args.out} ({len(rows)} rows from {results_dir})")


if __name__ == "__main__":
    main()
