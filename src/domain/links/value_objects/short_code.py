from dataclasses import dataclass, field

from domain.common.value_objects import ValueObject


@dataclass(frozen=True)
class ShortCode(ValueObject[str]):
    value: str = field(default_factory=str)

    def __composite_values__(self) -> tuple[str]:
        return (self.value,)

    def validate(self) -> None:
        pass
