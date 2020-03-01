import json
import sqlite3


CONVERTERS = {
    'list': json.loads
}


def loadTable(conn, table_name):
    with conn:
        rowlist = conn.cursor().execute(
            f'SELECT * FROM {table_name}').fetchall()

    return {row['id']: {k: v for k, v in row.items() if k != 'id'} for row in rowlist}


def getTables(conn):
    with conn:
        rows = [dict(r) for r in conn.execute(
            'SELECT type, name FROM sqlite_master').fetchall()]
        return [r['name'] for r in rows if r['type'] == 'table' and r['name'] != 'sqlite_sequence']


def loadDB(path):
    for typename, converter in CONVERTERS.items():
        sqlite3.register_converter(typename, converter)

    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = lambda cursor, row: dict(sqlite3.Row(cursor, row))

    return {table: loadTable(conn, table) for table in getTables(conn)}
