import time

from ape.types import ContractLog


from silverback import SilverbackBot

from lib.liquidation_bot import LiquidationBot
from lib.liquity import LiquityMethods
from lib.logging import configure_logging
from lib.utils import load_network_constants
from lib.constants import NETWORK_CONFIG

bot = SilverbackBot()

network_constants = load_network_constants()

print(network_constants["BORROWER_OPERATIONS"])
print(network_constants["TROVE_MANAGER"])


liquity = LiquityMethods(network_constants["TROVE_MANAGER"], network_constants["MULTI_TROVE_GETTER"], network_constants["BORROWER_OPERATIONS"])
LQTY_bot = LiquidationBot(liquity, batch_size=10)

logger = configure_logging()


@bot.on_startup()
def start_bot(startup_state):
    """Launch liquidation bot once upon every application startup."""
    while True:
        try:
            LQTY_bot.run_bot()
        except Exception as err:
            logger.error("the bot exited due to an error: %s", err)

        logger.info("sleeping")
        time.sleep(120)


@bot.on_(liquity.borrower_operations.TroveCreated)
def add_new_trove(new_trove: ContractLog, liquity) -> None:
    """Function that executes the necessary actions when a new trove is created
    new_trove (ContractLog): Information from the contract log corresponding to the newly created trove.
    """
    logger.info("A trove has been created")
    address = new_trove._borrower
    logger.info("A new trove %s has been created", address)
    trove = liquity.get_trove_details(address)
    if trove == 0:
        return
    if trove.check():
        liquity.liquidate(trove.address)


@bot.on_(liquity.borrower_operations.TroveUpdated)
def new_trove_details(trove_details: ContractLog, liquity) -> None:
    """Function that executes the necessary actions when a new trove is updated
    Arg: trove_details(ContractLog): Information from the contract log corresponding to the updated trove.
    """
    address = trove_details._borrower
    logger.info("trove %s has been updated", address)
    trove = liquity.get_trove_details(address)
    if trove == 0:
        return
    if trove.check():
        liquity.liquidate(trove.address)
