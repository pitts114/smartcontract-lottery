from brownie import Lottery, accounts, network
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    STARTING_PRICE,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from scripts.deploy import deploy_lottery
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only run this test on local blockchain")

    entranceFeeInGwei = 50 * 10 ** 18 / (STARTING_PRICE * 10)
    account = get_account()
    lottery = deploy_lottery()

    assert lottery.getEntranceFee() == Web3.toWei(entranceFeeInGwei, "Gwei")
