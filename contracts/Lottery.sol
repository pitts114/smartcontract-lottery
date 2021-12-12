// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable {
    using SafeMathChainlink for uint256;

    address payable[] public players;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state = LOTTERY_STATE.CLOSED;
    // mapping(address => uint256) public addressToAmountFunded;
    uint256 public usdEntryFee = 50 * 10**18;
    AggregatorV3Interface internal ethUsdPriceFeed;

    constructor(address _priceFeed) public {
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeed);
    }

    function enter() public payable {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "The lottery is not open!"
        );
        require(msg.value >= getEntranceFee(), "You need to spend more ETH!");
        // addressToAmountFunded[msg.sender] += msg.value;
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        uint256 minimumUSD = 50 * 10**18;
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        return (minimumUSD * precision) / price;
    }

    function getPrice() public view returns (uint256) {
        (, int256 answer, , , ) = ethUsdPriceFeed.latestRoundData();
        return uint256(answer * 10000000000);
    }

    function getConversionRate(uint256 ethAmount)
        public
        view
        returns (uint256)
    {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1000000000000000000;
        return ethAmountInUsd;
    }

    function startLottery() public {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "The lottery is already open!"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "The lottery is not open!"
        );
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
    }
}
