import asyncio
from abc import ABC, abstractmethod
from asyncio import Lock
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum


class Amenity(StrEnum):
    wifi = "wifi"
    ac = "ac"
    tv = "tv"


@dataclass
class SearchRequest:
    from_date: date
    days: int
    guests: int
    budget: int
    amenities: set[Amenity]


@dataclass
class Booking:
    from_date: date
    to_date: date


@dataclass
class Room:
    id: int
    price: int
    capacity: int
    amenities: set[Amenity]
    bookings: list[Booking]


class RoomRepository(ABC):
    @abstractmethod
    async def find_all(self) -> list[Room]:
        pass

    @abstractmethod
    async def find_by_id(self, room_id: int) -> Room | None:
        pass


class SearchRoomService(ABC):
    @abstractmethod
    async def find_rooms_by_request(self, request: SearchRequest) -> list[Room]:
        pass


class LockManager(ABC):
    @abstractmethod
    @asynccontextmanager
    async def lock(self, room_id: int) -> AsyncIterator:
        yield


class PoolLockManagerImpl(LockManager):
    def __init__(self, pool_size: int = 512) -> None:
        self.size = pool_size
        self.locks = [Lock() for _ in range(self.size)]

    @asynccontextmanager
    async def lock(self, room_id: int) -> AsyncIterator:
        idx = room_id % self.size
        async with self.locks[idx]:
            yield


class SimpleRoomRepository(RoomRepository):
    def __init__(self, rooms: list[Room]) -> None:
        super().__init__()
        self.rooms = rooms
        self.map = {room.id: room for room in rooms}

    async def find_all(self) -> list[Room]:
        return self.rooms

    async def find_by_id(self, room_id: int) -> Room | None:
        return self.map.get(room_id)


class SearchRoomServiceImpl(SearchRoomService):
    def __init__(
        self, room_repository: RoomRepository, lock_manager: LockManager | None = None
    ) -> None:
        self.room_repository = room_repository
        self.lock_manager = lock_manager or PoolLockManagerImpl()

    async def find_rooms_by_request(self, request: SearchRequest) -> list[Room]:
        filtered_rooms = []
        rooms = await self.room_repository.find_all()
        for room in rooms:
            if room.capacity < request.guests:
                continue

            if room.price * request.days > request.budget:
                continue

            if request.amenities - room.amenities:
                continue

            if self.has_booking(request.from_date, request.days, room.bookings):
                continue

            filtered_rooms.append(room)

        return filtered_rooms

    def has_booking(self, from_date: date, days: int, bookings: list[Booking]) -> bool:
        to_date = from_date + timedelta(days=days)
        for booking in bookings:
            if max(from_date, booking.from_date) < min(to_date, booking.to_date):
                return True
        return False

    async def book_room(self, room_id: int, from_date: date, days: int) -> Booking:
        to_date = from_date + timedelta(days=days)
        room = await self.room_repository.find_by_id(room_id)
        assert room is not None

        async with self.lock_manager.lock(room_id):
            await asyncio.sleep(1)
            if self.has_booking(from_date, days, room.bookings):
                raise ValueError
            booking = Booking(from_date, to_date)
            room.bookings.append(booking)

        return booking
