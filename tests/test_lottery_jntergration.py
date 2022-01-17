from brownie import Lottery, accounts, network, exceptions
from scripts.helpful_scripts import (
    get_account,
    fund_with_link,
    STARTING_PRICE,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_contract,
)
from scripts.deploy import deploy_lottery
from web3 import Web3
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Don't run this test on local blockchain")
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000})
    fund_with_link(lottery.address, account=account)
    lottery.endLottery({"from": account})
    time.sleep(120)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
