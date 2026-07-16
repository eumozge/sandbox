import abc
import asyncio
from collections import defaultdict
import contextlib
from dataclasses import dataclass
import datetime as dt
from email.policy import default
import typing
from uuid import UUID

type UID = int
type Amount = int
type Banknote = int
type BanknoteCount = int
type Time = dt.datetime


@dataclass
class Booking:
    user_id: UID
    amount: Amount
    banknotes: list[tuple[Banknote, BanknoteCount]]
    to_time: Time

    cancel_task: asyncio.Task | None = None


BANKNOTES: tuple[Banknote, ...] = (50, 100, 500, 1000, 5000)


class SDK(abc.ABC):
    @abc.abstractmethod
    def count_banknotes(self, banknote: int) -> int: ...

    @abc.abstractmethod
    def move_banknote_to_dispenser(self, banknote: int, count: int) -> None:
        pass

    @abc.abstractmethod
    def open_dispenser(self) -> None:
        pass

    @abc.abstractmethod
    def close_dispenser(self) -> None:
        pass


class HardwareError(Exception): ...


class FatalError(Exception): ...


class ATM(abc.ABC):
    def __init__(self, sdk: SDK) -> None:
        self.sdk = sdk
        self.storage: dict[Banknote, BanknoteCount] = {}

    @abc.abstractmethod
    def setup(self) -> None: ...

    @abc.abstractmethod
    def teardown(self) -> None: ...

    @abc.abstractmethod
    def withdraw(self, amount: Amount) -> None: ...


class ATMImpl(ATM):
    def setup(self) -> None:
        self.storage = {d: self.sdk.count_banknotes(d) for d in BANKNOTES}
        self.booking: dict[UID, Booking] = {}

    def has_booking(self, user_id: UID) -> bool:
        return user_id in self.booking

    async def cancel_task(self, booking: Booking) -> None:
        assert dt.datetime.now(tz=dt.UTC) < Booking.to_time
        delta = (Booking.to_time - dt.datetime.now(tz=dt.UTC))
        await asyncio.sleep(delta.total_seconds())

        if booking.user_id is not self.booking:
            return

        self.withdrow_increment(booking.banknotes)

    def book(self, user_id: int, amount: Amount, to_time: Time) -> Booking:
        banknotes = self.get_withdrow(amount)
        booking = Booking(user_id, amount, banknotes, to_time)
        booking.cancel_task = asyncio.create_task(self.cancel_task(booking))
        self.booking[user_id] = booking
        return booking

    def teardown(self) -> None: ...

    def get_withdrow(self, amount: Amount) -> list[tuple[Banknote, BanknoteCount]]:
        withdrow_banknotes = []
        for banknote in BANKNOTES[::-1]:
            available = self.storage[banknote]
            necessery = amount // banknote
            count = min(available, necessery)
            if count:
                amount -= count * banknote
                withdrow_banknotes.append((banknote, count))

        if amount != 0:
            return []

        return withdrow_banknotes

    def withdrow_decrement(self, banknotes: list[tuple[Banknote, BanknoteCount]]) -> None:
        for banknnote, banknote_count in banknotes:
            self.storage[banknnote] -= banknote_count

    def withdrow_increment(self, banknotes: list[tuple[Banknote, BanknoteCount]]) -> None:
        for banknnote, banknote_count in banknotes:
            self.storage[banknnote] += banknote_count

    def withdraw(self, amount: Amount, user_id: UID | None = None) -> None:
        if user_id is not None and self.has_booking(user_id):
            booking = self.booking[user_id]
            assert booking.cancel_task
            booking.cancel_task.cancel()
            banknotes = booking.banknotes
        else:
            banknotes = self.get_withdrow(amount)

        if not banknotes:
            raise ValueError

        try:
            for banknote, banknote_count in banknotes:
                self.sdk.move_banknote_to_dispenser(banknote, banknote_count)
            self.sdk.open_dispenser()
            if user_id and self.has_booking(user_id):
                del self.booking[user_id]
        except FatalError:
            self.teardown()
        except HardwareError:
            with contextlib.suppress(FatalError):
                self.sdk.close_dispenser()
                self.teardown()
        else:
            self.withdrow_decrement(banknotes)
