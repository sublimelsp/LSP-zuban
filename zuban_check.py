import sublime
import sublime_plugin

from pathlib import Path
from dataclasses import dataclass, field
from subprocess import run as shell  # noqa: S404


# sublime.status_message('No errors')
# self.window.run_command('exec', {
#     'cmd': ['zuban', 'check', '.'],
#     'working_dir': self.root,
#     'quiet': True,
# })


@dataclass
class Settings:
    ''' User settings manager '''
    data = sublime.load_settings('LSP-zuban.sublime-settings')

    @classmethod
    def check_cmd(cls) -> Path:
        val: str = cls.data.get('check', {}).get('cmd', 'auto')  # type: ignore
        return Path(val).expanduser()

    @classmethod
    def check_args(cls) -> list[str]:
        return cls.data.get('check', {}).get('args', [])  # type: ignore


#################################################
# Helper
#################################################

def jump_to_line(view: 'sublime.View', line: int) -> None:
    ''' Jump to line in selected tab. '''
    pt = view.text_point(line - 1, 0)
    view.sel().clear()
    view.sel().add(sublime.Region(pt, pt))
    view.show_at_center(pt)


def is_py_tab(view: 'sublime.View|None') -> bool:
    ''' Check if selected tab is a python file. '''
    if not view:
        return False
    return view.settings().get('syntax', '').endswith('Python.sublime-syntax')  # type: ignore[union-attr]


#################################################
# zuban check
#################################################

@dataclass
class Violation:
    desc: str
    fname: Path = Path()
    line: int = -1


@dataclass
class ZubanCheck:
    ''' Parameters passed down to zuban check shell call. '''
    files: list[Path] | list[str] = field(default_factory=lambda: ['.'])
    cwd: Path | None = None
    noName: bool = False

    def run(self) -> list[Violation]:
        ''' Run `zuban check` '''
        extra_args = Settings.check_args()
        args = [Settings.check_cmd(), 'check'] + self.files + extra_args
        out = shell(args, capture_output=True, check=False, cwd=self.cwd)  # noqa: S603
        lines = out.stdout.decode('utf8').splitlines()

        rv: list[Violation] = []
        if '--no-error-summary' in extra_args:
            rv.append(Violation('<current file>'))
        else:
            rv.append(Violation(lines.pop()))  # move last line to first

        root = self.cwd or Path()
        for line in lines:
            fname, lineno, remainder = line.split(':', 2)
            if remainder.startswith(' note: '):
                continue
            path = (root / fname).resolve()

            if self.noName:
                desc = f'L{lineno}:{remainder}'
            else:
                desc = f'{path.name}:{lineno}:{remainder}'
            rv.append(Violation(desc, path, int(lineno)))
        return rv

    def show(self, window: 'sublime.Window') -> None:
        ''' Run command and show results. '''
        try:
            ViolationResultsViewer(window, self.run())
        except Exception as e:
            sublime.error_message(str(e))
            return


class ViolationResultsViewer:
    def __init__(self, window: sublime.Window, data: list[Violation]) -> None:
        self.window = window
        self.data = data
        self.calling_view = window.active_view()
        window.show_quick_panel(
            [x.desc for x in data],
            self.jump_to_file,
            on_highlight=lambda i: self.jump_to_file(i, preview=True),
        )

    def jump_to_file(self, index: int, *, preview: bool = False) -> None:
        if index >= 0:
            err = self.data[index]
            if err.line >= 0:
                self.show_file(err.fname, err.line, preview=preview)
                return
        self._restore_original()

    def _restore_original(self) -> None:
        if self.calling_view and self.calling_view.is_valid():
            self.window.focus_view(self.calling_view)

    def show_file(self, path: Path, line: int, *, preview: bool) -> None:
        if path.is_file():
            if not self._switch_to_already_open_file(path, line):
                self._open_new_file(path, line, preview=preview)

    def _switch_to_already_open_file(self, path: Path, line: int) -> bool:
        for view in self.window.views():
            tab = view.file_name()
            if tab and Path(tab).resolve() == path:
                self.window.focus_view(view)
                jump_to_line(view, line)
                return True
        return False

    def _open_new_file(self, path: Path, line: int, *, preview: bool) -> None:
        if preview:
            view = self.window.open_file(str(path), sublime.TRANSIENT)
        else:
            view = self.window.open_file(str(path))

        def jump() -> None:
            if view.is_valid():
                if view.is_loading():
                    sublime.set_timeout(jump, 50)  # try again
                else:
                    jump_to_line(view, line)
        jump()


#################################################
# Register commands
#################################################

class ZubanCurrentFileCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        # TODO: should we cwd to any `pyproject.toml` in a parent dir?
        if path := self.getPath():
            ZubanCheck([path], noName=True).show(self.window)

    def is_enabled(self) -> bool:
        return is_py_tab(self.window.active_view()) and bool(self.getPath())

    def getPath(self) -> 'str|None':
        return self.window.extract_variables().get('file')


class ZubanOpenFilesCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        if files := self.getPaths():
            ZubanCheck(files).show(self.window)

    def is_enabled(self) -> bool:
        return bool(self.getPaths())

    def getPaths(self) -> list[str]:
        return [
            name for tab in sublime.active_window().views()
            if (name := tab.file_name()) and is_py_tab(tab)
        ]


class ZubanWorkdirCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        if root := self.getPath():
            ZubanCheck(cwd=Path(root)).show(self.window)

    def is_enabled(self) -> bool:
        return bool(self.getPath())

    def getPath(self) -> 'str|None':
        return self.window.extract_variables().get('folder')


class ZubanParentDirCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        if path := self.getPath():
            parents = list(Path(path).parents)
            self.window.show_quick_panel(
                [x.as_posix() for x in parents],
                lambda i: self.parent_selected(parents[i]) if i >= 0 else None,
            )

    def parent_selected(self, path: Path) -> None:
        ZubanCheck(cwd=path).show(self.window)

    def is_enabled(self) -> bool:
        return bool(self.getPath())

    def getPath(self) -> 'str|None':
        return self.window.extract_variables().get('file')
