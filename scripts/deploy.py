from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3
import yaml
import json
import os
import shutil

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp_token(update_front_end=False):
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    tokenFarm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    # Sending almost all the dappToken supply to the tokenFarm contract
    tx = dapp_token.transfer(
        tokenFarm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    # dapp_token, wethToken, fauToken/dai
    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),
        fau_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
    }
    add_allowed_tokens(tokenFarm, dict_of_allowed_tokens, account)
    if update_front_end:
        update_front_end_func()
    return tokenFarm, dapp_token


def add_allowed_tokens(tokenFarm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        tx = tokenFarm.addAllowedTokens(token.address, {"from": account})
        tx.wait(1)
        tx2 = tokenFarm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        tx2.wait(1)
    return tokenFarm


def update_front_end_func():
    # Send the build folder
    copy_folders_to_front_end("./build", "./front_end/src/chain-info")

    # Send the front end our config in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_dapp_token(update_front_end=True)
