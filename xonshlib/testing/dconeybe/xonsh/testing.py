from collections.abc import Sequence
import dataclasses

@dataclasses.dataclass
class FakeSubprocessSpec:
  args: Sequence[str]

