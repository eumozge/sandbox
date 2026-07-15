from unittest.mock import AsyncMock, call

import pytest

from main import Batch, Consumer, PipeProcessor, Producer


class TestPipeProcessor:
    @pytest.mark.parametrize(
        (
            "max_items",
            "batchs",
            "process_items",
        ),
        [
            (
                9,
                [Batch([1, 2, 3], "0"), Batch([4, 5, 6], "1"), Batch([7, 8], "2"), Batch([], "")],
                [[1, 2, 3, 4, 5, 6, 7, 8]],
            ),
            (
                3,
                [Batch([1, 2, 3], "0"), Batch([4, 5, 6], "1"), Batch([7, 8], "2"), Batch([], "")],
                [[1, 2, 3], [4, 5, 6], [7, 8]],
            ),
            (
                4,
                [Batch([1, 2, 3], "0"), Batch([4, 5, 6], "1"), Batch([7, 8], "2"), Batch([], "")],
                [[1, 2, 3], [4, 5, 6], [7, 8]],
            ),
        ],
    )
    async def test_pipe(
        self, max_items: int, batchs: list[Batch[int, str]], process_items: list[int]
    ) -> None:
        producer = AsyncMock(spec=Producer)
        producer.next.side_effect = batchs

        consumer = AsyncMock(spec=Consumer)
        consumer.MAX_ITEMS = max_items

        pipeline = PipeProcessor(producer=producer, consumer=consumer)

        await pipeline.pipe()

        producer.next.assert_called()

        assert consumer.process.mock_calls == [call(items) for items in process_items]
