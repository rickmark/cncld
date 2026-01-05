pragma solidity ^0.8.33;

import {Test} from "forge-std/Test.sol";
import {CNCLCoin} from "../src/CNCLCoin.sol";
import {Upgrades} from "@openzeppelin/foundry-upgrades/Upgrades.sol";


contract CNCLCoinTest is Test {
    CNCLCoin coin;

    address constant DEPLOYER_ACCOUNT = 0xb4c79daB8f259C7Aee6E5b2Aa729821864227e84;
    address immutable PROXY_ADMIN = makeAddr("INITIAL_OWNER_ADDRESS_FOR_PROXY_ADMIN");
    address immutable ADMIN_ACCOUNT = makeAddr("ADMIN_ACCOUNT");
    address immutable MINTER_ACCOUNT = makeAddr("MINTER_ACCOUNT");

    address immutable NFT_OWNER = makeAddr("RICKMARK");

    function setUp() public {
        vm.deal(DEPLOYER_ACCOUNT, 100.0);
        vm.deal(MINTER_ACCOUNT, 100.0);

        address proxy = Upgrades.deployUUPSProxy(
            "CNCLCoin.sol",
            abi.encodeCall(CNCLCoin.initialize, (ADMIN_ACCOUNT, MINTER_ACCOUNT, PROXY_ADMIN))
        );
        coin = CNCLCoin(proxy);
    }

    function test_cancelTrump() public {
        vm.startPrank(MINTER_ACCOUNT);

        coin.cancel("Donald Trump", 4000, NFT_OWNER);

        vm.stopPrank();
    }

    function test_doubleCancel() public {
        vm.startPrank(MINTER_ACCOUNT);

        coin.cancel("Tucker Carlson", 2000, NFT_OWNER);
        coin.cancel("Tucker Carlson", 2000, NFT_OWNER);

        vm.stopPrank();
    }
}