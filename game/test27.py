#%%
from __future__ import print_function
from collections import namedtuple
from rx.subjects import Subject


s = Subject()
itemstream = s.filter(lambda e: e[0] == 'item')

itemstream.subscribe(print)

#%%
DisplayName = namedtuple('DisplayName', ('name', 'color'))
Char = namedtuple('Char', ('displayName', 'stat'))

bob = DisplayName('Bob', [1, 2, 3])
c = Char(bob, 23)