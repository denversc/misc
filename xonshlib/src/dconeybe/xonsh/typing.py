from typing import Protocol, NamedTuple, NewType

class SubprocessSpec(Protocol):
  args: tuple[str]

ExitCode = NewType('ExitCode', int)

Stdout = NewType('Stdout', str)

Stderr = NewType('Stderr', str)

class StdoutStderr(NamedTuple):
  stdout: Stdout | None
  stderr: Stderr | None

class StdoutStderrExitCode(NamedTuple):
  stdout: str | None
  stderr: str | None
  exit_code: ExitCode


# See https://xon.sh/tutorial.html#callable-aliases
CallableAliasResult = (
    None
    | ExitCode
    | Stdout
    | StdoutStderr
    | StdoutStderrExitCode
)
