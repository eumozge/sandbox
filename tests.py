from unittest.mock import Mock

import pytest

from main import Connect, ImageType, ThumnailProcessor, image_classifier


class TestThumnailProcessor:
    def get_connect(self, image: bytes) -> Mock:
        connect = Mock(spec=Connect)
        connect.is_ready_to_read.side_effect = [True]
        connect.is_ready_to_write.side_effect = [True]
        connect.read.side_effect = [image]
        connect.write.side_effect = [len(image)]
        return connect

    @pytest.mark.parametrize(
        ("image_size", "queue"),
        [
            (1024, ImageType.SMALL),
        ],
    )
    async def test_process(self, image_size: int, queue: ImageType) -> None:
        image = b"0" * image_size
        connect = self.get_connect(image)
        processor = ThumnailProcessor(connects=[connect], image_classifier=image_classifier)
        await processor.process()

        connect.is_ready_to_read.assert_called()
        connect.read.assert_called()
        connect.is_ready_to_write.assert_called()

        connect.write.assert_called_with(image[:4])
