import os
import json
import ue_pylink
from .db import loadDB

DB_PATH = os.path.abspath(os.path.dirname(
    os.path.realpath(__file__)) + '/game.db')

DB = loadDB(DB_PATH)

# ue_pylink.broadcast('Init', 'Go')  # pylint: disable=no-member


def getGameEntity(entityid: str):
    return json.dumps(DB['npcs'].get(entityid, {}))
