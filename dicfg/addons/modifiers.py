
import base64
import datetime

import os
import re
import subprocess
from pathlib import Path

from dicfg.addons.addon import ModifierAddon
from dicfg.formats import FORMAT_READERS


class FetchModifierError(Exception):
    pass


class IncludeModifierError(Exception):
    pass


class TupleModifierError(Exception):
    pass


class CommandModifierError(Exception):
    pass


class Base64DecodeModifierError(Exception):
    pass


class EnvModifierError(Exception):
    pass


class GitRepoModifierError(Exception):
    pass



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


class PathModifier(ModifierAddon):

    NAME = "path"

    @classmethod
    def modify(cls, value):
        if not isinstance(value, (str, Path)):
            raise TupleModifierError(
                f"Value '{value}' is not a str | Path"
            )
        return Path(value)


class TupleModifier(ModifierAddon):

    NAME = "tuple"

    @classmethod
    def modify(cls, value):
        if not isinstance(value, (list, tuple, set, dict)):
            raise TupleModifierError(
                f"Value '{value}' is not a list | tuple | set | dict"
            )
        return tuple(value)


class SetModifier(ModifierAddon):

    NAME = "set"

    @classmethod
    def modify(cls, value):
        if not isinstance(value, (list, tuple, set, dict)):
            raise TupleModifierError(
                f"Value '{value}' is not a list | tuple | set | dict"
            )
        return set(value)


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



class EnvModifier(ModifierAddon):
    NAME = "env"

    @classmethod
    def modify(cls, var_name):
        value = os.getenv(var_name)
        if value is None:
            raise EnvModifierError(f"Environment variable '{var_name}' not found")
        return value


class GitRepoModifier(ModifierAddon):
    NAME = "gitrepo"

    @classmethod
    def modify(cls, repo_path):
        """
        Given a path to a Git repository, returns a string containing
        the current commit hash and, if the repository is dirty, a " (dirty)" flag.
        """
        repo = Path(repo_path)
        # Check if the repository exists and has a .git directory
        if not repo.exists() or not (repo / ".git").exists():
            raise GitRepoModifierError(
                f"Path '{repo_path}' is not a valid Git repository."
            )

        try:
            # Get the current commit hash
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=str(repo), text=True
            ).strip()
        except Exception as e:
            raise GitRepoModifierError(f"Error retrieving commit hash: {e}")

        try:
            # Check for uncommitted changes using 'git status --porcelain'
            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=str(repo), text=True
            ).strip()
            is_dirty = bool(status_output)
        except Exception as e:
            raise GitRepoModifierError(f"Error checking repository status: {e}")

        # Return the commit hash with a " (dirty)" suffix if changes exist.
        return f"{commit_hash}{' (dirty)' if is_dirty else ''}"
