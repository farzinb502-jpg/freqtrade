# Freqtrade dry-run paper trading (BTC / ETH / SOL)

**PAPER ONLY. `dry_run: true`. No live trading. No real funds. No exchange API keys required.**

This is a simulated bot that reads **public** market data and pretends to trade. It will not place orders on the exchange. It is **not** a signal that SampleStrategy (or any strategy here) is profitable live.

Backtest reminder from `artifacts/REPORT.md` and `artifacts/TRENDRIDER_COMPARE.md`:

- Combined 15m book (91 days): SampleStrategy **+12%**, EMA trend **−3%**, Supertrend **−16%**, MACD **−19%**, TrendRider **−22%**.
- Buy-and-hold in the same window: BTC **+17%**, ETH **+43%**, SOL **+39%**.
- **SampleStrategy lagged buy-and-hold.** TrendRider lost to SampleStrategy on profit factor and expectancy (15m PF 0.64 vs 2.52; 1h native also lost). Dry-run paper trading will not magically fix that.

Do **not** set `"dry_run": false`. Do **not** paste live API keys into this config.

## Config to use

| File | Exchange | Why |
| --- | --- | --- |
| **`user_data/config_dryrun_crypto.json`** | **`binanceus`** | Same source as the research backtests. Binance.com (`api.binance.com`) returned HTTP 451 (geo-restricted) from this environment. |
| Copy | `artifacts/config_dryrun_crypto.json` | Identical snapshot committed next to this doc. |

Pairs: `BTC/USDT`, `ETH/USDT`, `SOL/USDT`. Stake currency USDT. Simulated wallet **1000 USDT**. Spot only.

If Binance.com is reachable on your network and you prefer it, change `"exchange": { "name": "binanceus"` to `"binance"` in the JSON (keep `dry_run: true` and empty `key` / `secret`). Then re-run. Do not add API keys.

## Timeframe knob

Paper trading uses **15m** to match the research.

The `freqtrade trade` CLI has **no** `-i/--timeframe` flag. Edit the config:

```json
"timeframe": "15m"
```

`SampleStrategy`’s file still says `timeframe = "5m"`; Freqtrade **overrides that from this config**. After changing the JSON, restart the bot.

## Default strategy

Default is **`SampleStrategy`** (the only combined-book backtest winner). That does **not** mean it beats holding BTC/ETH/SOL.

Set in the JSON:

```json
"strategy": "SampleStrategy"
```

Or override on the CLI (recommended when switching):

```bash
# still paper-only because of --dry-run
freqtrade trade --dry-run -c user_data/config_dryrun_crypto.json -s TrendFollowingEMA
freqtrade trade --dry-run -c user_data/config_dryrun_crypto.json -s MomentumMACD
freqtrade trade --dry-run -c user_data/config_dryrun_crypto.json -s SupertrendATR
```

```bash
STRATEGY=TrendFollowingEMA ./artifacts/run_dryrun_trade.sh
```

Available class names under `user_data/strategies/`: `SampleStrategy`, `TrendFollowingEMA`, `MomentumMACD`, `SupertrendATR`, `TrendRiderStrategy`.

**Do not switch the paper default to TrendRider.** Same 91-day / 0.10% fee book: it lost (−22% at 15m, −13% at native 1h) with profit factor well below 1. SampleStrategy stays the default because it was the only green combined book — not because it beats holding BTC/ETH/SOL. Full write-up: `artifacts/TRENDRIDER_COMPARE.md`.

If you only want to watch TrendRider’s simulated fills (still `--dry-run`, empty keys):

```bash
# optional research only — this strategy lost the compare
freqtrade trade --dry-run -c user_data/config_dryrun_crypto.json -s TrendRiderStrategy
```

Prefer `"timeframe": "1h"` in the JSON for that experiment (TrendRider’s native bar). Restart after editing. This is not a recommendation to paper-trade it as a candidate for live.

## Install (once)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Start paper trading

Always pass `--dry-run`. Empty exchange keys stay empty; Freqtrade also strips secrets when `--dry-run` is set.

```bash
source .venv/bin/activate

freqtrade trade \
  --dry-run \
  -c user_data/config_dryrun_crypto.json \
  --userdir user_data \
  -s SampleStrategy \
  --db-url sqlite:///user_data/tradesv3.dryrun.sqlite \
  --logfile user_data/logs/dryrun.log
```

Wrapper (same flags):

```bash
./artifacts/run_dryrun_trade.sh
```

Leave it running. On 15m candles it may sit idle between bars; that is normal. Ctrl+C stops it.

Historical `download-data` is **optional**. Dry-run fetches public OHLCV/tickers live. To refresh a few days of 15m history first:

```bash
./artifacts/run_dryrun_trade.sh --download
# or
freqtrade download-data -c user_data/config_dryrun_crypto.json --exchange binanceus --days 5 -t 15m --trading-mode spot
```

## Stop

- Foreground: **Ctrl+C**.
- If you started it in another terminal and have a pid file from a custom background job: `./artifacts/run_dryrun_trade.sh --stop` (only if `user_data/logs/dryrun.pid` exists).
- Otherwise find the process and send SIGTERM:

```bash
pgrep -af "freqtrade trade"
kill <pid>
```

Simulated trades persist in `user_data/tradesv3.dryrun.sqlite` (gitignored). Restarting continues that paper book unless you delete the sqlite file.

## View open trades and logs

Logs (default):

```bash
tail -f user_data/logs/dryrun.log
```

Look for:

- `Dry run is enabled`
- `Instance is running with dry_run enabled`
- `Starting worker`
- later: entries/exits tagged as simulated

Paper trades in the sqlite DB:

```bash
freqtrade show-trades \
  -c user_data/config_dryrun_crypto.json \
  --db-url sqlite:///user_data/tradesv3.dryrun.sqlite
```

Telegram, Discord, webhooks, and FreqUI / API server are **disabled** so this setup needs no tokens. Do not enable them unless you add your own secrets locally (never commit secrets). The API `password` / JWT fields in the JSON exist only because Freqtrade’s schema requires them when the `api_server` block is present; `"enabled": false` means they are unused.

## What this will not do

- It will not make you money.
- It will not match backtests tick-for-tick (live candles, slippage, downtime).
- It will not beat buy-and-hold just because SampleStrategy printed +12% in one bull window.
- It will not place or cancel real Binance orders.

Paper trading is for learning the Freqtrade loop (start, logs, simulated fills). It is not a go-live checklist.

## Agent sanity-check

In this environment the paper bot was started with `--dry-run` against Binance.US public data (empty keys), reached `state='RUNNING'` with timeframe 15m and SampleStrategy, subscribed to BTC/ETH/SOL 15m websockets, then was stopped. It does not stay running here; run it locally and leave it up.

```bash
LOGFILE=artifacts/logs/dryrun-sanity.log ./artifacts/run_dryrun_trade.sh --validate
```
