try:
    from LSP.plugin import LspPlugin  # type: ignore[import-not-found]
    useLSP = True
except ImportError:
    useLSP = False


if useLSP:
    class ZubanLSP(LspPlugin):
        pass

    def plugin_loaded() -> None:
        ZubanLSP.register()

    def plugin_unloaded() -> None:
        ZubanLSP.unregister()
