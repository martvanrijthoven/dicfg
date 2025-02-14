import datetime
import platform
import uuid
from enum import Enum
from pathlib import Path

from dicfg.addons.addon import TemplateAddon


class LogLevel(Enum):
    """Log level for templates"""

    DEBUG = "DEBUG"
    VERBOSE = "VERBOSE"


class Verbose(TemplateAddon):
    NAME = "verbose"

    @classmethod
    def data(self):
        return {"*log": LogLevel.VERBOSE}


class Debug(TemplateAddon):
    NAME = "debug"

    @classmethod
    def data(self):
        return {"*log": LogLevel.DEBUG}


class Build(TemplateAddon):
    NAME = "build"

    @classmethod
    def data(self):
        return {"*build": True}


class DontBuild(TemplateAddon):
    """Template for io.StringIO object"""

    NAME = "dontbuild"

    @classmethod
    def data(self):
        return {"*build": False}


class CurrentWorkingDirectory(TemplateAddon):

    NAME = "cwd"

    @classmethod
    def data(cls):
        return str(Path.cwd())


class SystemInfo(TemplateAddon):
    NAME = "systeminfo"

    @classmethod
    def data(cls):
        return {
            "os_name": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.architecture()[0],
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_compiler": platform.python_compiler(),
            "node": platform.node(),
        }


class DateTimeNow(TemplateAddon):

    NAME = "datetimenow"

    @classmethod
    def data(cls):
        return str(datetime.datetime.now())


class UUID4(TemplateAddon):
    NAME = "uuid4"

    @classmethod
    def data(cls):
        """Returns a random version 4 UUID."""
        return str(uuid.uuid4())


import sqlite3


def get_sqlite_type(value):
    """
    Maps a Python value to an appropriate SQLite column type.
    Booleans are treated as INTEGER since True/False are stored as 1/0.
    """
    if isinstance(value, bool):
        return "INTEGER"
    elif isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    elif isinstance(value, bytes):
        return "BLOB"
    return "TEXT"


def write_to_database(database: str, table: str, rows: list[dict]):
    """
    Writes a list of dictionaries as rows into the specified table.

    Parameters:
        database (str): Path to the SQLite database file.
        table (str): The name of the table to write to.
        rows (list of dict): A list of dictionaries representing rows to insert,
                             where keys are column names.

    Behavior:
        - If the database file does not exist, it will be created.
        - If the table does not exist, it will be created using the union of keys from all dictionaries.
          The column types are inferred from the first non-null value encountered for each key.
        - For each row, if a key is missing, NULL will be inserted.
    """
    if not rows:
        raise ValueError("The list of rows is empty.")

    # Combine keys from all dictionaries to form the complete set of columns.
    columns = set()
    for row in rows:
        columns.update(row.keys())
    columns = list(columns)

    # Infer column definitions: For each column, find the first non-null value to determine its type.
    column_definitions = []
    for col in columns:
        col_type = None
        for row in rows:
            if col in row and row[col] is not None:
                col_type = get_sqlite_type(row[col])
                break
        if col_type is None:
            col_type = "TEXT"
        column_definitions.append(f"{col} {col_type}")

    conn = sqlite3.connect(database)
    try:
        cursor = conn.cursor()

        # Create the table if it doesn't exist.
        create_table_query = (
            f"CREATE TABLE IF NOT EXISTS {table} ("
            + ", ".join(column_definitions)
            + ");"
        )
        cursor.execute(create_table_query)

        # Build the INSERT query dynamically.
        placeholders = ", ".join("?" for _ in columns)
        insert_query = (
            f"INSERT INTO {table} ("
            + ", ".join(columns)
            + ") VALUES ("
            + placeholders
            + ");"
        )

        # Prepare data: for each row, get the value for each column (using None if a column is missing).
        data = [tuple(row.get(col) for col in columns) for row in rows]
        cursor.executemany(insert_query, data)

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


class SQLWriter(TemplateAddon):
    """Template"""

    NAME = "sqlwrite"

    @classmethod
    def data(self):
        return {"*object": "dicfg.addons.templates.write_to_database"}
