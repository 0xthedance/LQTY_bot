import os 

NETWORK_CONFIG = {
    "mainnet": {
        "TROVE_MANAGER": "0xA39739EF8b0231DbFA0DcdA07d7e29faAbCf4bb2",
        "MULTI_TROVE_GETTER": "0xFc92d0E9Fa35df17E3A6d9F40716ca2cE749922B",
        "BORROWER_OPERATIONS": "0x24179CD81c9e782A4096035f7eC97fB8B783e007",
        "FLASHBOT": True,
    },
    "sepolia": {
        "TROVE_MANAGER": "0x9431a9fa3300Cd5Db4733283A864Db3347d89311",
        "MULTI_TROVE_GETTER": "0xA975b76c81686DD2992095Cb9149A3392c63F248",
        "BORROWER_OPERATIONS": "0xe093bC0a552C5cBbE0a07C0094F4AfB6204aa1b9",
        "FLASHBOT": False,
    },
}

# Chainlink address for ETH/USD price feed
ETH_USD_PRICE_FEED = "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"

MIN_CLR = 1.10

# Recipient of liquidation rewards
ACCOUNT_ALIAS = os.environ["ACCOUNT_ALIAS"]

# About 2M gas required to liquidate 10 Troves (much of it is refunded though).
MAX_TROVES_TO_LIQUIDATE = 4


DEFAULT_PRIORITY_FEE = 5 * 10**9
