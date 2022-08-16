from brownie import network, accounts, config, MockV3Aggregator, Contract, VRFCoordinatorMock, LinkToken

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local", "ganache-local1"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]

contract_to_mock = {"eth_usd_price_feed": MockV3Aggregator, 'vrf_cordinator': VRFCoordinatorMock, 'link_token': LinkToken}


# accounts[0]
# accounts.add('env')
# accounts.load('id')
def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config['wallets'][0]['from_key'])


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract


def fund_with_link(contract_address, account=None, amount=100000000000000000, link_token=None):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract('link_token')
    tx = link_token.transfer(contract_address, amount, {'from': account})
    tx.wait(1)
    print(f'Link token funded to contract address {contract_address}')
    return tx

DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, INITIAL_VALUE, {"from": account})
    link_token = LinkToken.deploy({'from': account})
    VRFCoordinatorMock.deploy(link_token.address, {'from': account})
