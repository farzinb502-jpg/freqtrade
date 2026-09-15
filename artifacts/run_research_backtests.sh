#!/usr/bin/env bash
# Reproduce BTC/ETH/SOL spot backtests (paper only; no live keys).
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
TIMEFRAME="${TIMEFRAME:-15m}"
STRATEGIES=(SampleStrategy TrendFollowingEMA MomentumMACD SupertrendATR)
PAIRS=("BTC/USDT" "ETH/USDT" "SOL/USDT")

mkdir -p "$OUT_DIR" artifacts/logs

echo "==> Downloading public OHLCV (spot USDT)"
# Binance.com is geo-restricted in some environments (HTTP 451).
# Prefer --exchange binance; this script defaults to binanceus as a public fallback.
EXCHANGE="${EXCHANGE:-binanceus}"
freqtrade download-data \
  -c "$CONFIG" \
  --exchange "$EXCHANGE" \
  --days 120 \
  -t 5m 15m \
  --trading-mode spot \
  | tee "artifacts/logs/download-data.log"

echo "==> Combined 3-pair comparison (${TIMEFRAME}, ${TIMERANGE})"
freqtrade backtesting \
  -c "$CONFIG" \
  --strategy-list "${STRATEGIES[@]}" \
  --timeframe "$TIMEFRAME" \
  --timerange "$TIMERANGE" \
  --export trades \
  --backtest-directory "$OUT_DIR" \
  --breakdown month \
  --cache none \
  --notes "combined BTC/ETH/SOL ${TIMEFRAME} ${TIMERANGE}" \
  | tee "artifacts/logs/backtest-combined-${TIMEFRAME}.log"

for pair in "${PAIRS[@]}"; do
  pair_tag="${pair//\//_}"
  echo "==> Isolated pair ${pair} (${TIMEFRAME}, ${TIMERANGE}, max_open_trades=1)"
  freqtrade backtesting \
    -c "$CONFIG" \
    --strategy-list "${STRATEGIES[@]}" \
    --timeframe "$TIMEFRAME" \
    --timerange "$TIMERANGE" \
    -p "$pair" \
    --max-open-trades 1 \
    --export trades \
    --backtest-directory "$OUT_DIR" \
    --cache none \
    --notes "isolated ${pair} ${TIMEFRAME} ${TIMERANGE}" \
    | tee "artifacts/logs/backtest-${pair_tag}-${TIMEFRAME}.log"
done

echo "==> Summarizing exported JSON"
python artifacts/summarize_backtests.py --results-dir "$OUT_DIR" --out artifacts/comparison_table.md
echo "Done. See artifacts/REPORT.md and artifacts/comparison_table.md"
