from LSP.plugin import LspPlugin, OnPreStartContext
from lsp_utils import UvVenvManager
from sublime_lib import ResourcePath

from .lib.utils import resolve_zuban_path, EXE_NAME


class ZubanLSP(LspPlugin):
    @classmethod
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        storage = cls.plugin_storage_path
        py_proj = ResourcePath('Packages', 'LSP-zuban', 'server')
        UvVenvManager.on_pre_start_async(context, storage, py_proj, 'zuban')

        # If user provides just the binary name ("zuban" or "zuban.exe"),
        # and this binary cannot be located with `shutil.which`,
        # try to lookup UV-generated binary in .venv dir.
        # This allows to sporadically update the binary via UV,
        # while reducing frequent web-connections for update checks.
        pth = context.variables['server_path']
        if pth == EXE_NAME:
            context.variables['server_path'] = str(resolve_zuban_path(pth))


def plugin_loaded() -> None:
    ZubanLSP.register()


def plugin_unloaded() -> None:
    ZubanLSP.unregister()
