import logging


from lib.liquity import Trove, LiquityMethods
from lib.utils import estimate_gas_price
from lib.constants import MAX_TROVES_TO_LIQUIDATE

logger = logging.getLogger("my_logger")


class LiquidationBot:
    def __init__(self, liquity: LiquityMethods, batch_size) -> None:
        self.liquity = liquity
        self.batch_size = batch_size

    def get_trove_list(self) -> list[Trove]:
        """Function to obtain the list of troves with a CR below MIN_CLR"""
        trove_count = self.liquity.get_trove_owners_count()
        n_troves = self.batch_size
        start_ind = -1
        more_troves = trove_count > 0
        selected = []

        while more_troves:
            logger.info("fetching %s troves", n_troves)

            if trove_count < n_troves:
                n_troves = trove_count
                more_troves = False

            trove_details = self.liquity.get_multiple_sorted_troves(start_ind, n_troves)
            logger.debug(" %s troves obtained", trove_details)

            if trove_details == 0:
                break

            start_ind -= self.batch_size
            trove_count -= self.batch_size

            for trove in trove_details:
                trove = Trove(trove.owner, trove.coll, trove.debt)
                if not trove.check():
                    logger.debug(trove.check())
                    more_troves = False
                    break
                selected.append(trove)

        logger.info("troves with CR below the minimum:%s", selected)
        return selected

    def liquidate_list_of_troves(self, selected: list[Trove]) -> None:
        """Function that liquidate the troves if the transaction is profitable"""
        """ Rough gas requirements:
            `500K + n * 200K` should cover all cases
            (including starting in recovery mode and ending in
            normal mode) with some margin for safety.
        """
        gas = estimate_gas_price()
        if gas < 0:
            logger.info("It was not possible to proceed with the liquidation")
            return
        logger.info("Gas price: %s", gas)
        compensation = 0
        cost_initial = (500 * 10**3 * gas) * 10**-9  # ETH
        cost_per_trove = (200 * 10**3 * gas) * 10**-9
        last_revenue = -cost_initial
        troves_to_liquidate = []
        for trove in selected:
            compensation = trove.estimate_compensation()
            logger.debug(" coll %s", trove.coll)
            logger.debug("compensation %s", compensation)
            logger.debug("last rev %s", last_revenue)
            new_revenue = last_revenue + compensation - cost_per_trove
            logger.debug("  --> new %s", new_revenue)
            if new_revenue < last_revenue:
                break
            troves_to_liquidate.append(trove)
            last_revenue = new_revenue
        logger.debug("last revenue %s", last_revenue)
        if last_revenue > 0:
            trove_addresses = []
            logger.info(
                "Sending to liquidate the following troves %s", troves_to_liquidate
            )
            for trove in troves_to_liquidate:
                trove_addresses.append(trove.address)
            self.liquity.batch_liquidate_troves(trove_addresses)
        else:
            logger.info(
                "It is not profitable to liquidate troves. The collateral is insufficient, and there is no benefit from this operation."
            )

    def run_bot(self):
        """Launch the bot"""
        logger.info("starting the check")
        selected = self.get_trove_list()
        if len(selected) <= 0:
            logger.info("Nothing to liquidate")
        else:
            selected.sort(
                key=lambda x: x.coll, reverse=True
            )  # sort by descending collateral
            for i in range(0, len(selected), MAX_TROVES_TO_LIQUIDATE):
                self.liquidate_list_of_troves(selected[i: i + MAX_TROVES_TO_LIQUIDATE])
