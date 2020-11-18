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

    def _get_data(self, data) -> tuple[dict, dict, int, str, str]:
        data = {**{'item_id': None, 'entity': 'player'}, **data}

        return (self.store.get_component(data['item_id'], 'item_base'),
                self.store.get_component(data['entity'], 'inventory'),
                data.get('count', 1),
                data['entity'],
                data['item_id'])

    def _add(self, data):
        item_base, inventory, num, eid, item_id = self._get_data(data)

        if item_base and inventory:
            current = inventory.get(item_id, 0)
            self.store.set_component(eid,
                                     'inventory',
                                     inventory.update({item_id: current + num}))

    def _remove(self, data):
        item_base, inventory, num, eid, item_id = self._get_data(data)

        if item_base and inventory and item_id in inventory:
            newcount = max(inventory.get(item_id, 0) - num, 0)

            if newcount:
                inventory[item_id] = newcount
            else:
                del inventory[item_id]

            self.store.set_component(eid, 'inventory', inventory)
