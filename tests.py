from unittest.mock import Mock

import pytest

from main import SDK, ATMImpl, BanknoteCount, Banknote


class TestATMImpl:
    @pytest.mark.parametrize(
        ("amount", "init_banknotes", "remainig_banknotes"),
        [
            (
                7850,
                [(50, 5), (100, 5), (500, 5), (1000, 2), (5000, 1)],
                {(50, 4), (100, 2), (500, 4), (1000, 0), (5000, 0)},
            ),
        ],
    )
    def test_withdraw__success(
        self,
        amount: int,
        init_banknotes: list[tuple[Banknote, BanknoteCount]],
        remainig_banknotes: set[tuple[Banknote, BanknoteCount]],
    ) -> None:
        sdk = Mock(spec=SDK)
        sdk.count_banknotes.side_effect = [count for _, count in init_banknotes]
        atm = ATMImpl(sdk)
        atm.setup()

        atm.withdraw(amount)

        atm.teardown()

        assert atm.storage == dict(remainig_banknotes)

    @pytest.mark.parametrize(
        ("amount", "count_banknotes"),
        [],
    )
    def test_withdraw__fail(
        self, amount: int, count_banknotes: list[tuple[Banknote, BanknoteCount]]
    ) -> None: ...
