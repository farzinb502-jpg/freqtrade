# Freqtrade paper research: BTC / ETH / SOL (USDT spot)

**Paper / backtest / dry-run only. No live trading. No real exchange keys. Do not spend funds based on this report.**

This fork was used as a **framework evaluation**, not a rewrite of Freqtrade. Classic mean-reversion / ORB strategies already lost money on these pairs in a prior ~30-day bake-off. This run asks a narrower question: can Freqtrade be installed, fed public data, and used to backtest a mix of sample + trend/momentum strategies on high-volume USDT markets — and what do the numbers actually say?

**Bottom line:** the framework works. The strategies mostly do not. Over 91 days of 15m candles, three of four strategies lost money after 0.10% fees. The one winner (`SampleStrategy`, +12% combined) **lagged buy-and-hold** on a strongly rising market (BTC +17%, ETH +43%, SOL +39%) and still lost on SOL. This is not evidence of a day-trading edge.

## What was tested

| Item | Value |
| --- | --- |
| Exchange data | Binance.US public OHLCV (spot). Binance.com returned HTTP 451 (geo-restricted) from this environment. |
| Pairs | `BTC/USDT`, `ETH/USDT`, `SOL/USDT` |
| Primary timeframe | **15m** |
| Sensitivity timeframe | 5m (SampleStrategy’s native setting) |
| Timerange | `2026-06-15` → `2026-09-14` (91 days) |
| Downloaded history | 2026-05-18 → 2026-09-15 (~120 days of 5m + 15m, including startup candles) |
| Starting wallet | 1000 USDT |
| Stake | `unlimited` (split across `max_open_trades`) |
| Combined book | `max_open_trades=3` |
| Isolated book | one pair at a time, `max_open_trades=1` |
| Fee | 0.10% per side (Freqtrade’s worst-case Binance.US tier) |
| Trading mode | spot, long-only, `dry_run: true` |

Buy-and-hold over the same 15m window (close-to-close, no fees):

| Pair | First close | Last close | Buy-and-hold |
| --- | --- | --- | --- |
| BTC/USDT | 65,873.58 | 76,827.78 | **+16.63%** |
| ETH/USDT | 1,731.34 | 2,477.16 | **+43.08%** |
| SOL/USDT | 71.69 | 99.29 | **+38.50%** |

Equal-weight average ≈ **+32.7%** (Freqtrade reported market change **+33.11%** on the combined run). Any strategy that made ~12% in this window was **behind sitting in the coins**.

## Strategies

None of these were hyperopted. Parameters are textbook defaults. Core Freqtrade code was not changed.

| Strategy | File | Style | Notes |
| --- | --- | --- | --- |
| `SampleStrategy` | `user_data/strategies/sample_strategy.py` | Official sample (RSI + TEMA + Bollinger) | Tight ROI (`1%` / `2%` / `4%`), `-10%` stoploss. High win rate from clipping small ROI in an uptrend. |
| `TrendFollowingEMA` | `user_data/strategies/trend_following_ema.py` | Trend | EMA 20/50 crossover with ADX > 20. |
| `MomentumMACD` | `user_data/strategies/momentum_macd.py` | Momentum | MACD signal cross, close > EMA 50, RSI > 50. |
| `SupertrendATR` | `user_data/strategies/supertrend_atr.py` | Trend | pandas-ta Supertrend (ATR 10, multiplier 3). |

Config: `user_data/research_spot_usdt.json` (copy at `artifacts/research_spot_usdt.json`). Exchange `key` / `secret` are empty strings. Telegram and the API server are disabled.

## Ranked results — 15m combined (the realistic book)

Capital shared across the three pairs, `max_open_trades=3`, start 1000 USDT.

| Rank | Strategy | Trades | Win rate | Total profit | Profit factor | Max DD (acct) | Expectancy (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | SampleStrategy | 61 | 93.4% | **+119.73 USDT (+11.97%)** | **2.52** | 3.26% | 1.96 (0.10) |
| 2 | TrendFollowingEMA | 101 | 16.8% | **-33.66 USDT (−3.37%)** | 0.87 | 7.58% | −0.33 (−0.10) |
| 3 | SupertrendATR | 460 | 28.9% | **-161.25 USDT (−16.12%)** | 0.78 | 22.36% | −0.35 (−0.16) |
| 4 | MomentumMACD | 600 | 25.2% | **-191.96 USDT (−19.20%)** | 0.71 | 24.92% | −0.32 (−0.22) |

`SampleStrategy` is the only combined-book winner. That win is not a day-trading edge:

- Almost every winner exited on the **1% ROI timer**, not a trend capture.
- Two SOL stoplosses at **−10%** wiped a large chunk of the clipped wins.
- Combined SOL still finished **−0.70%**.
- +12% vs buy-and-hold ~+33% is an opportunity cost, not a strategy to fund.

Trend/momentum strategies lost the way the earlier mean-reversion/ORB bake-off lost: **fees + chop + late entries**. `MomentumMACD` overtraded (600 trades in 91 days ≈ 6.6/day) and paid for it.

## Strategy × pair — 15m isolated (`max_open_trades=1`)

Each cell is a dedicated 1000 USDT book on that pair only. Ranked by absolute profit.

| Strategy | Pair | Trades | Win rate | Total profit % | Profit USDT | Profit factor | Max DD % | Expectancy | Exp. ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SampleStrategy | ETH/USDT | 25 | 96.0% | +24.34% | +243.44 | 11.34 | 1.86% | 9.74 | 0.41 |
| SampleStrategy | BTC/USDT | 16 | 93.8% | +15.29% | +152.88 | 24.59 | 0.56% | 9.56 | 1.47 |
| TrendFollowingEMA | BTC/USDT | 32 | 25.0% | +11.33% | +113.35 | 1.52 | 6.58% | 3.54 | 0.39 |
| SampleStrategy | SOL/USDT | 20 | 90.0% | **−3.09%** | −30.95 | 0.85 | 13.91% | −1.55 | −0.02 |
| SupertrendATR | ETH/USDT | 150 | 32.0% | −7.17% | −71.68 | 0.90 | 16.62% | −0.48 | −0.07 |
| TrendFollowingEMA | ETH/USDT | 38 | 13.2% | −9.98% | −99.77 | 0.64 | 13.91% | −2.63 | −0.31 |
| TrendFollowingEMA | SOL/USDT | 31 | 12.9% | −11.52% | −115.21 | 0.64 | 16.02% | −3.72 | −0.32 |
| MomentumMACD | SOL/USDT | 193 | 29.5% | −14.52% | −145.21 | 0.81 | 23.25% | −0.75 | −0.14 |
| SupertrendATR | BTC/USDT | 140 | 25.7% | −15.77% | −157.70 | 0.72 | 23.88% | −1.13 | −0.21 |
| MomentumMACD | ETH/USDT | 211 | 23.7% | −20.27% | −202.73 | 0.72 | 25.83% | −0.96 | −0.22 |
| MomentumMACD | BTC/USDT | 196 | 22.4% | −23.22% | −232.18 | 0.57 | 29.64% | −1.18 | −0.33 |
| SupertrendATR | SOL/USDT | 170 | 28.8% | −25.46% | −254.59 | 0.70 | 28.37% | −1.50 | −0.22 |

Even the two isolated SampleStrategy “wins” trail buy-and-hold (ETH +24% vs +43% hold; BTC +15% vs +17% hold). SOL lost for every strategy.

The only non-sample isolated winner is `TrendFollowingEMA` on BTC (+11.3%, PF 1.52). That did **not** survive the combined three-pair book (overall −3.4%), and ETH/SOL EMA trend both lost.

## 5m sensitivity (combined)

SampleStrategy’s file defaults to 5m. Same 91 days, three pairs, `max_open_trades=3`:

| Strategy | Trades | Win rate | Total profit | Profit factor | Max DD |
| --- | --- | --- | --- | --- | --- |
| SampleStrategy | 80 | 88.8% | **+41.39 USDT (+4.14%)** | 1.21 | 9.86% |
| TrendFollowingEMA | 306 | 21.9% | −175.56 (−17.56%) | 0.62 | 17.56% |
| MomentumMACD | 1557 | 18.3% | −611.87 (−61.19%) | 0.40 | 61.19% |
| SupertrendATR | 2081 | 20.4% | −728.21 (−72.82%) | 0.43 | 73.30% |

Finer candles made trend/momentum **worse** (more signals, more fees). SampleStrategy stayed green but smaller and with a deeper drawdown. 5m Supertrend/MACD would have drawn the account down ~60–73%.

## Framework evaluation (the actual goal)

Freqtrade is usable for this research loop:

1. Native install (`venv` + `pip install -r requirements.txt` + `pip install -e .`) works on Python 3.12. `ta-lib` 0.7.1 installed from a wheel; no manual C library build was required here.
2. `freqtrade create-userdir` produced the expected `user_data/strategies` layout.
3. `download-data` needs no API keys for public OHLCV.
4. `backtesting --strategy-list` compared four strategies in one command and exported zip + metadata under `artifacts/backtest_results/`.
5. Dry-run config validates without live keys (dummy Telegram token/chat_id are schema-required even when Telegram is off).

Friction worth knowing:

- **Binance.com is geo-blocked** in some environments (HTTP 451). Use `--exchange binanceus` or Freqtrade’s `data.binance.vision` path (`exchange.only_from_ccxt: false` on `binance`) from a non-restricted network.
- Config schema still wants Telegram `token` / `chat_id` and a ≥32-char JWT secret even when those features are disabled.
- `user_data/*` is gitignored upstream. This branch adds exceptions for strategies + the research config only. OHLCV feather files stay local.

## Reproduce

From a clone of this branch:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install -r requirements.txt
python -m pip install -e .

# One-shot (download + combined 15m + isolated 15m + summary)
./artifacts/run_research_backtests.sh
```

Manual commands actually used in this run:

```bash
# Data. Prefer binance; this environment had to use binanceus.
freqtrade download-data \
  -c user_data/research_spot_usdt.json \
  --exchange binanceus \
  --days 120 \
  -t 5m 15m \
  --trading-mode spot

# Combined 15m comparison
freqtrade backtesting \
  -c user_data/research_spot_usdt.json \
  --strategy-list SampleStrategy TrendFollowingEMA MomentumMACD SupertrendATR \
  --timeframe 15m --timerange 20260615-20260914 \
  --export trades --backtest-directory artifacts/backtest_results \
  --breakdown month --cache none \
  --notes "combined BTC/ETH/SOL 15m 20260615-20260914"

# Isolated pair books
for pair in BTC/USDT ETH/USDT SOL/USDT; do
  freqtrade backtesting \
    -c user_data/research_spot_usdt.json \
    --strategy-list SampleStrategy TrendFollowingEMA MomentumMACD SupertrendATR \
    --timeframe 15m --timerange 20260615-20260914 \
    -p "$pair" --max-open-trades 1 \
    --export trades --backtest-directory artifacts/backtest_results \
    --cache none \
    --notes "isolated ${pair} 15m 20260615-20260914"
done

# Optional 5m sensitivity
freqtrade backtesting \
  -c user_data/research_spot_usdt.json \
  --strategy-list SampleStrategy TrendFollowingEMA MomentumMACD SupertrendATR \
  --timeframe 5m --timerange 20260615-20260914 \
  --export trades --backtest-directory artifacts/backtest_results \
  --cache none \
  --notes "combined BTC/ETH/SOL 5m 20260615-20260914"

python artifacts/summarize_backtests.py
```

Reprint a saved result:

```bash
freqtrade backtesting-show --backtest-directory artifacts/backtest_results
```

## Artifacts

| Path | What |
| --- | --- |
| `artifacts/REPORT.md` | This file |
| `artifacts/comparison_table.md` | Generated ranked tables |
| `artifacts/comparison_table.csv` | Same metrics as CSV |
| `artifacts/research_spot_usdt.json` | Copy of the dry-run config |
| `artifacts/run_research_backtests.sh` | Reproduction script |
| `artifacts/summarize_backtests.py` | Zip → table extractor |
| `artifacts/backtest_results/*.zip` | Raw Freqtrade exports (trades, config snapshot, strategy copies) |
| `artifacts/logs/` | Full CLI logs from this run |
| `user_data/strategies/` | Strategies |
| `user_data/research_spot_usdt.json` | Live research config |
| `user_data/data/binanceus/` | OHLCV (gitignored; re-download) |

## Honest conclusion

Freqtrade is a reasonable **research harness** for these pairs: config, public data, backtest, and exports all work without live keys.

It is **not** a reason to day-trade BTC/ETH/SOL on these signals. In a 91-day bull window:

- Mean-reversion was already known to lose (prior bake-off).
- EMA trend, MACD momentum, and Supertrend also lost after fees on the combined 15m book.
- The official sample’s +12% is tight ROI harvesting that still **underperformed holding the coins**, and it lost on SOL.
- 5m made the losing strategies lose faster.

Next research (still paper-only): longer sample including a downtrend, walk-forward / out-of-sample, and a buy-and-hold benchmark as a required baseline — not more live keys.

Freqtrade’s own disclaimer applies: this software is for educational use. Do not risk money you cannot afford to lose.
