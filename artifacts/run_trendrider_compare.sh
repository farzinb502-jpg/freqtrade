#!/usr/bin/env bash
# Compare TrendRiderStrategy vs SampleStrategy on the research BTC/ETH/SOL book.
# Paper / backtest only. No live keys.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

CONFIG="user_data/research_spot_usdt.json"
OUT_DIR="artifacts/backtest_results"
TIMERANGE="${TIMERANGE:-20260615-20260914}"
EXCHANGE="${EXCHANGE:-binanceus}"
# Match prior research: Freqtrade worst-case Binance.US tier (0.10% per side).
FEE="${FEE:-0.001}"
# Daily EMA200 needs ~200 completed 1d candles before the timerange start.
DOWNLOAD_DAYS="${DOWNLOAD_DAYS:-400}"

mkdir -p "$OUT_DIR" artifacts/logs

echo "==> Download public OHLCV for TrendRider MTF (1h/4h/1d) + 15m apples-to-apples"
freqtrade download-data \
  -c "$CONFIG" \
  --exchange "$EXCHANGE" \
  --days "$DOWNLOAD_DAYS" \
  -t 15m 1h 4h 1d \
  --trading-mode spot \
  | tee "artifacts/logs/download-data-trendrider.log"

echo "==> Combined 15m, no protections (same window/fees as prior SampleStrategy table)"
freqtrade backtesting \
  -c "$CONFIG" \
  --strategy-list SampleStrategy TrendRiderStrategy \
  --timeframe 15m \
  --timerange "$TIMERANGE" \
  --fee "$FEE" \
  --export trades \
  --backtest-directory "$OUT_DIR" \
  --breakdown month \
  --cache none \
  --notes "trendrider-vs-sample combined 15m ${TIMERANGE} fee=${FEE}" \
  | tee "artifacts/logs/backtest-trendrider-vs-sample-15m.log"

echo "==> Combined 15m TrendRider with --enable-protections (strategy-defined Cooldown/SL guard/MaxDD)"
freqtrade backtesting \
  -c "$CONFIG" \
  --strategy-list TrendRiderStrategy \
  --timeframe 15m \
  --timerange "$TIMERANGE" \
  --fee "$FEE" \
  --enable-protections \
  --export trades \
  --backtest-directory "$OUT_DIR" \
  --cache none \
  --notes "trendrider 15m protections ${TIMERANGE} fee=${FEE}" \
  | tee "artifacts/logs/backtest-trendrider-15m-protections.log"

echo "==> Combined 1h native TrendRider vs SampleStrategy (TrendRider file timeframe is 1h)"
freqtrade backtesting \
  -c "$CONFIG" \
  --strategy-list SampleStrategy TrendRiderStrategy \
  --timeframe 1h \
  --timerange "$TIMERANGE" \
  --fee "$FEE" \
  --enable-protections \
  --export trades \
  --backtest-directory "$OUT_DIR" \
  --cache none \
  --notes "trendrider-vs-sample combined 1h protections ${TIMERANGE} fee=${FEE}" \
  | tee "artifacts/logs/backtest-trendrider-vs-sample-1h.log"

echo "==> Isolated 15m pair books (max_open_trades=1), no protections"
PAIRS=("BTC/USDT" "ETH/USDT" "SOL/USDT")
for pair in "${PAIRS[@]}"; do
  pair_tag="${pair//\//_}"
  freqtrade backtesting \
    -c "$CONFIG" \
    --strategy-list SampleStrategy TrendRiderStrategy \
    --timeframe 15m \
    --timerange "$TIMERANGE" \
    --fee "$FEE" \
    -p "$pair" \
    --max-open-trades 1 \
    --export trades \
    --backtest-directory "$OUT_DIR" \
    --cache none \
    --notes "isolated ${pair} 15m trendrider-vs-sample ${TIMERANGE}" \
    | tee "artifacts/logs/backtest-trendrider-${pair_tag}-15m.log"
done

echo "==> Isolated 1h pair books with protections"
for pair in "${PAIRS[@]}"; do
  pair_tag="${pair//\//_}"
  freqtrade backtesting \
    -c "$CONFIG" \
    --strategy-list SampleStrategy TrendRiderStrategy \
    --timeframe 1h \
    --timerange "$TIMERANGE" \
    --fee "$FEE" \
    --enable-protections \
    -p "$pair" \
    --max-open-trades 1 \
    --export trades \
    --backtest-directory "$OUT_DIR" \
    --cache none \
    --notes "isolated ${pair} 1h trendrider-vs-sample ${TIMERANGE}" \
    | tee "artifacts/logs/backtest-trendrider-${pair_tag}-1h.log"
done

echo "Done. Summarize with: python artifacts/summarize_backtests.py"
echo "Write-up: artifacts/TRENDRIDER_COMPARE.md"
