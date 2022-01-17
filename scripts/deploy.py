from brownie import Lottery, MockV3Aggregator, accounts, config, network
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    deploy_mocks,
    fund_with_link,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
import time


def deploy_lottery():
    account = get_account()
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address
    else:
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]

    # lottery = Lottery.deploy(
    #     price_feed_address,
    #     {"from": account},
    #     publish_source=config["networks"][network.show_active()].get("verify"),
    # )
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print(f"Lottery contract address: {lottery.address}")
    return lottery


def start_lottery():
    """Starts the lottery contract."""
    account = get_account()
    lottery = Lottery[-1]
    starting_txn = lottery.startLottery({"from": account})
    starting_txn.wait(1)
    print("Lottery started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 1000000000
    txn = lottery.enter({"from": account, "value": value})
    txn.wait(1)
    print("Entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    fund_with_link(lottery.address)
    txn = lottery.endLottery({"from": account})
    txn.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    """Deploys the Lottery contract."""
    lottery = deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
