from operator import index
from brownie import Lottery, accounts, network, config, exceptions
from web3 import Web3
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link, get_contract, get_account
from scripts.deploy_lottery import deploy_lottery
import pytest

def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip('Not in local environments!')
    # Arrange
    lottery = deploy_lottery()
    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(0.025, 'ether')
    assert expected_entrance_fee == entrance_fee

def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip('Not in local environments!')
    account = get_account()
    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({'from': account, 'value': lottery.getEntranceFee()})

def test_can_start_and_enter():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip('Not in local environments!')
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    lottery.start({'from': account})
    # Act
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    # Assert
    lottery.players(0) == account

def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip('Not in local environments!')
    # Arrange
    account = get_account()
    lottery  = deploy_lottery()
    lottery.start({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    # Act
    fund_with_link(lottery.address)
    lottery.end({'from': account})
    # Assert
    assert lottery.lotteryState() == 2

def test_can_choose_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip('Not in local environments!')
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    lottery.start({'from': account})
    lottery.enter({'from': get_account(index=1), 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(index=2), 'value': lottery.getEntranceFee()})
    lottery.enter({'from': get_account(index=3), 'value': lottery.getEntranceFee()})
    winner_starting_balance = get_account(index=1).balance()
    winner_expected_total_balance = winner_starting_balance + lottery.balance()
    MOCK_RANDOM_NUMBER = 777
    # Act 
    fund_with_link(lottery.address)
    tx = lottery.end({'from': account})
    request_id = tx.events['RequestedRandomness']['requestId']
    get_contract('vrf_cordinator').callBackWithRandomness(request_id, MOCK_RANDOM_NUMBER, lottery)
    # Assert
    assert lottery.recentWinner() == get_account(index=1)
    assert lottery.balance() == 0
    assert winner_expected_total_balance == get_account(index=1).balance()


