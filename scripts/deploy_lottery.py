from multiprocessing.sharedctypes import Value
from scripts.helpful_scripts import fund_with_link, get_account, get_contract
from brownie import Lottery, network, config
import time

# config for gar prices
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
# from brownie.network.gas.strategies import GasNowStrategy
# gas_strategy = GasNowStrategy("fast")

def set_default_gas():
    gas_strategy = LinearScalingStrategy("10 gwei", "50 gwei", 1.1)
    gas_price(gas_strategy)

def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract('eth_usd_price_feed').address,
        get_contract('vrf_cordinator').address,
        get_contract('link_token').address,
        config['networks'][network.show_active()]['fee'],
        config['networks'][network.show_active()]['keyhash'],
        {'from': account},
        publish_source=config['networks'][network.show_active()].get('verify', False)
    )
    return lottery

def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    start_trx = lottery.start({'from': account})
    start_trx.wait(1)
    print('Lottery is started!')

def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 10000
    trx = lottery.enter({'from': account, 'value': value})
    trx.wait(1)
    print('You have entered the lottery!')

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    fund_tx = fund_with_link(lottery.address)
    fund_tx.wait(1)
    end_tx = lottery.end({'from': account});
    time.sleep(60)
    print(f'{lottery.recentWinner()} is the new winner!')



def main():
    set_default_gas()
    deploy_lottery();
    start_lottery()
    enter_lottery()
    end_lottery()