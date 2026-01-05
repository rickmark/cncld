// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.10;

contract CNCLCoinDeploy {

    address constant ADMIN_ADDRESS = 0xd54651A671B7259eFf157a5e4F2EE11B87A31563;
    address constant MINT_ADDRESS = 0x3b0e917e46429046Ac0767d47B6C971140BA718A;

    function run() {
        address proxy = Upgrades.deployUUPSProxy(
            "CNCLCoin.sol",
            abi.encodeCall(MyContract.initialize, (ADMIN_ADDRESS, MINT_ADDRESS, ADMIN_ADDRESS));
        );
    }
}
