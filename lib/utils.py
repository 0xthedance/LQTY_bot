import logging

from ape import Contract, chain, accounts, networks
from ape.exceptions import ContractLogicError
from lib.constants import NETWORK_CONFIG


from lib.constants import (
    ACCOUNT_ALIAS,
    ETH_USD_PRICE_FEED,
    DEFAULT_PRIORITY_FEE,
)

account = accounts.load(ACCOUNT_ALIAS)
account.set_autosign(True)

logger = logging.getLogger("my_logger")


def load_network_constants():
    network_name = networks.provider.network.name
    if network_name not in NETWORK_CONFIG:
        raise ValueError(f"Network not supported: {network_name}")

    network_constants = {
        "TROVE_MANAGER": NETWORK_CONFIG[network_name]["TROVE_MANAGER"],
        "MULTI_TROVE_GETTER": NETWORK_CONFIG[network_name]["MULTI_TROVE_GETTER"],
        "BORROWER_OPERATIONS": NETWORK_CONFIG[network_name]["BORROWER_OPERATIONS"],
        "FLASHBOT": NETWORK_CONFIG[network_name]["FLASHBOT"],
    }
    return network_constants


def get_eth_price() -> float:
    """Fetch ETH price in a smart contract Oracle"""
    decimals = 10**8
    with networks.parse_network_choice("ethereum:mainnet:alchemy"):
        contract = Contract(ETH_USD_PRICE_FEED)
        try:
            eth_price = contract.latestRoundData()
            return eth_price.answer / decimals
        except ContractLogicError as err:
            logger.error("Cannot fetch eth price due this error %s", err)
            return -1


def activate_flashbot():
    return load_network_constants()["FLASHBOT"]


def estimate_gas_price() -> int:
    """Function that estimates the actual gas price fetching it from the last block.
    returns gas price in GWei
    Don't pay a priority fee by default when using Flashbots"""
    try:
        block = chain.provider.get_block("latest")  # obtain base fee
    except Exception as err:
        logger.error("Imposible to obtain base fee due an error: %s", err)
        return -1
    if activate_flashbot():
        priority_fee = 0
    else:
        priority_fee = DEFAULT_PRIORITY_FEE
    max_gas_fee = (block.base_fee * 2) + priority_fee
    return max_gas_fee * 10**-9  # convert to Gwei
