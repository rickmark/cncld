import os
import json
from web3 import Web3
from eth_account import Account
from ens import ENS

class BlockchainManager:
    def __init__(self, rpc_url: str, contract_address: str, abi_path: str, private_key: str):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        
        with open(abi_path, 'r') as f:
            self.abi = json.load(f)
            
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=self.abi)

    def _send_transaction(self, func_call):
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        
        # Build transaction
        tx = func_call.build_transaction({
            'from': self.account.address,
            'nonce': nonce,
            'gasPrice': self.w3.eth.gas_price,
        })
        
        # Estimate gas
        tx['gas'] = self.w3.eth.estimate_gas(tx)
        
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)

    def cancel(self, recipient: str, subject: str, cancel_factor: int):
        """
        Calls the custom 'cancel' function which mints tokens based on a subject string hash.
        """
        recipient = Web3.to_checksum_address(recipient)
        func = self.contract.functions.cancel(recipient, subject, cancel_factor)
        return self._send_transaction(func)

    def get_balance(self, address: str, token_id: int) -> int:
        """
        Returns the token balance of an address for a specific token ID.
        """
        address = Web3.to_checksum_address(address)
        return self.contract.functions.balanceOf(address, token_id).call()

    def get_total_supply(self, token_id: int) -> int:
        """
        Returns the total supply of a specific token ID.
        """
        return self.contract.functions.totalSupply(token_id).call()
