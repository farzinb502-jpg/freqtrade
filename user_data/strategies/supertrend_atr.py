# pragma pylint: disable=missing-docstring, invalid-name
"""
Classic ATR Supertrend, long-only.

Intended for paper/backtest research on high-volume USDT pairs.
Not optimized; ATR period 10 / multiplier 3.0 are common defaults.
"""

from pandas import DataFrame
import numpy as np

from freqtrade.strategy import IStrategy
import talib.abstract as ta
from technical import qtpylib


class SupertrendATR(IStrategy):
    """
    Enter when close crosses above the Supertrend line (trend flips up).
    Exit when close crosses below the Supertrend line (trend flips down).
    """

    INTERFACE_VERSION = 3
    can_short = False
    timeframe = "15m"

    minimal_roi = {
        "0": 0.25,
    }
    stoploss = -0.08
    trailing_stop = False

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    startup_candle_count = 200

    atr_period = 10
    atr_multiplier = 3.0

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=self.atr_period)
        hl2 = (dataframe["high"] + dataframe["low"]) / 2.0
        dataframe["st_upper"] = hl2 + self.atr_multiplier * dataframe["atr"]
        dataframe["st_lower"] = hl2 - self.atr_multiplier * dataframe["atr"]

        supertrend = np.full(len(dataframe), np.nan)
        direction = np.ones(len(dataframe))
        upper = dataframe["st_upper"].to_numpy()
        lower = dataframe["st_lower"].to_numpy()
        close = dataframe["close"].to_numpy()

        for i in range(1, len(dataframe)):
            if np.isnan(upper[i]) or np.isnan(lower[i]):
                continue
            # Final upper/lower bands
            if lower[i] > lower[i - 1] or close[i - 1] < lower[i - 1]:
                final_lower = lower[i]
            else:
                final_lower = lower[i - 1]
            if upper[i] < upper[i - 1] or close[i - 1] > upper[i - 1]:
                final_upper = upper[i]
            else:
                final_upper = upper[i - 1]
            lower[i] = final_lower
            upper[i] = final_upper

            if np.isnan(supertrend[i - 1]):
                supertrend[i] = final_upper
                direction[i] = -1
                continue

            if supertrend[i - 1] == upper[i - 1]:
                if close[i] > final_upper:
                    supertrend[i] = final_lower
                    direction[i] = 1
                else:
                    supertrend[i] = final_upper
                    direction[i] = -1
            else:
                if close[i] < final_lower:
                    supertrend[i] = final_upper
                    direction[i] = -1
                else:
                    supertrend[i] = final_lower
                    direction[i] = 1

        dataframe["st_upper"] = upper
        dataframe["st_lower"] = lower
        dataframe["supertrend"] = supertrend
        dataframe["st_direction"] = direction
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["st_direction"], 0)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["st_direction"], 0)
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe
