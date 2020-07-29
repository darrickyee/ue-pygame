# %%
import csv
import typing as t
from functools import reduce


def readf(fpath):
    with open(fpath, newline='', encoding='utf-8') as f:
        rdr = csv.reader(f)
        rows = [r for r in rdr]
        return {int(row[0]): tuple(float(p) for p in row[1:5]) for row in rows[1:]}


def pick(keys: t.Iterable[t.Any], dct: dict):
    return {k: dct[k] for k in keys if k in dct}


def flatten(iterables: t.Iterable[t.Iterable[t.Any]]):
    return reduce(lambda prev, curr: [*prev, *curr], iterables, [])

# %%


spypr = readf('./QQQ.csv')

start = min(spypr)
end = max(spypr)

data = list()

for monday in range(start, end, 7):
    prices = flatten(pick(tuple(range(monday, monday+7)), spypr).values())
    week = {'day': monday, 'open': prices[0], 'maxchg': max(
        map(lambda price: abs(price - prices[0])/prices[0]*100, prices))}
    data.append(week)

with open('./QQQchg.csv', 'w', newline='') as f:
    wrtr = csv.writer(f)
    for row in data:
        wrtr.writerow(row.values())

# %%
