// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script} from "forge-std/Script.sol";
import {CancelCoin, CancelCoinSigner} from "../src/CancelCoin.sol";
import {Create2} from "@openzeppelin/contracts/utils/Create2.sol";
import {UUPSUpgradeable} from "@openzeppelin/contracts/proxy/upgradeable/UUPSUpgradeable.sol";

contract CancelCoinScript is Script {
    CancelCoinSigner public uriSetterSigner;
    CancelCoinSigner public pauserSigner;
    CancelCoinSigner public adminSigner;
    CancelCoinSigner public upgradeSigner;

    bytes32 constant SALT = 0x4c920832741bbbcdf87432e06ab48dde46469ce3049849a410afb98b322918f6;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        bytes memory implCreationCode = CancelCoin.creationCode;

        address implAddress = Create2.computeAddress(SALT, keccak256(implCreationCode));
        Create2.deploy(0, SALT, implCreationCode);

        bytes memory proxyCreationCode = type(UUPSUpgradeable).creationCode;
        address proxyAddress = Create2.computeAddress(SALT, keccak256(proxyCreationCode));

        Create2.deploy(0, SALT, proxyCreationCode);

        emit Deployed(proxyAddress, implAddress);

        vm.stopBroadcast();
    }
}
