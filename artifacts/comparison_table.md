# Backtest comparison tables

Starting wallet 1000 USDT. Spot only. Fees 0.10% per side (Binance.US worst-case tier).
Timerange 2026-06-15 → 2026-09-14 unless noted. Isolated runs use `max_open_trades=1`.

### 15m isolated pair runs (strategy × pair), ranked by absolute profit

| Strategy | Pair | Trades | Win rate | Total profit % | Total profit USDT | Profit factor | Max DD % (acct) | Expectancy | Expectancy ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SampleStrategy | ETH/USDT | 25 | 96.00% | 24.34% | 243.44 | 11.34 | 1.86% | 9.7376 | 0.4135 |
| SampleStrategy | BTC/USDT | 16 | 93.75% | 15.29% | 152.88 | 24.59 | 0.56% | 9.5551 | 1.4747 |
| TrendFollowingEMA | BTC/USDT | 32 | 25.00% | 11.33% | 113.35 | 1.52 | 6.58% | 3.5421 | 0.3930 |
| SampleStrategy | SOL/USDT | 20 | 90.00% | -3.09% | -30.95 | 0.85 | 13.91% | -1.5473 | -0.0151 |
| SupertrendATR | ETH/USDT | 150 | 32.00% | -7.17% | -71.68 | 0.90 | 16.62% | -0.4779 | -0.0657 |
| TrendFollowingEMA | ETH/USDT | 38 | 13.16% | -9.98% | -99.77 | 0.64 | 13.91% | -2.6254 | -0.3097 |
| TrendFollowingEMA | SOL/USDT | 31 | 12.90% | -11.52% | -115.21 | 0.64 | 16.02% | -3.7165 | -0.3150 |
| MomentumMACD | SOL/USDT | 193 | 29.53% | -14.52% | -145.21 | 0.81 | 23.25% | -0.7524 | -0.1372 |
| SupertrendATR | BTC/USDT | 140 | 25.71% | -15.77% | -157.70 | 0.72 | 23.88% | -1.1264 | -0.2061 |
| MomentumMACD | ETH/USDT | 211 | 23.70% | -20.27% | -202.73 | 0.72 | 25.83% | -0.9608 | -0.2161 |
| MomentumMACD | BTC/USDT | 196 | 22.45% | -23.22% | -232.18 | 0.57 | 29.64% | -1.1846 | -0.3299 |
| SupertrendATR | SOL/USDT | 170 | 28.82% | -25.46% | -254.59 | 0.70 | 28.37% | -1.4976 | -0.2158 |


### 15m combined 3-pair runs (max_open_trades=3)

| Strategy | Pair | Trades | Win rate | Total profit % | Total profit USDT | Profit factor | Max DD % (acct) | Expectancy | Expectancy ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SampleStrategy | TOTAL | 61 | 93.44% | 11.97% | 119.73 | 2.52 | 3.26% | 1.9628 | 0.0996 |
| SampleStrategy | ETH/USDT | 25 | 96.00% | 7.66% | 76.60 | 11.99 | 0.64% | 3.0638 | 0.4397 |
| SampleStrategy | BTC/USDT | 16 | 93.75% | 5.01% | 50.12 | 24.91 | 0.20% | 3.1326 | 1.4946 |
| TrendFollowingEMA | BTC/USDT | 32 | 25.00% | 3.86% | 38.64 | 1.57 | 2.11% | 1.2076 | 0.4241 |
| SampleStrategy | SOL/USDT | 20 | 90.00% | -0.70% | -6.99 | 0.90 | 4.79% | -0.3493 | -0.0100 |
| SupertrendATR | ETH/USDT | 150 | 32.00% | -1.96% | -19.60 | 0.91 | 5.07% | -0.1307 | -0.0592 |
| TrendFollowingEMA | ETH/USDT | 38 | 13.16% | -3.33% | -33.26 | 0.65 | 4.80% | -0.8753 | -0.3082 |
| TrendFollowingEMA | TOTAL | 101 | 16.83% | -3.37% | -33.66 | 0.87 | 7.58% | -0.3333 | -0.1041 |
| TrendFollowingEMA | SOL/USDT | 31 | 12.90% | -3.90% | -39.04 | 0.64 | 5.63% | -1.2595 | -0.3178 |
| MomentumMACD | SOL/USDT | 193 | 29.53% | -4.64% | -46.44 | 0.81 | 7.74% | -0.2406 | -0.1356 |
| SupertrendATR | BTC/USDT | 140 | 25.71% | -5.26% | -52.63 | 0.73 | 8.20% | -0.3759 | -0.2015 |
| MomentumMACD | ETH/USDT | 211 | 23.70% | -6.38% | -63.83 | 0.72 | 8.49% | -0.3025 | -0.2102 |
| MomentumMACD | BTC/USDT | 196 | 22.45% | -8.17% | -81.69 | 0.58 | 10.55% | -0.4168 | -0.3287 |
| SupertrendATR | SOL/USDT | 170 | 28.82% | -8.90% | -89.02 | 0.70 | 10.06% | -0.5236 | -0.2120 |
| SupertrendATR | TOTAL | 460 | 28.91% | -16.12% | -161.25 | 0.78 | 22.36% | -0.3505 | -0.1596 |
| MomentumMACD | TOTAL | 600 | 25.17% | -19.20% | -191.96 | 0.71 | 24.92% | -0.3199 | -0.2158 |


### 5m combined 3-pair runs (sensitivity; SampleStrategy native timeframe)

| Strategy | Pair | Trades | Win rate | Total profit % | Total profit USDT | Profit factor | Max DD % (acct) | Expectancy | Expectancy ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SampleStrategy | TOTAL | 80 | 88.75% | 4.14% | 41.39 | 1.21 | 9.86% | 0.5174 | 0.0235 |
| SampleStrategy | ETH/USDT | 31 | 87.10% | 3.23% | 32.26 | 1.55 | 3.38% | 1.0407 | 0.0710 |
| SampleStrategy | SOL/USDT | 34 | 91.18% | 1.30% | 12.97 | 1.14 | 3.38% | 0.3814 | 0.0121 |
| SampleStrategy | BTC/USDT | 15 | 86.67% | -0.38% | -3.84 | 0.92 | 3.36% | -0.2557 | -0.0113 |
| TrendFollowingEMA | ETH/USDT | 111 | 27.93% | -4.32% | -43.18 | 0.72 | 4.83% | -0.3890 | -0.2015 |
| TrendFollowingEMA | BTC/USDT | 104 | 16.35% | -6.04% | -60.40 | 0.56 | 6.60% | -0.5808 | -0.3707 |
| TrendFollowingEMA | SOL/USDT | 91 | 20.88% | -7.20% | -71.98 | 0.58 | 7.20% | -0.7909 | -0.3350 |
| TrendFollowingEMA | TOTAL | 306 | 21.90% | -17.56% | -175.56 | 0.62 | 17.56% | -0.5737 | -0.2976 |
| MomentumMACD | SOL/USDT | 486 | 20.37% | -19.95% | -199.50 | 0.47 | 20.46% | -0.4105 | -0.4212 |
| MomentumMACD | ETH/USDT | 531 | 19.02% | -20.43% | -204.33 | 0.41 | 20.75% | -0.3848 | -0.4759 |
| MomentumMACD | BTC/USDT | 540 | 15.74% | -20.80% | -208.04 | 0.28 | 20.80% | -0.3853 | -0.6064 |
| SupertrendATR | BTC/USDT | 608 | 18.42% | -22.10% | -221.00 | 0.35 | 22.10% | -0.3635 | -0.5290 |
| SupertrendATR | ETH/USDT | 685 | 20.44% | -23.96% | -239.60 | 0.45 | 25.04% | -0.3498 | -0.4365 |
| SupertrendATR | SOL/USDT | 788 | 21.83% | -26.76% | -267.62 | 0.48 | 27.43% | -0.3396 | -0.4096 |
| MomentumMACD | TOTAL | 1557 | 18.30% | -61.19% | -611.87 | 0.40 | 61.19% | -0.3930 | -0.4930 |
| SupertrendATR | TOTAL | 2081 | 20.37% | -72.82% | -728.21 | 0.43 | 73.30% | -0.3499 | -0.4501 |

