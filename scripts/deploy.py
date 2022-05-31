from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp_token():
    account = get_account()
    dappToken = DappToken.deploy({"from": account})
    tokenFarm = TokenFarm.deploy(
        dappToken.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # Sending almost all the dappToken supply to the tokenFarm contract
    tx = dappToken.transfer(
        tokenFarm.address, dappToken.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    # dappToken, wethToken, fauToken/dai
    add_allowed_tokens()

def add_allowed_tokens(tokenFarm, dict_of_allowed_tokens, account):



def main():
    deploy_token_farm_and_dapp_token()
