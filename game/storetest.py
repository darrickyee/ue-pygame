# %%
from game.lib.store import Store

st = Store({'world': {'day': 1, 'location': 'Home'},
            'player': {'name': 'Bob', 'memories': ['ok', 'not ok']}})

# %%
st.next({'path': '/world/day', 'value': 34})
