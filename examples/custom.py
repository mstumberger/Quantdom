from quantdom import AbstractStrategy, Order, Portfolio
import numpy as np


class CUSTOM_RSI(AbstractStrategy):
    prices = None
    last_position = None
    signal = None
    short_MA = None
    short_MA_bigger = None
    long_MA = None
    MA_bigger = None
    MA_previous = None
    short_interval = None
    RSI_short = 0
    long_interval = None
    RSI_long = 0

    volume = 100  # shares

    def init(self, balance=2000, short_interval=2, long_interval=8):
        self.prices = []
        Portfolio.initial_balance = balance  # default value
        self.short_interval = short_interval
        self.long_interval = long_interval

    def handle(self, quote):
        props = {
            'symbol': self.symbol,  # current selected symbol
            'otype': self.signal,
            'price': quote.open,
            'volume': self.volume,
            'time': quote.time,
        }

        self.prices.append(quote.open)

        if len(self.prices) > self.long_interval:

            # when enough prices we can calculate indicators
            self.long_MA = self.moving_average(self.prices, self.long_interval)
            self.short_MA = self.moving_average(self.prices, self.short_interval)
            self.MA_previous = self.MA_bigger
            self.MA_bigger = self.short_MA > self.long_MA


            self.RSI_short = self.RSI(self.prices, self.short_interval)
            self.RSI_long = self.RSI(self.prices, self.long_interval)

            # determine signal
            if self.MA_bigger:
                if self.signal != Order.BUY:
                    self.signal = Order.BUY
            # elif 35 > self.RSI_long < 55:
            #     self.signal = Order.BUY
            else:
                if self.signal != Order.SELL:
                    self.signal = Order.SELL
            # if self.RSI_long > 70:
            #     self.signal = Order.SELL

            # open position if none is opened
            if not self.last_position:
                self.last_position = Order.open(**props)
            #
            # # # MARGIN ?
            if self.last_position.type == Order.BUY:
                if (self.last_position.open_price * 0.10) < quote.open:
                    Order.close(self.last_position, price=quote.open, time=quote.time)
                    self.signal = Order.SELL
                    self.last_position = Order.open(**props)
            else:
                if (self.last_position.open_price * 0.10) > quote.open:
                    Order.close(self.last_position, price=quote.open, time=quote.time)
                    self.signal = Order.BUY
                    self.last_position = Order.open(**props)
            #
            # # if signal is different then position's opening reopen with current signal
            if self.last_position.type != self.signal:
                Order.close(self.last_position, price=quote.open, time=quote.time)
                self.last_position = Order.open(**props)

    @staticmethod
    def moving_average(data_points, period):
        if len(data_points) > period:
            res = sum(data_points[-period:]) / float(len(data_points[-period:]))
        else:
            res = sum(data_points)
        return float(res)

    @staticmethod
    def RSI(prices, period=12):
        deltas = np.diff(prices)
        seed = deltas[:period + 1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100. / (1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1]  # cause the diff is 1 shorter
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)
        if len(prices) > period:
            return rsi[-1]
        else:
            return 50  # output a neutral amount until enough prices in list to calculate RSI
