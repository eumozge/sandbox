from dataclasses import dataclass, field
from uuid import UUID, uuid4

from domain.common.value_objects import ValueObject


@dataclass(frozen=True)
class ID(ValueObject[UUID]):
    value: UUID = field(default_factory=uuid4)

    def validate(self) -> None:
        pass
