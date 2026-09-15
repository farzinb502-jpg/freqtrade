#!/usr/bin/env bash
# Start Freqtrade paper trading (dry-run only). Never live. No API keys required.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

CONFIG="${CONFIG:-user_data/config_dryrun_crypto.json}"
STRATEGY="${STRATEGY:-SampleStrategy}"
LOGFILE="${LOGFILE:-user_data/logs/dryrun.log}"
DB_URL="${DB_URL:-sqlite:///user_data/tradesv3.dryrun.sqlite}"
EXCHANGE="${EXCHANGE:-binanceus}"
PIDFILE="${PIDFILE:-user_data/logs/dryrun.pid}"

usage() {
  cat <<'EOF'
Paper / dry-run only. Will not place real orders. Will not use live API keys.

Usage:
  ./artifacts/run_dryrun_trade.sh              # foreground paper bot
  ./artifacts/run_dryrun_trade.sh --download   # optional: refresh public OHLCV, then start
  ./artifacts/run_dryrun_trade.sh --validate   # start briefly, confirm dry-run, then stop
  ./artifacts/run_dryrun_trade.sh --stop       # stop a background paper bot started by this script
  ./artifacts/run_dryrun_trade.sh --status     # show pid / recent log lines

Switch strategy (do not use live mode):
  STRATEGY=TrendFollowingEMA ./artifacts/run_dryrun_trade.sh

Env knobs:
  CONFIG     default user_data/config_dryrun_crypto.json
  STRATEGY   default SampleStrategy
  EXCHANGE   default binanceus  (set EXCHANGE=binance if .com is reachable)
  LOGFILE    default user_data/logs/dryrun.log
  DB_URL     default sqlite:///user_data/tradesv3.dryrun.sqlite
EOF
}

trade_cmd() {
  freqtrade trade \
    --dry-run \
    -c "$CONFIG" \
    --userdir user_data \
    -s "$STRATEGY" \
    --db-url "$DB_URL" \
    --logfile "$LOGFILE"
}

download_public_ohlcv() {
  echo "==> Optional public OHLCV refresh (not required for paper trading)"
  freqtrade download-data \
    -c "$CONFIG" \
    --exchange "$EXCHANGE" \
    --days 5 \
    -t 15m \
    --trading-mode spot
}

stop_background() {
  if [[ ! -f "$PIDFILE" ]]; then
    echo "No pid file at $PIDFILE"
    return 0
  fi
  pid="$(cat "$PIDFILE")"
  if kill -0 "$pid" 2>/dev/null; then
    echo "Stopping paper bot pid $pid"
    kill "$pid" || true
    sleep 1
    kill -0 "$pid" 2>/dev/null && kill -9 "$pid" || true
  else
    echo "Pid $pid is not running"
  fi
  rm -f "$PIDFILE"
}

status_background() {
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "Paper bot running pid=$(cat "$PIDFILE")"
  else
    echo "Paper bot is not running"
  fi
  if [[ -f "$LOGFILE" ]]; then
    echo "--- last 20 log lines ($LOGFILE) ---"
    tail -n 20 "$LOGFILE" || true
  fi
}

validate_start() {
  mkdir -p "$(dirname "$LOGFILE")"
  : > "$LOGFILE"
  echo "==> Sanity-check: start dry-run bot, wait for worker, then stop"
  set +e
  timeout 45s freqtrade trade \
    --dry-run \
    -c "$CONFIG" \
    --userdir user_data \
    -s "$STRATEGY" \
    --db-url "$DB_URL" \
    --logfile "$LOGFILE"
  rc=$?
  set -e
  # 124 = timeout sent SIGTERM after the bot was running. That is success.
  if [[ "$rc" -ne 0 && "$rc" -ne 124 ]]; then
    echo "Dry-run process exited with $rc before the validation timeout"
    tail -n 40 "$LOGFILE" || true
    exit "$rc"
  fi
  if grep -q "Dry run is enabled" "$LOGFILE" \
    && grep -q "Starting worker" "$LOGFILE" \
    && grep -q "running with dry_run enabled" "$LOGFILE"; then
    echo "OK: dry-run paper bot started (SampleStrategy/config as given), then was stopped."
    echo "    Confirmed: dry_run enabled, worker started, no live trading."
    exit 0
  fi
  echo "Validation failed: expected dry-run startup lines were missing"
  tail -n 80 "$LOGFILE" || true
  exit 1
}

mkdir -p user_data/logs artifacts/logs

case "${1:-}" in
  -h|--help) usage; exit 0 ;;
  --stop) stop_background; exit 0 ;;
  --status) status_background; exit 0 ;;
  --validate) validate_start ;;
  --download)
    download_public_ohlcv
    echo "==> Starting PAPER / DRY-RUN bot. Ctrl+C to stop. No real orders."
    trade_cmd
    ;;
  "")
    echo "==> Starting PAPER / DRY-RUN bot. Ctrl+C to stop. No real orders."
    echo "    config=$CONFIG strategy=$STRATEGY exchange(from config)=binanceus"
    trade_cmd
    ;;
  *)
    echo "Unknown argument: $1"
    usage
    exit 2
    ;;
esac
