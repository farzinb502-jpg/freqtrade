# pragma pylint: disable=missing-docstring, invalid-name
"""
Trend-following EMA crossover with an ADX regime filter.

Long-only. Intended for paper/backtest research on high-volume USDT pairs.
Not optimized; parameters are textbook defaults.
"""

from pandas import DataFrame

from freqtrade.strategy import IStrategy
import talib.abstract as ta
from technical import qtpylib


class TrendFollowingEMA(IStrategy):
    """
    Enter when the fast EMA crosses above the slow EMA while ADX shows a trend.
    Exit on the opposite crossover. Relies on signals more than tight ROI.
    """

    INTERFACE_VERSION = 3
    can_short = False
    timeframe = "15m"

    # Give trend trades room; take-profit is mostly the exit signal.
    minimal_roi = {
        "0": 0.20,
    }
    stoploss = -0.06
    trailing_stop = False

    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    startup_candle_count = 200

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False,
    }
    order_time_in_force = {"entry": "GTC", "exit": "GTC"}

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["ema_fast"], dataframe["ema_slow"])
                & (dataframe["adx"] > 20)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["ema_fast"], dataframe["ema_slow"])
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe
