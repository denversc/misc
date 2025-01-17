import dataclasses

@dataclasses.dataclass(frozen=True)
class FakeSubprocessSpec:
  args: tuple[str]

