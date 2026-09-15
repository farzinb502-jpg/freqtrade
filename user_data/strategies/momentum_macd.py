# pragma pylint: disable=missing-docstring, invalid-name
"""
MACD momentum with an EMA-50 trend filter.

Long-only. Intended for paper/backtest research on high-volume USDT pairs.
Not optimized; parameters are textbook defaults.
"""

from pandas import DataFrame

from freqtrade.strategy import IStrategy
import talib.abstract as ta
from technical import qtpylib


class MomentumMACD(IStrategy):
    """
    Enter when MACD crosses above its signal while price is above EMA 50
    and RSI is not oversold (momentum confirmation).
    Exit when MACD crosses back below the signal.
    """

    INTERFACE_VERSION = 3
    can_short = False
    timeframe = "15m"

    minimal_roi = {
        "0": 0.12,
        "60": 0.04,
        "180": 0.01,
    }
    stoploss = -0.05
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
        macd = ta.MACD(dataframe, fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]
        dataframe["ema_50"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_above(dataframe["macd"], dataframe["macdsignal"])
                & (dataframe["close"] > dataframe["ema_50"])
                & (dataframe["rsi"] > 50)
                & (dataframe["volume"] > 0)
            ),
            "enter_long",
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                qtpylib.crossed_below(dataframe["macd"], dataframe["macdsignal"])
                & (dataframe["volume"] > 0)
            ),
            "exit_long",
        ] = 1
        return dataframe
