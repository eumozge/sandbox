from dataclasses import dataclass, field

from domain.common.value_objects import ValueObject


@dataclass(frozen=True)
class ShortCode(ValueObject[str]):
    value: str = field(default_factory=str)

    def validate(self) -> None:
        pass
