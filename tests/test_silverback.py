from unittest.mock import patch

import pytest

from lib.liquity import Trove

from tests.liquity_mock import LiquityMock

from silverback_bot_update import add_new_trove, new_trove_details


class MockNewTrove:
    address_borrower = "Address01"
    _borrower = "Address"


liquity = LiquityMock([])
new_trove = MockNewTrove()


@pytest.mark.use_network("ethereum:mainnet:alchemy")
def test_my_ethereum_test(chain):
    assert chain.provider.network.ecosystem.name == "ethereum"


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
@patch.object(LiquityMock, "liquidate")
@patch("lib.liquity.get_eth_price")
@patch.object(LiquityMock, "get_trove_details")
def test_add_new_trove(
    mock_get_trove_details, mock_eth_price, mock_liquidate, test_trove, expected_output
):
    """test add_new_trove"""
    mock_get_trove_details.return_value = test_trove
    mock_eth_price.return_value = 2000
    add_new_trove(new_trove, liquity)
    assert mock_liquidate.called == expected_output


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
@patch.object(LiquityMock, "liquidate")
@patch("lib.liquity.get_eth_price")
@patch.object(LiquityMock, "get_trove_details")
def test_new_trove_details(
    mock_get_trove_details, mock_eth_price, mock_liquidate, test_trove, expected_output
):
    """Test new_trove_details function"""
    mock_get_trove_details.return_value = test_trove
    mock_eth_price.return_value = 2000
    new_trove_details(new_trove, liquity)
    assert mock_liquidate.called == expected_output
