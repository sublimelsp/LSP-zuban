LSP-zuban for Sublime Text
==========================

This plugin provides LSP bindings to [zuban](https://github.com/zubanls/zuban) type checker (Python).

Additionally, it provides commands to manually `zuban check` individual files/folders (via Command Palette).

`zuban` **must** be installed for this plugin to work (single Rust binary, installable via `pip`).


### Installation

- Install `LSP` and `LSP-zuban` from Package Control.
- Optionally: change path to `zuban` binary in the plugin settings (`zuban: Settings`).
- Restart Sublime Text.


### What it does

This plugin adds commands to run `zuban check` manually on various files and folders:

```
zuban: check Current File
zuban: check Open Files
zuban: check Work-dir
zuban: check Parent-dir
```

Plus, a simple wrapper for an LSP server:

```json
"zuban": {
  "enabled": true,
  "command": ["zuban", "server"],
  "selector": "source.python",
}
```
