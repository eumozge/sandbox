from typing import Any

from sqlalchemy.engine import Dialect
from sqlalchemy.types import UUID as SA_UUID, String, TypeDecorator

from domain.links.value_objects.id import ID
from domain.links.value_objects.url import URL


class IDColumn(TypeDecorator):
    impl = SA_UUID
    cache_ok = True

    def process_bind_param(self, value: ID | None, _dialect: Dialect) -> Any:
        return value.value if value is not None else None

    def process_result_value(self, value: Any, _dialect: Dialect) -> ID | None:
        return ID(value=value) if value is not None else None


class URLColumn(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value: URL | None, _dialect: Dialect) -> Any:
        return value.value if value is not None else None

    def process_result_value(self, value: Any, _dialect: Dialect) -> URL | None:
        return URL(value=value) if value is not None else None
