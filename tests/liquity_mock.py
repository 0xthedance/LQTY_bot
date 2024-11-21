import pytest

from lib.liquidation_bot import LiquidationBot


class LiquityMock:
    """Mock LiquityMethods class"""

    def __init__(self, troves) -> None:
        self.troves = troves

    def get_trove_owners_count(self) -> int:
        return len(self.troves)

    def get_multiple_sorted_troves(self, start_ind, n_troves) -> list:
        troves_list = []
        for i in range(start_ind, start_ind - n_troves, -1):
            troves_list.append(self.troves[i])

        return troves_list  # address debt uint256, coll uint256, stake uint256, status uint8, arrayIndex uint128'''

    def batch_liquidate_troves(self, trove_addresses):
        print(f"{trove_addresses} has been liquidated")

    def get_trove_details(self, address):
        return self.troves[1]

    def liquidate(self, address):
        print(f"{address} has been liquidated")


@pytest.fixture
def mock_liquity() -> LiquityMock:
    """Return a function to create LiquityMock instances with different trove lists"""

    def _mock_liquity(troves):
        liquity_mock = LiquityMock(troves)
        return LiquidationBot(liquity=liquity_mock, batch_size=3)

    return _mock_liquity
