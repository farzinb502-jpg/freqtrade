# pragma pylint: disable=missing-docstring, invalid-name
"""
Classic ATR Supertrend, long-only.

Intended for paper/backtest research on high-volume USDT pairs.
Uses pandas-ta Supertrend (ATR period 10, multiplier 3.0).
"""

from pandas import DataFrame
import pandas_ta as pta

from freqtrade.strategy import IStrategy
from technical import qtpylib


class SupertrendATR(IStrategy):
    """
    Enter when Supertrend direction flips from down (-1) to up (+1).
    Exit when it flips back to down.
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
        st = pta.supertrend(
            dataframe["high"],
            dataframe["low"],
            dataframe["close"],
            length=self.atr_period,
            multiplier=self.atr_multiplier,
        )
        direction_col = f"SUPERTd_{self.atr_period}_{self.atr_multiplier}"
        line_col = f"SUPERT_{self.atr_period}_{self.atr_multiplier}"
        dataframe["st_direction"] = st[direction_col]
        dataframe["supertrend"] = st[line_col]
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
