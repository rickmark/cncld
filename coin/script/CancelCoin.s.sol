// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script} from "forge-std/Script.sol";
import {CancelCoin, CancelCoinSigner} from "../src/CancelCoin.sol";

contract CancelCoinScript is Script {
    CancelCoinSigner public uriSetterSigner;
    CancelCoinSigner public pauserSigner;
    CancelCoinSigner public adminSigner;
    CancelCoinSigner public upgradeSigner;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();


        vm.stopBroadcast();
    }
}
