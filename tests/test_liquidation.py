from unittest.mock import patch, call

import pytest

from lib.liquidation_bot import LiquidationBot
from lib.liquity import Trove

from tests.liquity_mock import LiquityMock, mock_liquity


class LiquityTrove:
    """Mock Trove class"""

    def __init__(self, owner, coll, debt) -> None:
        self.owner = owner
        self.coll = coll
        self.debt = debt


troves_list = [
    LiquityTrove("0xAddress1", coll=100 * 10**18, debt=3500 * 10**18),
    LiquityTrove("0xAddress2", coll=150 * 10**18, debt=10000 * 10**18),
    LiquityTrove("0xAddress3", coll=5 * 10**18, debt=3000 * 10**18),
    LiquityTrove("0xAddress4", coll=20 * 10**18, debt=8000 * 10**18),
    LiquityTrove("0xAddress5", coll=1000 * 10**18, debt=1000000 * 10**18),
    LiquityTrove("0xAddress6", coll=350000 * 10**18, debt=900000000 * 10**18),
    LiquityTrove("0xAddress7", coll=0.5 * 10**18, debt=4000 * 10**18),
]
troves_total_liquidation = [
    Trove("0xAddress7", coll=0.5 * 10**18, debt=4000 * 10**18),
    Trove("0xAddress6", coll=350000 * 10**18, debt=900000000 * 10**18),
    Trove("0xAddress5", coll=1000 * 10**18, debt=1000000 * 10**18),
    Trove("0xAddress4", coll=20 * 10**18, debt=8000 * 10**18),
    Trove("0xAddress3", coll=5 * 10**18, debt=3000 * 10**18),
    Trove("0xAddress2", coll=150 * 10**18, debt=10000 * 10**18),
    Trove("0xAddress1", coll=100 * 10**18, debt=3500 * 10**18),
]

troves_partial_liquidation = [
    Trove("0xAddress7", coll=0.5 * 10**18, debt=4000 * 10**18),
    Trove("0xAddress6", coll=350000 * 10**18, debt=900000000 * 10**18),
]


@pytest.mark.use_network("ethereum:mainnet:alchemy")
@pytest.mark.parametrize(
    "test_trove,expected_output",
    [
        (
            Trove("0xAddress1", coll=0.5 * 10**18, debt=5000 * 10**18),
            True,
        ),  # liquidation case
        (Trove("0xAddress1", coll=5.5 * 10**18, debt=5000 * 10**18), False),
        (Trove("0xAddress1", coll=5.5 * 10**18, debt=0), False),
    ],
)
@patch("lib.liquity.get_eth_price")
def test_check(mock_get_eth_price, test_trove, expected_output, networks):
    mock_get_eth_price.return_value = 2000
    assert test_trove.check() == expected_output


@pytest.mark.use_network("ethereum:mainnet:alchemy")
@pytest.mark.parametrize(
    "price,expected_output",
    [
        (30, troves_total_liquidation),  # All troves
        (1500, troves_partial_liquidation),
        (10000, []),  # No troves
    ],
)
@patch("lib.liquity.get_eth_price")
def test_get_trove_list(mock_eth_price, mock_liquity, price, expected_output):
    # mocks the get_eth_price response
    mock_eth_price.return_value = price

    # Create a LiquidationBot with the mocked liquity
    bot = mock_liquity(troves_list)

    # Call the method
    result = bot.get_trove_list()

    # Assert that the length of the result matches the expected output
    assert result == expected_output


@pytest.mark.use_network("ethereum:mainnet:alchemy")
@pytest.mark.parametrize(
    "mock_gas_response,address_liquidated",
    [
        (
            1,
            ["0xAddress4", "0xAddress7", "0xAddress6", "0xAddress5"],
        ),  # the compensation is higher than the gas, batch_liquidate_troves is called
        (8, ["0xAddress4", "0xAddress7", "0xAddress6"]),
        (
            15,
            [],
        ),  # the compensation is lower than the gas, batch_liquidate_troves is not called
    ],
)
@patch.object(LiquityMock, "batch_liquidate_troves")
@patch("lib.liquidation_bot.estimate_gas_price")
def test_liquidate_list_of_troves(
    mock_gas_estimation,
    mock_batch_liquidate,
    mock_liquity,
    mock_gas_response,
    address_liquidated,
):
    mock_gas_estimation.return_value = mock_gas_response
    bot = mock_liquity(troves_list)
    troves = [
        Trove("0xAddress4", coll=2 * 10**18, debt=900 * 10**18),
        Trove("0xAddress7", coll=0.5 * 10**18, debt=900 * 10**18),
        Trove("0xAddress6", coll=0.4 * 10**18, debt=8000 * 10**18),
        Trove("0xAddress5", coll=0.1 * 10**18, debt=2000 * 10**18),
    ]

    bot.liquidate_list_of_troves(troves)

    if mock_gas_response == 15:
        mock_batch_liquidate.assert_not_called()
    else:
        mock_batch_liquidate.assert_called_once_with(address_liquidated)


@pytest.mark.use_network("ethereum:mainnet:alchemy")
@pytest.mark.parametrize(
    "troves_selected, expected_calls, calls",
    [
        ([], 0, []),
        (
            troves_total_liquidation,
            2,
            [
                call(
                    [
                        Trove(
                            "0xAddress6", coll=350000 * 10**18, debt=900000000 * 10**18
                        ),
                        Trove("0xAddress5", coll=1000 * 10**18, debt=1000000 * 10**18),
                        Trove("0xAddress2", coll=150 * 10**18, debt=10000 * 10**18),
                        Trove("0xAddress1", coll=100 * 10**18, debt=3500 * 10**18),
                    ]
                ),
                call(
                    [
                        Trove("0xAddress4", coll=20 * 10**18, debt=8000 * 10**18),
                        Trove("0xAddress3", coll=5 * 10**18, debt=3000 * 10**18),
                        Trove("0xAddress7", coll=0.5 * 10**18, debt=4000 * 10**18),
                    ]
                ),
            ],
        ),
        (
            troves_partial_liquidation,
            1,
            [
                call(
                    [
                        Trove(
                            "0xAddress6", coll=350000 * 10**18, debt=900000000 * 10**18
                        ),
                        Trove("0xAddress7", coll=0.5 * 10**18, debt=4000 * 10**18),
                    ]
                )
            ],
        ),
    ],
)
@patch.object(LiquidationBot, "liquidate_list_of_troves")
@patch.object(LiquidationBot, "get_trove_list")
def test_run_bot(
    mock_trove_selected,
    mock_liquidation,
    mock_liquity,
    troves_selected,
    expected_calls,
    calls,
):
    mock_trove_selected.return_value = troves_selected

    bot = mock_liquity(troves_list)
    bot.run_bot()
    assert mock_liquidation.call_count == expected_calls
    if expected_calls > 0:
        mock_liquidation.assert_has_calls(calls)
