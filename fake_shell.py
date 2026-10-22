"""FakeShell: a custom Strands sandbox with a simulated shell and an in-memory filesystem."""

import posixpath
import shlex

from strands.sandbox import ExecutionResult, FileInfo, Sandbox
from strands.vended_tools import make_file_editor, make_shell

HOME = "/home/agent"


class FakeShell(Sandbox):
    def __init__(self):
        self.files = {f"{HOME}/welcome.txt": b"Welcome to FakeShell! Type `help` to see what you can do.\n"}

    def path(self, p):
        return posixpath.normpath(posixpath.join(HOME, p))

    # shell 
    async def execute_streaming(self, command, **kwargs):
        words = shlex.split(command)
        redirect_to = None
        if ">" in words:  # `echo hi > notes.txt` writes the output into a file
            redirect_to = words[words.index(">") + 1]
            words = words[: words.index(">")]

        name, args = words[0], words[1:]
        if name not in COMMANDS:
            yield ExecutionResult(exit_code=127, stdout="", stderr=f"fakeshell: {name}: command not found\n")
            return
        try:
            output = COMMANDS[name](self, *args)
        except KeyError as missing:
            yield ExecutionResult(exit_code=1, stdout="", stderr=f"{name}: {missing.args[0]}: No such file\n")
            return
        except Exception as error:
            yield ExecutionResult(exit_code=1, stdout="", stderr=f"{name}: {error}\n")
            return

        if redirect_to:
            await self.write_text(redirect_to, output)
            output = ""
        yield ExecutionResult(exit_code=0, stdout=output, stderr="")

    async def execute_code_streaming(self, code, language, **kwargs):
        yield ExecutionResult(exit_code=127, stdout="", stderr=f"FakeShell has no {language} interpreter.\n")

    # filesystem 
    async def read_file(self, path, **kwargs):
        if self.path(path) not in self.files:
            raise FileNotFoundError(path)
        return self.files[self.path(path)]

    async def write_file(self, path, content, **kwargs):
        self.files[self.path(path)] = content

    async def remove_file(self, path, **kwargs):
        if self.files.pop(self.path(path), None) is None:
            raise FileNotFoundError(path)

    async def list_files(self, path, **kwargs):
        folder = self.path(path).rstrip("/") + "/"
        names = {p[len(folder):].split("/")[0] for p in self.files if p.startswith(folder)}
        return [FileInfo(name=n, is_dir=f"{folder}{n}" not in self.files) for n in sorted(names)]

    # tools
    def get_tools(self):
        return [make_shell(sandbox=self, name="sandbox_shell"), make_file_editor(sandbox=self, name="sandbox_file_editor")]


# shell commands
def ls(os, folder=HOME):
    return "".join(p[len(HOME) + 1:] + "\n" for p in sorted(os.files) if p.startswith(os.path(folder)))

def cat(os, *paths):
    return "".join(os.files[os.path(p)].decode() for p in paths)

def echo(os, *words):
    return " ".join(words) + "\n"

def rm(os, *paths):
    for p in paths:
        del os.files[os.path(p)]
    return ""

def uname(os):
    return "FakeShell 1.0 (a simulated shell; files live in memory)\n"

def help(os):
    return "Commands: " + " ".join(sorted(COMMANDS)) + "\n"


COMMANDS = {"ls": ls, "cat": cat, "echo": echo, "rm": rm, "uname": uname, "help": help}
