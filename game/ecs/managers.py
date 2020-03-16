class EntityManager():

    def __init__(self, database=None):
        self.database = database or {}

    @property
    def entity_ids(self):
        return tuple({eid
                      for components in self.database.values()
                      for eid in components})

    @property
    def component_types(self):
        return tuple(self.database.keys())

    @property
    def entity_components(self):
        return {eid: tuple(ctype
                           for ctype, table in self.database.items()
                           if eid in table)
                for eid in self.entity_ids}

    def getEntity(self, entity_id):
        components = {component: data[entity_id]
                      for component, data in self.database.items()
                      if entity_id in data}
        return {'eid': entity_id, **components} if components else {}

    def addComponent(self, entity_id, component):
        ctype = component.get('type', None)
        if not ctype or ctype not in self.database:
            return False

        del component['type']
        self.database[ctype][entity_id] = component
        return True
