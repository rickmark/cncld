// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test} from "forge-std/Test.sol";
import {CancelCoin, CancelCoinSigner} from "../src/CancelCoin.sol";
import {Upgrades} from "openzeppelin-foundry-upgrades/Upgrades.sol";


contract CounterTest is Test {
    address alice = makeAddr("alice");
    address bob = makeAddr("bob");
    address carl = makeAddr("carl");
    address dave = makeAddr("dave");

    address zach = makeAddr("zach");

    address minter = makeAddr("minter");

    uint256 constant DONALD_TRUMP = 0xD963E39259969293F1733433F1C59DAA4551D62A74FB478F882203154A877A74;


    CancelCoinSigner public uriSetterSigner;
    CancelCoinSigner public pauserSigner;
    CancelCoinSigner public adminSigner;
    CancelCoinSigner public upgradeSigner;


    CancelCoin public coin;

    function setUp() public {
        bytes[] memory participants = new bytes[](4);
        participants[0] = abi.encodePacked(alice);
        participants[1] =   abi.encodePacked(bob);
        participants[2] =   abi.encodePacked(carl);
        participants[3] =   abi.encodePacked(dave);

        uriSetterSigner = new CancelCoinSigner(participants, 2);
        pauserSigner = new CancelCoinSigner(participants, 1);
        adminSigner = new CancelCoinSigner(participants, 3);
        upgradeSigner = new CancelCoinSigner(participants, 4);

        address implementation = address(new CancelCoin());

        address proxy = Upgrades.deployUUPSProxy(
            "CancelCoin.sol:CancelCoin",
            abi.encodeCall(CancelCoin.initialize, (address(adminSigner), address(pauserSigner), minter, address(upgradeSigner)))
        );

        coin = CancelCoin(proxy);
    }

    function test_Cancel() public {
        vm.prank(minter);
        coin.cancel(zach, "Donald Trump", 5000);
        assert(coin.balanceOf(zach, DONALD_TRUMP) == 5000);
    }

    function test_DoubleMintCancel() public {
        vm.prank(minter);
        coin.cancel(zach, "Donald Trump", 5000);
        vm.expectRevert(abi.encodeWithSelector(CancelCoin.AlreadyCanceledError.selector, DONALD_TRUMP, "Donald Trump", 5000));
        vm.prank(minter);
        coin.cancel(alice, "Donald Trump", 5000);
    }
}
