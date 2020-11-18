from .. import EcsGameSystem
from ...lib.util import pick


class LocationSystem(EcsGameSystem):

    @property
    def actions(self):
        return {'MOVE_ENTITY': self._update_location}

    def _update_location(self, data):
        eid = data.get('entity', None)
        if eid and self.store.get_entity(eid).get('location', None):
            self.store.update(
                '/location/{eid}', {
                    **{'level': None, 'area': None},
                    **pick(('level', 'area'), data)
                })
