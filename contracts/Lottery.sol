// SPDX-License-Identifier: MIT
pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase {
    uint256 public usdEntryFee;
    address payable[] public players;
    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lotteryState;

    uint256 public randomnessFee;
    bytes32 public keyHash;
    address payable public recentWinner;
    uint256 randomness;
    event RequestedRandomness(bytes32 requestId);

    constructor(address _priceFeedAddress, address _vrfCordinator, address _link, uint256 _randomnessFee, bytes32 _keyHash) public VRFConsumerBase(_vrfCordinator, _link) {
        usdEntryFee = 50 * 10**18;
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED;
        randomnessFee = _randomnessFee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(lotteryState == LOTTERY_STATE.OPEN);
        require(msg.value >= getEntranceFee(), '50 USD or more worth of ETH required!');
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        // $50, $2000 /eth
        // costToEnter = 50/2000 in eth
        // costToEnter = 50 * 10**18 /2000 in wei
         (
            /*uint80 roundID*/,
            int price,
            /*uint startedAt*/,
            /*uint timeStamp*/,
            /*uint80 answeredInRound*/
        ) = ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10; // 8 from feed + 10 to get 18 dec 
        uint256 costToEnter = uint256 ( usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter; // in wei
    }

    function start() public onlyOwner {
        require(lotteryState == LOTTERY_STATE.CLOSED, 'A lottery is already running!');
        lotteryState = LOTTERY_STATE.OPEN;
    }

    function end() public onlyOwner {
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32  requestId = requestRandomness(keyHash, randomnessFee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        require(lotteryState == LOTTERY_STATE.CALCULATING_WINNER, "You are not there yet!");
        require(_randomness > 0, 'random-not-found!');
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        // reset
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }
}