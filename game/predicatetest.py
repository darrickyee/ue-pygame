# %%
from game.core.predicate import evaluator

DATA = {
    'world': {'day': 30}
}

p1 = {'path': '/world/day', 'op': '>', 'value': 29}
p2 = {'path': '/world/day', 'op': '==', 'value': 30}
p3 = {'path': '/world/day', 'op': 'le', 'value': 30}
err1 = {'path': '/world/day'}
err2 = {'path': '/world/time', 'op': '==', 'value': 30}
err3 = {'path': '/world/day', 'op': '222', 'value': 30}
err4 = {'path': '/world/day', 'op': '==', 'value': '30'}

for pred in p1, p2, p3, err1, err2, err3, err4:
    fn = evaluator(pred)
    try:
        print(fn(DATA))
    except ValueError as e:
        print(f'Error in predicate {pred}: {e}')

# %%
