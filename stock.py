# %%
import numpy as np

np.random.seed(123)

ln = np.log
exp = np.exp


def pick(keys, dct: dict):
    return {k: dct[k] for k in keys if k in dct}


class Symbol:

    def __init__(self, ln_mu=0.0, ln_sig=0.01, price=1):
        self.ln_mu = ln_mu
        self.ln_sig = ln_sig
        self.price = price

    def __repr__(self):
        return f"{type(self).__name__}(ln_mu={self.ln_mu}, ln_sig={self.ln_sig}, price={self.price})"

    @property
    def mu(self):
        return np.exp(self.ln_mu)

    @property
    def sig(self):
        return np.exp(self.ln_sig)

    def simLnReturns(self, periods=1):
        return [np.random.normal(self.ln_mu - self.ln_sig**2/2, self.ln_sig)
                for _ in range(periods)]

    def simReturns(self, periods=1):
        return np.exp(self.simLnReturns(periods))

    def simMults(self, periods=1):
        return np.cumprod(self.simReturns(periods))

    def simPrices(self, periods=1):
        return self.price*self.simMults(periods)

# %%


def _logreturns(mean=0.0, volatility=0.01, days=40):
    return np.random.normal(mean - volatility**2/2, volatility, size=days)


def _isoutside(logreturns, spread):
    hi = ln(1 + spread)
    lo = ln(1 - spread)
    logmults = np.cumsum(logreturns)
    return any(logmults < lo) or any(logmults > hi)


def straddle(mean=0.0, volatility=0.01, spread=0.1, days=60, trials=20000):
    return sum(_isoutside(_logreturns(mean, volatility, days), spread)
               for _ in range(trials)) / trials


# %%


UN = {'mean': ln(54/47)/72,
      'volatility': .00963,
      'spread': 6/54,
      'days': 60}

LNG = {'mean': ln(50/34)/72,
       'volatility': .0185,
       'spread': 11.4/50,
       'days': 60}

SPY = {'mean': ln(320/300)/42,
       'volatility': .0094,
       'spread': 22.5/323,
       'days': 60}

VTI = {'mean': ln(160/148)/40,
       'volatility': .01,
       'spread': 22/163,
       'days': 90}

GLD = {'mean': ln(170/160)/60,
       'volatility': .00477,
       'spread': 12.65/170,
       'days': 60}


def printEst(symbol: dict):
    halfvol = symbol['volatility'] / 2
    increments = np.linspace(halfvol, 4*halfvol, 11)
    return [straddle(**{**symbol, 'volatility': inc})
            for inc in increments]

# %%


for sym in UN, LNG:
    print(f'{sym}: {straddle(**sym)}')

# %%
