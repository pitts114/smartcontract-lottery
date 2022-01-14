from brownie import Lottery, MockV3Aggregator, accounts, config, network
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)


def deploy_lottery():
    account = get_account(id="freecodecamp-account")
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


def main():
    """Deploys the Lottery contract."""
    lottery = deploy_lottery()
