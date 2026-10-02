LSP-zuban for Sublime Text
==========================

This plugin provides LSP bindings to [zuban](https://github.com/zubanls/zuban) type checker (Python).

Additionally, it provides commands to manually `zuban check` individual files/folders (via Command Palette).


### Installation

- Install `LSP` and `LSP-zuban` from Package Control.
- Optionally: change path to `zuban` binary in the plugin settings (`LSP-zuban: Settings`).
- Restart Sublime Text.


### What it does

This plugin adds commands to run `zuban check` manually on various files and folders:

```
LSP-zuban: check Current File
LSP-zuban: check Open Files
LSP-zuban: check Work-dir
LSP-zuban: check Parent-dir
```

Plus, a simple wrapper for the LSP server.
You *could* also use this manual config without this plugin:

```json
"zuban": {
  "enabled": true,
  "command": ["zuban", "server"],
  "selector": "source.python",
}
```
