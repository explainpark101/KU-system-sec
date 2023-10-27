import json
import datetime
from decimal import Decimal
import sqlite3

from ..config.settings import BASE_DIR, DB_NAME

def json_default_timeISO(value):
    if isinstance(value, dict):
        return json.dumps(value, default=json_default_timeISO)
    if isinstance(value, datetime.datetime):
        return value.strftime('%Y-%m-%dT%T')
    if isinstance(value, datetime.date):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, datetime.time):
        return value.strftime('%T')
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError("JSON not serializable")

def json_dump(objects, iso=False):
    return json.dumps(objects, default=json_default_timeISO)

def dictfetchall(cursor):
    # "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

def dictfetchall_lazy(cursor):
    desc = cursor.description
    return (dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall())

def get_connection():
    return sqlite3.connect(DB_NAME)