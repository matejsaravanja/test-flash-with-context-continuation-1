# nft-purchase-app/backend/app.py
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import SystemProgram
from solana.publickey import PublicKey
from dotenv import load_dotenv
from datetime import datetime  # Import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import dbapi2 as sqlite

# Import utility functions (NFT generation, email, etc.)
from .utils import generate_nft, send_email

load_dotenv()

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", 'sqlite:///:memory:')  # Replace with your DB URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if "sqlite" in app.config['SQLALCHEMY_DATABASE_URI']:
    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

db = SQLAlchemy(app)

# Solana Configuration
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")  # Default to devnet
CRAFT_TOKEN_MINT_ADDRESS = os.getenv("CRAFT_TOKEN_MINT_ADDRESS")
ADMIN_WALLET_PRIVATE_KEY = os.getenv("ADMIN_WALLET_PRIVATE_KEY")  # Securely manage this!
ADMIN_WLLET_PUBLIC_KEY = os.getenv("ADMIN_WALLET_PUBLIC_KEY")

solana_client = Client(SOLANA_RPC_URL)


# Ensure  ADMIN_WLLET_PRIVATE_KEY is not None before attempting to use it.
if ADMIN_WLLET_PRIVATE_KEY:
    try:
        admin_keypair = Keypair.from_secret_key(bytes(eval(ADMIN_WLLET_PRIVATE_KEY)))  # Careful with this
    except Exception as e:
        print(f"Error loading admin keypair: {e}")
        admin_keypair = None # Set to None to prevent further errors

else:
    admin_keypair = None
    print("ADMIN_WLLET_PRIVATE_KEY not set.  Application will not be" 
          "able to perform admin functions.")

# Database Models
class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(255), nullable=False, unique=True)
    user_public_key = db.Column(db.String(255), nullable=False)
    nft_id = db.Column(db.String(255), db.ForeignKey('nft.nft_id'), nullable=False)  # Foreign key to NFT
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.transaction_id}>"


class NFT(db.Model):
    nft_id = db.Column(db.String(255), primary_key=True)  # Use String for NFT IDs
    metadata_url = db.Column(db.String(255))  # IPFS URL for the metadata
    owner_public_key = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<NFT {self.nft_id}>"


with app.app_context():
    db.create_all()  # Create tables


# Improved Transaction Verification Function
def verify_transaction(transaction_signature, user_public_key, amount, craft_token_mint_address, admin_wallet_public_key):  # Include token address

    try:
        transaction_data = solana_client.get_transaction(transaction_signature)
        if not transaction_data or transaction_data["result"]["meta"]["err"] is not None:
            return False, "Transaction failed or not found on Solana"

        transaction = transaction_data["result"]["transaction"]
        message = transaction["message"]
        instructions = message["instructions"]

        # Check if the transaction involves a transfer FROM the user TO the admin (or designated recipient)
        transfer_instruction_found = False
        for instruction in instructions:
            accounts = instruction.get("accounts", [])
            data = instruction.get("data", "") #Added Safety check for 'data'

            # Decode instruction data (Spl Token Program)
            if instruction.get("programIdIndex") == 2 and len(accounts) >= 3: #SPL Token transfer has at least 3 accounts
                 source_account = message["accountKeys"][accounts[0]]
                 dest_account   = message["accountKeys"][accounts[1]]
                 token_mint     = message["accountKeys"][accounts[2]]

                 #Ver