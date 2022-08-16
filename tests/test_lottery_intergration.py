from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, fund_with_link, get_account
from brownie import network, config
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    lottery.start({'from': account})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    lottery.enter({'from': account, 'value': lottery.getEntranceFee()})
    fund_with_link(lottery.address)
    # Act
    tx = lottery.end({'from': account})
    time.sleep(60)
    # Assert
    assert lottery.balance() == 0
    assert account == lottery.recentWinner()
