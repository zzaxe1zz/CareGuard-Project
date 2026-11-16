import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "careguard.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
LOG_PATH = os.path.join(BASE_DIR, "auditoria.log")
