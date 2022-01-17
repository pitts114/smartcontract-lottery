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


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only run this test on local blockchain")

    # entranceFeeInGwei = 50 * 10 ** 18 / (STARTING_PRICE * 10)
    entranceFeeInWei = Web3.toWei(50 / 4000.0, "ether")
    account = get_account()
    lottery = deploy_lottery()

    # assert lottery.getEntranceFee() == Web3.toWei(entranceFeeInGwei, "Gwei")
    assert lottery.getEntranceFee() == entranceFeeInWei


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only run this test on local blockchain")

    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError) as excinfo:
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})

    assert "The lottery is not open!" in str(excinfo.value)


def test_can_enter_after_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only run this test on local blockchain")

    lottery = deploy_lottery()
    account = get_account()

    assert lottery.lottery_state() == 1
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account
    assert lottery.lottery_state() == 0


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only run this test on local blockchain")

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    assert lottery.lottery_state() == 0
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery.address, account=account)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only run this test on local blockchain")

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    fund_with_link(lottery.address, account=account)

    account_starting_balance = account.balance()
    lottery_balance = lottery.balance()

    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    STATIC_RND = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RND, lottery.address, {"from": account}
    )

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == account_starting_balance + lottery_balance
