# TrendRider vs SampleStrategy (paper backtest)

**Paper / backtest only. No live trading. No real exchange keys. Do not spend funds based on this file.**

Awesome-list blurbs and TrendRider’s README are **not** evidence. This file is the backtest we actually ran on this fork.

## Recommendation

**Keep `SampleStrategy` as the dry-run default. Do not switch paper trading to TrendRider. Do not go live with either.**

TrendRider did **not** beat SampleStrategy on expectancy or profit factor (the criteria that matter here — not win rate alone). It lost money on the same 91-day Binance.US spot book where SampleStrategy was green. SampleStrategy still **lagged buy-and-hold** (see `artifacts/REPORT.md`). Neither result is a day-trading edge.

`-s TrendRiderStrategy` is available for research, but it is **not** wired as the paper default.

## What was pulled in

| Item | Detail |
| --- | --- |
| Upstream | [darkvolg/trendrider-strategy](https://github.com/darkvolg/trendrider-strategy) (MIT, Copyright 2026 TrendRider) |
| Copy in this fork | `user_data/strategies/trendrider_strategy.py` (class `TrendRiderStrategy`) |
| License text | `user_data/strategies/TRENDRIDER_LICENSE` |
| Listed as | Open-source Freqtrade strategy (cascading early-loss exit, MTF, BTC/ETH/SOL + alts) |
| Logic kept | TA-Lib entries/exits, confidence filter, 2h/4h/8h/16h/24h `custom_exit` cascade, 1x leverage hook, protections |
| Logic adapted | BTC sentiment pair `BTC/USDT` (spot) instead of Bybit perpetual `BTC/USDT:USDT` |

Upstream README marketing (not reproduced as a result): “+69% vs V3” on a **1h / 30-day / BTC+ETH+SOL** window, plus a paid “Pro Pack” PF 1.03 → 1.41 claim. Those are relative-to-their-V3 / other-window numbers. They are not this backtest.

Public TrendRider already stubs Fear & Greed at 50, funding/OI at 0, and 1x leverage. This fork did not add those private layers.

## Bybit-only pieces that did not port

Upstream `config.example.json` is **Bybit USDT-M futures**, not this fork’s dry-run path. We did **not** copy that file (it contains placeholder API key fields and live-oriented order types).

| Upstream (Bybit example) | This fork |
| --- | --- |
| `exchange.name: bybit` | `binanceus` |
| `trading_mode: futures`, `margin_mode: isolated` | `spot`, empty margin |
| Pairs `BTC/USDT:USDT`, `ETH/USDT:USDT`, `SOL/USDT:USDT` | Spot `BTC/USDT`, `ETH/USDT`, `SOL/USDT` |
| `stoploss_on_exchange: true` | Spot research config has no exchange stoploss |
| Order-book entry/exit (`price_side: other`, `use_order_book: true`) | Last-price / `price_side: same` (same as prior research) |
| `stake_amount: 50`, wallet 500 USDT | `unlimited` stake, 1000 USDT wallet, `max_open_trades: 3` |
| Placeholder `YOUR_API_KEY_HERE` | Empty `key` / `secret`; `dry_run: true` |
| Bybit funding / OI in the **private** bot | Already stubbed in the public strategy (`funding_rate = 0`) |

What **did** port cleanly: long-only TA, MTF 4h/1d, BTC 1h sentiment on spot `BTC/USDT`, ROI/stoploss/trailing, cascade exits, confidence reject, Cooldown/StoplossGuard/MaxDrawdown (minutes). `leverage()` stays 1 and is unused on spot.

## Backtest setup (same window/fees as before)

| Item | Value |
| --- | --- |
| Exchange data | Binance.US public OHLCV (spot). Same reason as `REPORT.md`: Binance.com HTTP 451 here. |
| Pairs | `BTC/USDT`, `ETH/USDT`, `SOL/USDT` |
| Timerange | `20260615-20260914` (91 days) — **same as SampleStrategy table** |
| Fee | `--fee 0.001` (0.10% per side) — same worst-case Binance.US tier |
| Wallet | 1000 USDT, `max_open_trades=3` combined / `1` isolated |
| Config | `user_data/research_spot_usdt.json` |
| 15m history | ~2026-05-18 onward (enough for 15m startup; daily EMA200 uses 1d files) |
| Extra MTF data | 1h / 4h / 1d from 2025-08-11 (~400 days) so daily EMA200 is defined before the timerange |
| Buy-and-hold (15m, same window) | BTC **+16.63%**, ETH **+43.08%**, SOL **+38.50%** |

Two timeframes:

1. **15m** — apples-to-apples with the previous SampleStrategy book. TrendRider’s file default is 1h; Freqtrade overrides from `--timeframe`. ROI keys are still **minutes**, cascade exits are wall-clock hours, so those pieces stay comparable. More 15m bars ⇒ more signals.
2. **1h** — TrendRider’s native timeframe (fairer to the author). SampleStrategy is also run at 1h so the comparison is not “native vs forced”.

`--enable-protections` is off by default in Freqtrade backtesting. TrendRider defines Cooldown 20m / StoplossGuard / MaxDrawdown 10%. We ran 15m both ways and 1h with protections on (1h without protections matched the protected 1h book).

Reproduce:

```bash
./artifacts/run_trendrider_compare.sh
```

## Combined book — 15m (the apples-to-apples run)

Capital shared across three pairs. No protections (matches how SampleStrategy was originally scored).

| Strategy | Trades | Win rate | Profit USDT | Profit % | Profit factor | Max DD (acct) | Expectancy (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **SampleStrategy** | 61 | 93.4% | **+119.73** | **+11.97%** | **2.52** | 3.26% | 1.96 (0.10) |
| TrendRiderStrategy | 395 | 22.8% | **−217.72** | **−21.77%** | **0.64** | 23.44% | −0.55 (−0.28) |

TrendRider 15m **with** `--enable-protections`: 386 trades, 23.1% win rate, **−211.17 USDT (−21.12%)**, PF **0.64**, max DD 22.68%, expectancy −0.55 (−0.28). Protections barely moved the needle.

Per pair inside the 15m combined TrendRider book (no protections): BTC −5.02% (124 trades), SOL −5.75% (127), ETH −11.01% (144). All three lost.

What actually exited TrendRider: the cascade (`early_loss_cut_*`) dominated. Lots of small losers from the 2h/4h cuts, a handful of ROI winners, one −6% stop. That is the opposite of SampleStrategy’s tight 1% ROI clip.

## Combined book — 1h (TrendRider native)

`--enable-protections` on. Same timerange and 0.10% fee.

| Strategy | Trades | Win rate | Profit USDT | Profit % | Profit factor | Max DD (acct) | Expectancy (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **SampleStrategy** | 24 | 100% | **+82.17** | **+8.22%** | n/a (no losses) | 0.00% closed / 2.08% wallet | 3.42 |
| TrendRiderStrategy | 133 | 18.0% | **−126.37** | **−12.64%** | **0.43** | 12.64% | −0.95 (−0.47) |

1h without protections for TrendRider was **identical** (−12.64%, 133 trades, PF 0.43). The protection block did not save it.

SampleStrategy 1h PF prints `0.00` in Freqtrade because there were **zero losing trades** (every exit was the 1% ROI timer). That is not infinite skill — it is the same tight-ROI harvest as 15m, on fewer bars, still far behind buy-and-hold (~+33% market change).

TrendRider 1h per pair (combined): BTC −2.67% (36), SOL −4.45% (46), ETH −5.51% (51).

## Isolated pair books (`max_open_trades=1`)

Each cell is its own 1000 USDT book.

### 15m

| Strategy | Pair | Trades | Win rate | Profit % | Profit factor | Max DD |
| --- | --- | --- | --- | --- | --- | --- |
| SampleStrategy | ETH/USDT | 25 | 96.0% | **+24.34%** | 11.34 | 1.86% |
| SampleStrategy | BTC/USDT | 16 | 93.8% | **+15.29%** | 24.59 | 0.56% |
| SampleStrategy | SOL/USDT | 20 | 90.0% | −3.09% | 0.85 | 13.91% |
| TrendRiderStrategy | BTC/USDT | 124 | 25.0% | **−15.73%** | 0.63 | 18.45% |
| TrendRiderStrategy | SOL/USDT | 127 | 22.8% | **−18.19%** | 0.72 | 23.25% |
| TrendRiderStrategy | ETH/USDT | 144 | 20.8% | **−31.44%** | 0.57 | 34.80% |

### 1h (protections on)

| Strategy | Pair | Trades | Win rate | Profit % | Profit factor | Max DD |
| --- | --- | --- | --- | --- | --- | --- |
| SampleStrategy | BTC/USDT | 10 | 100% | **+10.36%** | n/a (no losses) | 0.00% |
| SampleStrategy | ETH/USDT | 7 | 100% | **+7.15%** | n/a | 0.00% |
| SampleStrategy | SOL/USDT | 7 | 100% | **+7.15%** | n/a | 0.00% |
| TrendRiderStrategy | BTC/USDT | 36 | 19.4% | **−8.17%** | 0.35 | 8.17% |
| TrendRiderStrategy | SOL/USDT | 46 | 19.6% | **−13.73%** | 0.52 | 14.34% |
| TrendRiderStrategy | ETH/USDT | 51 | 15.7% | **−16.19%** | 0.36 | 16.19% |

TrendRider lost on **every** pair and timeframe we ran. SampleStrategy isolated 15m numbers match the earlier report (re-run with explicit `--fee 0.001` did not change them).

## Why this is not a surprise

- **Overtrade + fees.** 395 15m trades vs 61. 133 1h trades vs 24. 0.10% each side eats a wide-stop / small-target book.
- **Cascade cuts winners-to-be and keeps the bleed small-but-frequent.** Upstream designed that cascade to avoid sitting 24h in a loser. Here it produced hundreds of sub-1% losers and a profit factor below 1.
- **Confidence filter is not a free lunch.** `confirm_trade_entry` rejected many bars; the ones that passed still lost after fees.
- **Stubbed private layers cannot be blamed for “missing alpha” in a way we can measure.** FNG/funding/OI are constants. If the paid bot is better, that is a different (closed) system.
- **Bull window.** Buy-and-hold was the right benchmark. TrendRider did not capture it. SampleStrategy clipped 1% coupons and still trailed the coins.

## Dry-run wiring

Default paper config stays:

```bash
freqtrade trade --dry-run -c user_data/config_dryrun_crypto.json -s SampleStrategy
```

TrendRider is **not** the default. It did not earn an optional “switch the paper bot” recommendation.

If you still want to **observe** it on paper (it will not place real orders):

```bash
freqtrade trade --dry-run -c user_data/config_dryrun_crypto.json -s TrendRiderStrategy
```

Keep `dry_run: true`. Keep empty keys. Prefer **1h** in the JSON if you do this — that is the strategy’s native timeframe. 15m paper would over-signal the same way the 15m backtest did. This is still not a go-live checklist.

## Artifacts from this compare

| Path | What |
| --- | --- |
| `user_data/strategies/trendrider_strategy.py` | Adapted strategy |
| `user_data/strategies/TRENDRIDER_LICENSE` | MIT text |
| `artifacts/run_trendrider_compare.sh` | Download + backtest wrapper |
| `artifacts/logs/backtest-trendrider-vs-sample-15m.log` | Combined 15m |
| `artifacts/logs/backtest-trendrider-15m-protections.log` | Combined 15m + protections |
| `artifacts/logs/backtest-trendrider-vs-sample-1h.log` | Combined 1h + protections |
| `artifacts/logs/backtest-trendrider-1h-noprotections.log` | Combined 1h, protections off |
| `artifacts/logs/backtest-trendrider-{BTC,ETH,SOL}_USDT-{15m,1h}.log` | Isolated books |
| `artifacts/backtest_results/*.zip` | Raw Freqtrade exports |
