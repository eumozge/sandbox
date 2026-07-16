import asyncio
import datetime as dt

import pytest

from main import Amenity, Booking, Room, SearchRequest, SearchRoomServiceImpl, SimpleRoomRepository


class TestSearchRoomServiceImpl:
    @pytest.mark.parametrize(
        ("search_request", "rooms", "reference_ids"),
        [
            (
                SearchRequest(
                    dt.date(2025, 1, 20),
                    days=5,
                    guests=2,
                    budget=500,
                    amenities={Amenity.wifi, Amenity.tv},
                ),
                [
                    Room(
                        id=0,
                        price=100,
                        capacity=2,
                        amenities={Amenity.wifi, Amenity.tv},
                        bookings=[],
                    ),
                    Room(
                        id=1,
                        price=100,
                        capacity=3,
                        amenities={Amenity.wifi},
                        bookings=[Booking(dt.date(2025, 1, 25), dt.date(2025, 2, 21))],
                    ),
                ],
                [0],
            ),
        ],
    )
    async def test_find_rooms_by_request(
        self, search_request: SearchRequest, rooms: list[Room], reference_ids: set[int]
    ) -> None:
        room_repository = SimpleRoomRepository(rooms)
        search_service = SearchRoomServiceImpl(room_repository)

        filtered_rooms = await search_service.find_rooms_by_request(search_request)
        filtered_ids = [room.id for room in filtered_rooms]
        assert filtered_ids == reference_ids

    async def test_book_room(self) -> None:
        room = Room(
            id=0,
            price=100,
            capacity=1,
            amenities=set(),
            bookings=[],
        )
        room_repository = SimpleRoomRepository([room])
        search_service = SearchRoomServiceImpl(room_repository)

        tasks = [
            search_service.book_room(room.id, dt.date(2025, 1, 15), days=5),
            search_service.book_room(room.id, dt.date(2025, 1, 18), days=5),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        assert len(room.bookings) == 1

