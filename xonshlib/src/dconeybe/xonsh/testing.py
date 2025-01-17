import dataclasses

class FakeSubprocessSpec(dataclasses.dataclass(frozen=True)):
  args: tuple[str]

