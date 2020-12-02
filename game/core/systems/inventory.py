# %%
from functools import partial
# %%
from typing import Any, Callable
from .. import EcsGameSystem


class InventorySystem(EcsGameSystem):

    @property
    def actions(self):
        return {'ADD_ITEM': self._add,
                'REMOVE_ITEM': self._remove}

    def _get_inventory(self, eid) -> dict:
        return self._context.state['inventory'].get(eid, {})

    def _get_itembase(self, item_id):
        return self._context.state['itembase'].get(item_id, {})

    def _parsedata(self, data: dict):
        item_id = data.get('item_id', None)
        if item_id:
            if (item_base := self._get_itembase(item_id)):
                maxcount = item_base.get('maxcount', float('inf'))
                maxcount = float('inf') if maxcount < 1 else maxcount
                item_base = {**item_base, **{'maxcount': maxcount}}

                return {'item_id': item_id,
                        'count': data.get('count', 1),
                        'item_base': item_base}

        return {}

    def _get_data(self, data: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], Callable[[int], None]]:
        entity = data.get('entity', 'player')
        item_id = data.get('item_id', '')
        item_base: dict[str, Any] = self.store.get_component(
            item_id, 'item_base')
        inventory: dict[str, Any] = self.store.get_component(
            entity, 'inventory')

        def setter(count: int):

            if count <= 0:
                inventory.pop(item_id, None)
            else:
                inventory.update({item_id: count})

            self.store.set_component(entity, 'inventory', inventory)

        return (item_base,
                inventory,
                setter)

    def _add(self, data: dict):
        count = data.get('count', 1)
        item_id = data.get('item_id', '')
        item_base, inventory, set_count = self._get_data(data)

        if item_base and inventory:
            current = inventory.get(item_id, 0)
            set_count(current + count)

    def _remove(self, data):
        item_base, inventory, set_count = self._get_data(data)

        if item_base and inventory and item_id in inventory:
            newcount = max(inventory.get(item_id, 0) - num, 0)

            if newcount:
                inventory[item_id] = newcount
            else:
                del inventory[item_id]

            self.store.set_component(eid, 'inventory', inventory)
