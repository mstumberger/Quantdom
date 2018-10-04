from quantdom import AbstractStrategy, Order, Portfolio


class CUSTOM(AbstractStrategy):
    prices = None
    last_position = None
    signal = None
    short_MA = None
    short_MA_bigger = None
    long_MA = None
    MA_bigger = None
    MA_previous = None
    short_interval = None
    long_interval = None

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
            self.long_MA = float(self.moving_average(self.prices, self.long_interval))
            self.short_MA = float(self.moving_average(self.prices, self.short_interval))
            self.MA_previous = self.MA_bigger
            self.MA_bigger = self.short_MA > self.long_MA

            # determine signal
            if self.MA_bigger:
                self.signal = Order.BUY
            else:
                self.signal = Order.SELL

            # open position if none is opened
            if not self.last_position:
                self.last_position = Order.open(**props)

            # if signal is different then position's opening reopen with current signal
            if self.last_position.type != self.signal:
                Order.close(self.last_position, price=quote.open, time=quote.time)
                self.last_position = Order.open(**props)

    @staticmethod
    def moving_average(data_points, period):
        if len(data_points) > 1:
            return sum(data_points[-period:]) / float(len(data_points[-period:]))
        else:
            return sum(data_points)
