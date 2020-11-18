
def addItem(entity: str, item_id: str, count=1):
    return {'action_type': 'ADD_ITEM', 'data': {
        'entity': entity, 'item_id': item_id, 'count': count}}


def removeItem(entity: str, item_id: str, count=1):
    return {'action_type': 'REMOVE_ITEM', 'data': {
        'entity': entity, 'item_id': item_id, 'count': count}}


def startDialogue(dlg_id: str = None):
    return {'action_type': 'START_DIALOGUE', 'data': dlg_id}


def moveEntity(entity: str, level: str, area: str = None):
    return {'action_type': 'MOVE_ENTITY', 'data': {'entity': entity, 'level': level, 'area': area}}


def movePlayer(level: str, area: str = None):
    return {'action_type': 'MOVE_ENTITY', 'data': {'entity': 'player', 'level': level, 'area': area}}
