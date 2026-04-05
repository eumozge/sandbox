from collections.abc import Sequence
from dataclasses import dataclass, field


type HTML = str


@dataclass
class OilProduct:
    name: str
    code: str


@dataclass
class Trade:
    product: OilProduct
    volume: int
    price: float
    total: float


@dataclass
class Page:
    pid: str
    body: HTML
    status: int
    trades: Sequence[Trade] = field(default_factory=list)
