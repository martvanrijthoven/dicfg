import json
import sqlite3
from dicfg.addons.addon import ModifierAddon, TemplateAddon
from pathlib import Path


class SQLReadModifierError(Exception):
    pass


class SQLReaderModifier(ModifierAddon):
    NAME = "readsql"

    @classmethod
    def modify(cls, params):
        """
        Expects params as a dictionary with the following keys:
          - "database": (str) Path to the SQLite database file.
          - "query": (str) The SQL query to execute.
          - "params": (optional, list/tuple) Parameters for the SQL query.
          - "format": (optional, str) Output format: "raw" (default), "table", or "json".

        Example:
            {
                "database": "example.db",
                "query": "SELECT * FROM users WHERE age > ?",
                "params": [30],
                "format": "json"
            }
        """
        if not isinstance(params, dict):
            raise SQLReadModifierError(
                "Input must be a dictionary with keys 'database' and 'query'."
            )

        database = params.get("database")
        query = params.get("query")
        query_params = params.get("params", None)
        output_format = params.get("format", "data")

        if not database or not query:
            raise SQLReadModifierError("The 'database' and 'query' keys are required.")

        conn = None
        try:
            conn = sqlite3.connect(database)
            cursor = conn.cursor()

            if query_params:
                cursor.execute(query, query_params)
            else:
                cursor.execute(query)

            rows = cursor.fetchall()
            # Get column names for formatting
            headers = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            if output_format == "data":
                output = {
                    str(idx): dict(zip(headers, row)) for idx, row in enumerate(rows)
                }
            elif output_format == "table":
                # Fallback to simple formatting if tabulate isn't installed
                header_line = " | ".join(headers)
                row_lines = "\n".join(
                    " | ".join(str(cell) for cell in row) for row in rows
                )
                output = header_line + "\n" + row_lines
            elif output_format == "json":
                json_rows = [dict(zip(headers, row)) for row in rows]
                output = json.dumps(json_rows, indent=2)
            else:
                output = str(rows)
            return {"data": output}
        except sqlite3.Error as e:
            raise SQLReadModifierError(f"Database error: {e}")
        finally:
            if conn:
                conn.close()


class SQLWriterTemplate(TemplateAddon):
    """Template"""

    NAME = "writesql"

    @classmethod
    def data(self):
        return {
            "*object": "dicfg.addons.sql.write_to_database",
            "database!required": None,
            "table!required": None,
            "rows!required": None,
        }


def _get_sqlite_type(value):
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


def write_to_database(database: Path, table: str, rows: list[dict]):
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
                col_type = _get_sqlite_type(row[col])
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
