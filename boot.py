
def reload_plugin() -> None:
    import sys  # noqa: PLC0415

    # remove all previously loaded plugin modules
    p = f'{__package__}.'
    for name in [x for x in sys.modules if x.startswith(p) and x != __name__]:
        del sys.modules[name]


reload_plugin()

from .plugin import *  # type: ignore[misc]  # noqa: E402, F403
