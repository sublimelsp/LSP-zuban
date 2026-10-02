from LSP.plugin import LspPlugin, OnPreStartContext
from lsp_utils import UvVenvManager
from sublime_lib import ResourcePath


class ZubanLSP(LspPlugin):
    @classmethod
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        storage = cls.plugin_storage_path
        py_proj = ResourcePath('Packages', 'LSP-zuban', 'server')
        UvVenvManager.on_pre_start_async(context, storage, py_proj, 'zuban')


def plugin_loaded() -> None:
    ZubanLSP.register()


def plugin_unloaded() -> None:
    ZubanLSP.unregister()
