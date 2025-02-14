import ast
import base64
from dataclasses import dataclass
import datetime
import json
import operator as op
import os
import re
import sqlite3
import subprocess
import uuid
from pathlib import Path

import requests
from dicfg.addons.addon import ModifierAddon
from dicfg.formats import FORMAT_READERS


class MathModifierError(Exception):
    pass


class UUIDv5ModifierError(Exception):
    pass


class FetchModifierError(Exception):
    pass


class IncludeModifierError(Exception):
    pass


class CommandModifierError(Exception):
    pass


class Base64DecodeModifierError(Exception):
    pass


class EnvModifierError(Exception):
    pass


class SQLReadModifierError(Exception):
    pass


# Supported operators
operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg,
}


def safe_eval(expr):
    """
    Safely evaluate a math expression from a string.
    Only allows basic arithmetic operations.
    """

    def eval_node(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
            return operators[type(node.op)](eval_node(node.operand))
        else:
            raise TypeError("Unsupported expression: {}".format(node))

    parsed = ast.parse(expr, mode="eval").body
    return eval_node(parsed)


class IncludeModifier(ModifierAddon):

    NAME = "include"

    @classmethod
    def modify(cls, a):
        if Path(a).suffix in FORMAT_READERS:
            return FORMAT_READERS[Path(a).suffix](a)
        else:
            raise IncludeModifierError(
                f"Unsupported file format {Path(a).suffix} for include modifier {a}"
            )


class CommandModifier(ModifierAddon):
    NAME = "command"

    @classmethod
    def modify(cls, command):
        """Executes a shell command and returns its standard output."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise CommandModifierError(f"Command '{command}' failed: {e.stderr}")


class SlugifyModifier(ModifierAddon):
    NAME = "slugify"

    @classmethod
    def modify(cls, text):
        slug = re.sub(r"\W+", "-", text.lower()).strip("-")
        return slug


class DateModifier(ModifierAddon):
    NAME = "date"

    @classmethod
    def modify(cls, format_str="%Y-%m-%d"):
        return datetime.datetime.now().strftime(format_str)


class FetchModifier(ModifierAddon):
    NAME = "fetch"

    @classmethod
    def modify(cls, url):
        """Fetches and returns content from a remote URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise FetchModifierError(f"Failed to fetch content from {url}: {e}")


class EncodeBase64Modifier(ModifierAddon):
    NAME = "encodebase64"

    @classmethod
    def modify(cls, text):
        """Encodes the given text into Base64."""
        encoded_bytes = base64.b64encode(text.encode("utf-8"))
        return encoded_bytes.decode("utf-8")


class DecodeBase64Modifier(ModifierAddon):
    NAME = "decodebase64"

    @classmethod
    def modify(cls, text):
        """Decodes the given Base64-encoded string."""
        try:
            decoded_bytes = base64.b64decode(text)
            return decoded_bytes.decode("utf-8")
        except Exception:
            raise Base64DecodeModifierError(
                "Invalid Base64 string provided for decoding"
            )


class UUIDv5Modifier(ModifierAddon):
    NAME = "uuid5"

    @classmethod
    def modify(cls, params):
        """
        Expects parameters in the format 'namespace::name'.
        The namespace must be a valid UUID string.
        """
        try:
            namespace_str, name = params.split("::", 1)
            namespace = uuid.UUID(namespace_str)
            return str(uuid.uuid5(namespace, name))
        except Exception:
            raise UUIDv5ModifierError(
                "Invalid parameters for UUIDv5Modifier. Use 'namespace::name'."
            )


class MathModifier(ModifierAddon):
    NAME = "math"

    @classmethod
    def modify(cls, expression):
        try:
            result = safe_eval(expression)
            return result
        except Exception as e:
            raise MathModifierError(f"Error evaluating expression '{expression}': {e}")


class EnvModifier(ModifierAddon):
    NAME = "env"

    @classmethod
    def modify(cls, var_name):
        value = os.getenv(var_name)
        if value is None:
            raise EnvModifierError(f"Environment variable '{var_name}' not found")
        return value


class SQLReaderModifier(ModifierAddon):
    NAME = "sqlread"

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
                output = {str(idx): dict(zip(headers, row)) for idx,row in enumerate(rows)}
            elif output_format == "table":
                # Fallback to simple formatting if tabulate isn't installed
                header_line = " | ".join(headers)
                row_lines = "\n".join(
                    " | ".join(str(cell) for cell in row) for row in rows
                )
                output = header_line + "\n" + row_lines
            elif output_format == "json":
                json_rows = [dict(zip(headers, row)) for row in rows]
                output =  json.dumps(json_rows, indent=2)
            else:
                output = str(rows)
            return {'data': output}
        except sqlite3.Error as e:
            raise SQLReadModifierError(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
