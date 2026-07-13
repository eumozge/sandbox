from dataclasses import dataclass, field

from pydantic import HttpUrl, TypeAdapter

from domain.common.value_objects import ValueObject


@dataclass(frozen=True)
class URL(ValueObject[str]):
    value: str = field(default_factory=str)

    def validate(self) -> None:
        adapter = TypeAdapter(HttpUrl)
        adapter.validate_python(self.value)
