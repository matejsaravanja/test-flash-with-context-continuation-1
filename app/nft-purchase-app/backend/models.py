# backend/models.py
from app import db #Import db from app.py
from datetime import datetime

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