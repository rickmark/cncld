import os
import sys
from pathlib import Path

# Add the api directory to path so we can import blockchain
sys.path.append(str(Path(__file__).parent.parent / "api"))

from blockchain import BlockchainManager

# Configuration (Use environment variables for secrets)
RPC_URL = os.environ.get("RPC_URL", "http://localhost:8545")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
ABI_PATH = "../coin/out/CancelCoin.abi.json"

def main():
    if not os.path.exists(ABI_PATH):
        print(f"Error: ABI file not found at {ABI_PATH}")
        return

    # Initialize manager
    manager = BlockchainManager(RPC_URL, CONTRACT_ADDRESS, ABI_PATH, PRIVATE_KEY)
    
    # Example recipient
    recipient = "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"
    
    print(f"Interacting with contract at: {CONTRACT_ADDRESS}")
    print(f"Using account: {manager.account.address}")

    # 1. Minting
    token_id = 1
    amount = 100
    print(f"\nMinting {amount} of token {token_id} to {recipient}...")
    try:
        receipt = manager.mint(recipient, token_id, amount)
        print(f"Mint successful! TX Hash: {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"Mint failed: {e}")

    # 2. Check Balance
    balance = manager.get_balance(recipient, token_id)
    print(f"New balance of {recipient}: {balance}")

    # 3. Cancel (Custom minting logic)
    subject = "Example Subject"
    cancel_factor = 1
    print(f"\nCanceling subject '{subject}' for {recipient}...")
    try:
        receipt = manager.cancel(recipient, subject, cancel_factor)
        print(f"Cancel successful! TX Hash: {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"Cancel failed: {e}")

    # 4. Burning
    burn_amount = 50
    print(f"\nBurning {burn_amount} of token {token_id} from {recipient}...")
    # Note: Burning usually requires the burner to have the tokens or be approved.
    # If the manager account has MINTER_ROLE but not tokens, it can't burn from others 
    # unless it has approval or the contract allows it.
    try:
        receipt = manager.burn(recipient, token_id, burn_amount)
        print(f"Burn successful! TX Hash: {receipt.transactionHash.hex()}")
    except Exception as e:
        print(f"Burn failed: {e}")

    # 5. Final Balance
    balance = manager.get_balance(recipient, token_id)
    print(f"Final balance of {recipient}: {balance}")

if __name__ == "__main__":
    main()
