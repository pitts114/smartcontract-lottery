from brownie import (
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    accounts,
    config,
    network,
    Contract,
    interface,
)
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

DECIMALS = 8
STARTING_PRICE = 400000000000  # 4000.00000000


def get_account(index=None, id=None):
    if index is not None:
        return accounts[index]
    if id is not None:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.load("developer-exposed")


def deploy_mocks(decimals=DECIMALS, starting_price=STARTING_PRICE):
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()
    MockV3Aggregator.deploy(decimals, starting_price, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    print("Mocks deployed!")


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "link_token": LinkToken,
    "vrf_coordinator": VRFCoordinatorMock,
}


def get_contract(contract_name):
    """ "This function will grab the contract addressess from the brownie
    config if defined, otherwise it will deploy a mock version of that contract,
    and return that mock contract.

        Args:
            contract_name (string)

        Returns:
            brownie.network.contract.ProjectContract: The most
            recently deployed version of this contract.
            MockV3Aggregator[-1]
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    txn = interface.LinkTokenInterface(link_token.address).transfer(
        contract_address, amount, {"from": account}
    )
    txn.wait(1)
    print("Find contract!")
    return txn
