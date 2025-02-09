# nft-purchase-app/backend/app.py
import os
import json  # Import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import SystemProgram
from solana.publickey import PublicKey
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import dbapi2 as sqlite

# Import utility functions
from .utils import generate_nft, send_email

load_dotenv()

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", 'sqlite:///:memory:')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLite foreign key enforcement (for SQLite DBs)
if "sqlite" in app.config['SQLALCHEMY_DATABASE_URI']:
    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        if isinstance(dbapi_connection, sqlite.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGma foreign_keys=ON;")
            cursor.close()

db = SQLAlchemy(app)

# Solana Configuration
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
CRAFT_TOKEN_MINT_ADDRESS = os.getenv("CRAFT_TOKEN_MINT_ADDRESS")
ADMIN_WALLET_PRIVATE_KEY = os.getenv("ADMIN_WALLET_PRIVATE_KEY")
ADMIN_WALLET_PUBLIC_KEY = os.getenv("ADMIN_WALLET_PUBLIC_KEY")

solana_client = Client(SOLANA_RPC_URL)

# Load Admin Keypair - Securely (using json.loads instead of eval)
admin_keypair = None  # Initialize to None
if ADMIN_WALLET_PRIVATE_KEY:
    try:
        admin_keypair = Keypair.from_secret_key(bytes(json.loads(ADMIN_WALLET_PRIVATE_KEY)))
    except json.JSONDecodeError as e:
        print(f" Error decoding ADMIN_WALLET_PRIVATE_KEY: {e}.  Make sure it's a valid JSON list.")
    except Exception as e:
        print(f" Error loading admin keypair: {e}")

    # Validation check.  If admin_keypair did not load from the environment variable, set to None
    if not admin_keypair:
        print("Admin Keypair could not be loaded.  Admin priviledges unavailable")

else:
    print("ADMIN_WALLET_PRIVATE_KEY not set. Admin functions will be disabled.")

# Database Models
class TransactionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(255), nullable=False, unique=True)
    user_public_key = db.Column(db.String(255), nullable=False)
    nft_id = db.Column(db.String(255), db.ForeignKey('nft.nft_id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'


class NFT(db.Model):
    nft_id = db.Column(db.String(255), primary_key=True)
    metadata_url = db.Column(db.String(255))
    owner_public_key = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<NFT {self.nft_id}>'


with app.app_context():
    db.create_all()


# Transaction Verification Function
def verify_transaction(transaction_signature, user_public_key, amount, craft_token_mint_address, admin_wallen_puglic_key):  # Include token address

    try:
        transaction_data = solana_client.get_transaction(transaction_signature)

        # Robust Error Checking
        if not transaction_data or transaction_data.get("result") is None or transaction_data["result"].get("meta") is None or transaction_data["result"]["meta"].get("err") is not None:
            return False, "Transaction failed or not found on Solana"

        transaction = transaction_data["result"].get("transaction")  # Use .get() for safety
        if not transaction:
            return False, "Transaction data missing"

        message = transaction.get("message")  # Use .get() for safety
        if not message:
            return False, "Transaction message missing"

        instructions = message.get("instructions")  # Use .get() for safety
        if not instructions:
            return False, "Transaction instructions missing"

        transfer_instruction_found = False
        for instruction in instructions:
            if not isinstance(instruction, dict):
                continue  # Skip if instruction is not a dictionary

            accounts = instruction.get("accounts", [])  # Safely get accounts
            data = instruction.get("data", "")  # Safely get data

            program_id_index = instruction.get("programIdIndex")
            if program_id_index == 2 and len(accounts) >= 3:
                try:
                    source_account = message["accountKeys"][accounts[0]]
                    dest_account = message["accountKeys"][accounts[1]]
                    token_mint = message["accountKeys"][accounts[2]]

                    if str(token_mint) == craft_token_mint_address and str(source_account) == user_public_key and str(dest_account) == ADMIN_WALLET_PUBLIC_KEY:
                        transfer_instruction_found = True
                        break
                except (KeyError, IndexError) as e:
                    print(f" Error accessing account keys: {e}")  # Log the specific error with details
                    return False, f" Error accessing account keys: {e}"

        if not transfer_instruction_found:
            return False, "Invalid transaction: No transfer to the recipient found."

        return True, None

    except Exception as e:
        print(f" Error verifying transaction: {e}")
        return False, f" Error during verification: {str(e)}"


# API Endpoint for Payment Verification
@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    transaction_signature = data.get('transactionSignature')
    user_public_key = data.get('userPublicKey')
    amount = data.get('amount')  # Amount should be passed as a number in json
    craft_token_mint_address = data.get('craftTokenMintAddress')

    if not all([transaction_signature, user_public_key, amount, craft_token_mint_address]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        amount = float(amount)  # Try to convert to float (Defensive programming)
    except ValueError:
        return jsonify({'error': 'Invalid amount format'}), 400

    if not admin_keypair:
        return jsonify({'success': False, 'error': 'Admin wallet not properly configured'}), 500

    is_valid, error_message = verify_transaction(transaction_signature, user_public_key, amount, craft_token_mint_address, ADMIN_WALLET_PUBLIC_KEY)

    if is_valid:
        nft_data = generate_nft(user_public_key)
        if not nft_data:
            return jsonify({'success': False, 'error': 'NFT generation failed'}), 500

        nft = NFT(nft_id=nft_data['nft_id'], metadata_url=nft_data.get('metadata_url', ''), owner_public_key=user_public_key)
        new_transaction = TransactionHistory(transaction_id=transaction_signature, user_public_key=user_public_key, nft_id=nft.nft_id)

        try:
            db.session.add(nft)
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500

        eMaltMail_html = f"""
            <html>
            <body>
                <p>Congratulations! You've purchased an NFT!</p>
                <img src="{nft_data['image']}" alt="Your NFT">
                <p>Download your NFT: <a href="{nft_data['image']}">Download SVG</a></p>
            </body>
            </html>
        """
        send_email(user_public_key, "Your New NFT!", "See the attached NFT!", html=email_html)

        return jsonify({'success': True, 'message': 'Payment verified, NFT generated and email sent!', 'nft_data': nft_data})
    else:
        return jsonify({'success': False, 'error': error_message}), 400


# API Endpoint to Retrieve NFTs for a User
@app.route('/get_nfts/<user_public_key>', methods=['GET'])
def get_nfts(user_public_key):
    """ Retrieves all NFTs associated with a user's public key."""
    nfts = NFT.query.filter_by(owner_public_key=user_public_key).all()
    nft_data = []
    for nft in nfts:
        nft_data.append({
            'nft_id': nft.nft_id,
            'metadata_url': nft.metadata_url,
        })
    return jsonify(nft_data)


if __name__ == '__main__':
    app.run(debug=True)