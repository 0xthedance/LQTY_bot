import logging

from ape.exceptions import ContractLogicError, OutOfGasError
from ape import Contract

from lib.utils import get_eth_price, estimate_gas_price, account, activate_flashbot
from lib.constants import MIN_CLR


logger = logging.getLogger("my_logger")


class Trove:
    '''Class to create LQTY trove instances'''

    def __init__(self, address: str, coll: int, debt: int) -> None:
        self.address = address
        self.coll = coll
        self.debt = debt

    def __repr__(self) -> str:

        return f"Trove(address='{self.address}', coll={self.coll}, debt={self.debt})"

    def __eq__(self, other_test_class):
        if not isinstance(other_test_class, Trove):
            return False
        return (
            (self.address == other_test_class.address)
            and (self.coll == other_test_class.coll)
            and (self.debt == other_test_class.debt)
        )

    def check(self) -> bool:
        '''Funtion to check if CR is below the threshold'''
        if self.debt == 0:
            return False
        
        eth_price = get_eth_price()

        if eth_price < 0:
            return False

        coll_ratio = (self.coll * eth_price) / (self.debt)
        logger.info("price %s{} CR %s",eth_price,coll_ratio)

        return coll_ratio < MIN_CLR

    def estimate_compensation(self) -> float:
        """returns trove liquidation compensation in ETH"""
        decimals = 10**18
        return 5 * (10**-3) * (self.coll / decimals)


class LiquityMethods:
    '''Class containing the LQTY methods'''
    def __init__(self, trove_manager_address, multi_trove_getter_address, borrower_operations_address) -> None:
        self.trove_manager = Contract(trove_manager_address)
        self.multi_trove_getter = Contract(multi_trove_getter_address)
        self.borrower_operations = Contract(borrower_operations_address)

    def get_trove_owners_count(self) -> int:
        """Query trove manager to fetch number of troves in the protocol"""
        try:
            return self.trove_manager.getTroveOwnersCount()
        except ContractLogicError as err:
            logger.error("Cannot fetch trove count due this error %s", err)
            return 0

    def get_multiple_sorted_troves(self, start_ind, n_troves) -> list:
        """Query MultiTroveGetter to fecth n_troves starting in start_ind"""
        try:
            return self.multi_trove_getter.getMultipleSortedTroves(
                start_ind, n_troves
            )  # address debt, coll, stake, status, arrayIndex
        except ContractLogicError as err:
            logger.error("Cannot fetch troves due this error %s", err)
            return 0

    def batch_liquidate_troves(self, trove_addresses):
        """Call trove manager contract to liquidate a batch of trove_addresses"""
        logger.info("   %s",trove_addresses)

        try:
            self.trove_manager.batchLiquidateTroves(
                trove_addresses, sender=account, private=activate_flashbot()
            )
        except ContractLogicError as err:
            logger.error(
                "It was not possible to liquidate the troves batch due the following error: %s",
                err,
            )
        except OutOfGasError:
            logger.critical(
                "Out of gas. Exiting Liquidation bot: %s",
                err,
            )
            exit()

    def get_trove_details(self, address) -> Trove:
        """Call trove manager contract to obtain the details (call and debt) from an owner address"""

        try:
            trove_details = self.trove_manager.getEntireDebtAndColl(address)
            trove = Trove(address, trove_details.coll, trove_details.debt)
            return trove
        except ContractLogicError as err:
            logger.error(err)
            return 0

    def liquidate(self, trove) -> None:
        """Call trove manager contract to liquidate a single trove"""
        gas = estimate_gas_price()
        if gas < 0:
            logger.info("It was not possible to proceed with the liquidation")
            return
        compensation = trove.estimate_compensation()
        cost = ((500 * 10**3) + (200 * 10**3) * gas) * 10**-9
        rev = compensation - cost
        if rev > 0:
            try:
                self.trove_manager.liquidate(
                    trove.address, sender=account, private=activate_flashbot()
                )  # private to send it through Flashbots.Alchemy already supports it.
                logger.info(
                    "The following trove %s has been liquidated with a compensation of %s",
                    trove.address,
                    compensation,
                )
            except ContractLogicError as err:
                logger.error("It was not possible to liquidate the trove due a contract error %s",err)
            
            except OutOfGasError:
                logger.critical(
                    "Out of gas. Exiting Liquidation bot: %s",
                    err,
                )
                exit()
