import sublime

from shutil import which
from pathlib import Path

try:
    from LSP.plugin import ST_STORAGE_PATH
except ImportError:
    ST_STORAGE_PATH = ''


if sublime.platform() == 'windows':
    BIN_DIR = 'Scripts'
    EXE_NAME = 'zuban.exe'
else:
    BIN_DIR = 'bin'
    EXE_NAME = 'zuban'


def uv_binary() -> Path:
    ''' Path to UV-managed zuban binary. '''
    return Path(ST_STORAGE_PATH) / 'LSP-zuban' / '.venv' / BIN_DIR / EXE_NAME


def resolve_zuban_path(val: str) -> Path:
    ''' Resolve "auto" and "zuban" binary paths (mostly for `check`). '''
    if ST_STORAGE_PATH:
        if val == 'auto':
            # No need to check for exists, because "auto" is supposed to exist.
            # If not, it should fail in the UI and notify user accordingly.
            return uv_binary()
        if val == EXE_NAME and not which(EXE_NAME):
            exe = uv_binary()
            if exe.is_file():
                return exe
    elif val == 'auto':
        val = EXE_NAME
    return Path(val).expanduser()
