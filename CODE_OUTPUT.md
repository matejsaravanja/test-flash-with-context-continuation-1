**This file consists of the entire unaltered output for reference.**

Okay, based on your feedback, I've incorporated the suggested improvements and added detailed instructions to make the application effortlessly runnable. I will now provide the full code output, organized by file path, including necessary setup and configuration steps.

**Crucial Considerations Before Starting:**

1.  **Solana Tool Suite:** Verify that the Solana Tool Suite installed on your system and configured correctly. You can find instructions on the Solana website.
2.  **NodeJS and NPM/Yarn:**  Ensure that NodeJS and NPM (or Yarn) are installed on your system. These are used for the frontend (React) development.
3.  **Python:** Make sure that Python is installed on your system, as it's used for the backend.
4.  **IPFS Daemon:** You will most likely need a local IPFS daemon running if you want to test the functionality of minting NFTs. `ipfs daemon`

**Project directory structure:**

```
nft-purchase-app/  (Root directory)
├── backend/        (Python Backend)
│   ├── app.py       (Flask application)
│   ├── models.py    (Database models)
│   ├── utils.py     (Utility functions - SVG generation, token verification)
│   ├── .env         (Environment variables)
│   ├── requirements.txt
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_utils.py
│   └── Dockerfile    (Optional - for containerization)
├── frontend/       (React Frontend)
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   ├── WalletConnect.js
│   │   │   ├── NFTDisplay.js
│   │   │   ├── PurchaseButton.js
│   │   ├── utils/
│   │   │   ├── solana.js  (Solana interaction functions)
│   │   ├── App.css
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── README.md
├── .gitignore
└── README.md
```

**I. Project Setup & Infrastructure (Sprint 0):**

**1.  Environment Setup**

*   **Backend (Python)**

    1.  Create a folder named `backend`

    2.  Inside the `backend` folder, create a file named `requirements.txt` and paste the dependencies.

    ```txt
    # backend/requirements.txt
    Flask
    Flask-SQLAlchemy
    requests
    python-dotenv
    solana
    ipfshttpclient
    SQLAlchemy==1.4.41
    psycopg2-binary #Required for postgres
    ```

    3.  Create the `.env` file in same directory. Add all of these environment variables to the `.env` file. I will provide explanation after code.

    ```txt
    # backend/.env
    DATABASE_URL=postgresql://user:password@host:port/database_name # Replace this. Could also be a sqlite path
    SOLANA_RPC_URL=https://api.devnet.solana.com # Or your preferred RPC endpoint
    CRAFT_TOKEN_MINT_ADDRESS=YOUR_CRAFT_TOKEN_MINT_ADDRESS # Replace with the actual mint address
    ADMIN_WALLET_PRIVATE_KEY=[1,2,3, ... ,255] # replace this. Keep the list formatting.
    ADMIN_WALLET_PUBLIC_KEY=YOUR_ADMIN_WALLET_PUBLIC_KEY # Replace this
    IPFS_GATEWAY_URL=https://ipfs.io/ipfs # Or your preferred gateway
    EMAIL_ADDRESS=your_email@gmail.com # Replace
    EMAIL_PASSWORD=your_email_app_password # Replace (use an app password for Gmail)
    ```

    4.  Set up all of these environment variables properly. If you are using a `PostgreSQL` database, you must have it preconfigured.

    5.  The `ADMIN_WALLET_PRIVATE_KEY` must be in list format. For example `[124,32, ... ,83]`.

    6.  Create the `test` directory with `__init__.py` inside.

    7.  Install the dependencies. `pip install -r requirements.txt`

*   **Frontend (React)**

    1.  Create a folder named `frontend`

    2.  Open your terminal, navigate to the `frontend` directory.

    3.  Run `npx create-react-app .` This command initializes a new React project in the current directory.

    4.  Install the necessary dependencies:

    ```bash
    npm install @solana/web3.js @solana/wallet-adapter-base @solana/wallet-adapter-react @solana/wallet-adapter-wallets @solana/wallet-adapter-phantom @solana/wallet-adapter-solflare axios @solana/spl-token
    ```

**2.  Backend Code:**

*   **`backend/app.py`**

```python
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
ADMIN_WALLET_PUBLIC_KEY = os.getenv("ADMIN_WALLET_PUBLIC_KEY")

solana_client = Client(SOLANA_RPC_URL)


# Ensure  ADMIN_WALLET_PRIVATE_KEY is not None before attempting to use it.
if ADMIN_WALLET_PRIVATE_KEY:
    try:
        admin_keypair = Keypair.from_secret_key(bytes(eval(ADMIN_WALLET_PRIVATE_KEY)))  # Careful with this
    except Exception as e:
        print(f"Error loading admin keypair: {e}")
        admin_keypair = None # Set to None to prevent further errors

else:
    admin_keypair = None
    print("ADMIN_WALLET_PRIVATE_KEY not set.  Application will not be"
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

                 #Verify correct token mint address, source, and destination
                 if str(token_mint) == craft_token_mint_address and str(source_account) == user_public_key and str(dest_account) ==  admin_wallet_public_key:
                    transfer_instruction_found = True #Suitable transfer found
                    break #Exit loop

        if not transfer_instruction_found:
            return False, "Invalid transaction: No transfer to the recipient found."
        return True, None  # Transaction is valid

    except Exception as e:
        print(f"Error verifying transaction: {e}") # Good to keep for debugging
        return False, f"Error during verification: {str(e)}"


# API Endpoint for Payment Verification
@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    data = request.get_json()
    transaction_signature = data.get('transactionSignature')
    user_public_key = data.get('userPublicKey')
    amount = float(data.get('amount'))  # Amount of CRAFT tokens
    craft_token_mint_address = data.get('craftTokenMintAddress')

    if not all([transaction_signature, user_public_key, amount, craft_token_mint_address]):
        return jsonify({'error': 'Missing parameters'}), 400


    # Validate that the Admin keypair is properly loaded before transacting with it.
    if not admin_keypair:
        return jsonify({'success': False, 'error': 'Admin wallet not properly configured'}), 500

    is_valid, error_message = verify_transaction(transaction_signature, user_public_key, amount, craft_token_mint_address, ADMIN_WALLET_PUBLIC_KEY)

    if is_valid:
        # Generate NFT (call your function)
        nft_data = generate_nft(user_public_key)  # This should return the NFT metadata

        if not nft_data:
             return jsonify({'success': False, 'error': 'NFT generation failed'}), 500

        # Store NFT in database
        nft = NFT(nft_id=nft_data['nft_id'], metadata_url=nft_data.get('metadata_url', ''), owner_public_key=user_public_key)

        # Store transaction ONLY after NFT is successfully created/stored
        new_transaction = TransactionHistory(transaction_id=transaction_signature, user_public_key=user_public_key, nft_id=nft.nft_id)


        try:
            db.session.add(nft) #Add NFT First
            db.session.add(new_transaction)
            db.session.commit()
        except Exception as e:
            db.session.rollback() #Rollback upon error
            return jsonify({'success': False, 'error': f'Database error: {str(e)}'}), 500

        # Send email (call your email function)
        email_html = f"""
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
    """Retrieves all NFTs associated with a user's public key."""
    nfts = NFT.query.filter_by(owner_public_key=user_public_key).all() #Query based on owner

    nft_data = []
    for nft in nfts:
        nft_data.append({
            'nft_id': nft.nft_id,
            'metadata_url': nft.metadata_url, #Return Metadata URL
        })
    return jsonify(nft_data)


if __name__ == '__main__':
    app.run(debug=True)
```

*   **`backend/utils.py`**

```python
# nft-purchase-app/backend/utils.py
import os
import svgwrite
import json
import hashlib
import secrets
import time # Import time
from dotenv import load_dotenv
from ipfshttpclient import connect
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

load_dotenv()

IPFS_GATEWAY_URL = os.getenv("IPFS_GATEWAY_URL")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def generate_unique_id():
    """Generates a unique identifier using a combination of timestamp and random token."""
    timestamp = str(int(time.time()))  # Current timestamp as a string
    random_token = secrets.token_hex(16)  # 16 bytes of random data (32 hex characters)
    combined_string = timestamp + random_token
    unique_id = hashlib.sha256(combined_string.encode()).hexdigest()
    return unique_id

def generate_svg(unique_identifier):
    """Generates a simple SVG image based on a unique identifier."""
    dwg = svgwrite.Drawing('temp.svg', profile='tiny')
    # Use the hash to determine the circle's color and position.
    x = int(unique_identifier[:2], 16) * 5  # First two characters for X position
    y = int(unique_identifier[2:4], 16) * 5  # Next two for Y position
    radius = int(unique_identifier[4:6], 16) / 8  # Next two for radius
    color = f"#{unique_identifier[6:12]}"  # Next six for color

    dwg.add(dwg.circle((x, y), radius, fill=color))
    dwg.save()
    return 'temp.svg'

def upload_to_ipfs(file_path):
    """Uploads a file to IPFS and returns the CID."""
    try:
        client = connect() #Connects to local
        with open(file_path, 'rb') as f:
            response = client.add(f)
            return response['Hash']
    except Exception as e:
        print(f"Error uploading to IPFS: {e}")
        return None

def generate_nft(user_public_key):
    """Generates a unique NFT, uploads it to IPFS, and returns the metadata."""
    unique_id = generate_unique_id()
    svg_file = generate_svg(unique_id)

    #Upload to IPFS
    image_cid = upload_to_ipfs(svg_file)
    if image_cid is None:
        return None

    #Construct metadata
    metadata = {
        "name": f"My Cool NFT - {unique_id[:8]}",  #Shortened ID
        "description": "A Unique NFT Generated for User",
        "image": f"{IPFS_GATEWAY_URL}/{image_cid}",  #IPFS Gateway
        "attributes": [
            {"trait_type": "Generated For", "value": user_public_key},
            {"trait_type": "Unique ID", "value": unique_id}
        ],
        "nft_id": unique_id #Good to store unique IDs for retrieval later in the database
    }

    #Optionally Upload Metadata to IPFS - Recommended
    metadata_json = json.dumps(metadata, indent=4).encode('utf-8') #Properly format JSON

    metadata_cid = upload_to_ipfs(metadata_json) #UTF-8 Encoding!
    if metadata_cid:
       metadata["metadata_url"] = f"{IPFS_GATEWAY_URL}/{metadata_cid}" #Store this in database
    else:
        print("Warning: Could not upload metadata to IPFS")


    #Clean up temporary SVG file
    os.remove(svg_file)

    return metadata

def send_email(recipient, subject, body, html=None, image_path=None):
    """Sends an email using SMTP."""

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not set.  Cannot send email.")
        return False #Indicate failure

    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if html:
        # If an image path is provided, embed the image in the HTML
        if image_path:
            try:
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    html = html.replace('cid:image1', f'data:image/svg+xml;base64,{img_base64}') #Reference Image
            except Exception as e:
                print(f"Error embedding image: {e}")

        msg.attach(MIMEText(html, 'html'))


    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: #Adjust for your provider
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        print("Email sent successfully!")
        return True  #Indicate Success

    except Exception as e:
        print(f"Email sending failed: {e}")
        return False  #Indicate Failure
```

*   **`backend/models.py`**

```python
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
```

*   **`backend/tests/__init__.py`**

```python
# backend/tests/__init__.py
#Empty file.  Makes the directory a package.
```

*   **`backend/tests/test_utils.py`**

```python
# backend/tests/test_utils.py
import pytest
from backend.utils import generate_svg, upload_to_ipfs, send_email
import os

def test_generate_svg():
    svg_file = generate_svg("test_hash")
    assert os.path.exists(svg_file)
    os.remove(svg_file) #Clean up

#Mocking IPFS for testing
from unittest.mock import patch
@patch('backend.utils.connect')
def test_upload_to_ipfs(mock_connect):
    mock_instance = mock_connect.return_value
    mock_instance.add.return_value = {'Hash': 'test_cid'}
    cid = upload_to_ipfs("dummy_file.txt")
    assert cid == "test_cid"

#Test Email Sending
def test_send_email():
    #This test will only verify that the function runs without errors,
    #not that the email is actually sent (due to credentials).
    #You can extend it to check the return value based on successful/failed login

    result = send_email("test@example.com", "Test Subject", "Test Body")
    assert result is False #Because email is not configured properly

```

**3.  Frontend Code:**

*   **`frontend/src/App.js`**

```javascript
// frontend/src/App.js
import React from 'react';
import WalletConnect from './components/WalletConnect';
import NFTDisplay from './components/NFTDisplay';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>NFT Purchase App</h1>
        <WalletConnect />
        <NFTDisplay />
      </header>
    </div>
  );
}

export default App;
```

*   **`frontend/src/components/WalletConnect.js`**

```javascript
// frontend/src/components/WalletConnect.js
import React, { useCallback, useMemo } from 'react';
import {
    ConnectionProvider,
    WalletProvider,
} from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import {
    PhantomWalletAdapter,
    SolflareWalletAdapter
} from '@solana/wallet-adapter-wallets';
import {
    WalletModalProvider,
    WalletDisconnectButton,
    WalletMultiButton
} from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';

// Default styles that can be overridden by your app
require('@solana/wallet-adapter-react-ui/styles.css');

const WalletConnect = () => {
    // The network can be set to 'devnet', 'testnet', or 'mainnet-beta'.
    const network = WalletAdapterNetwork.Devnet;

    // You can also provide a custom RPC endpoint.
    const endpoint = useMemo(() => clusterApiUrl(network), [network]);

    // Wallets
    const wallets = useMemo(() => [
        new PhantomWalletAdapter(),
        new SolflareWalletAdapter({ network }),
    ], [network]);

    return (
        <ConnectionProvider endpoint={endpoint}>
            <WalletProvider wallets={wallets} autoConnect>
                <WalletModalProvider>
                    <WalletMultiButton />
                    <WalletDisconnectButton />
                </WalletModalProvider>
            </WalletProvider>
        </ConnectionProvider>
    );
};

export default WalletConnect;
```

*   **`frontend/src/components/NFTDisplay.js`**

```javascript
// frontend/src/components/NFTDisplay.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useWallet } from '@solana/wallet-adapter-react';

const NFTDisplay = () => {
    const { publicKey } = useWallet();
    const [nfts, setNfts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null); // Add error state


    useEffect(() => {
        const fetchNFTs = async () => {
            if (publicKey) {
                try {
                    const response = await axios.get(`/get_nfts/${publicKey.toString()}`); //Adjust URL - Change this to your backend url
                    setNfts(response.data);
                    setError(null); // Clear any previous errors
                } catch (err) {
                    console.error("Error fetching NFTs:", err);
                    setError(err.message || "Failed to fetch NFTs"); // Set error message
                    setNfts([]); // Ensure NFTs are cleared on error
                } finally {
                    setLoading(false);
                }
            } else {
                setLoading(false);
                setNfts([]);   // Clear NFTs when wallet is disconnected
                setError(null); // Clear any previous errors

            }
        };

        fetchNFTs();
    }, [publicKey]);

    if (loading) {
        return <div>Loading NFTs...</div>;
    }

    if (error) {
        return <div style={{ color: 'red' }}>Error: {error}</div>;  // Display error message
    }

    if (!publicKey) {
        return <div>Connect your wallet to view your NFTs.</div>;
    }

    return (
        <div>
            <h2>Your NFTs</h2>
            {nfts.length === 0 ? (
                <div>No NFTs found in your wallet.</div>
            ) : (
                <ul>
                    {nfts.map((nft) => (
                        <li key={nft.nft_id}>
                            <h3>{nft.metadata_url ? 'NFT Metadata' : 'Missing Metadata'}</h3>
                             {nft.metadata_url ? (
                                <>
                                    {/*  Ideally, you fetch the metadata from the URL and display it.
                                          For simplicity, I'm just providing a link to the metadata. */}
                                    <a href={nft.metadata_url} target="_blank" rel="noopener noreferrer">
                                        View NFT Metadata
                                    </a>
                                    {/* Add a download link for the metadata file
                                         You might need a separate endpoint to serve the raw metadata for download,
                                         or construct the download URL directly if IPFS is used. */}
                                </>
                            ) : (
                                <p>Metadata not available.</p>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default NFTDisplay;
```

*   **`frontend/src/components/PurchaseButton.js`**

```javascript
// frontend/src/components/PurchaseButton.js
import React, { useState } from 'react';
import { useWallet } from '@solana/wallet-adapter-react';
import { PublicKey, Transaction } from '@solana/web3.js';
import axios from 'axios';
import { connection } from '../utils/solana'; // Import the connection
import { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getOrCreateAssociatedTokenAccount, createTransferInstruction } from '@solana/spl-token';

const PurchaseButton = ({ amount, craftTokenMintAddress, decimals,  onPurchaseSuccess }) => { //amount in CRAFT
    const { publicKey, sendTransaction } = useWallet();
    const [isPurchasing, setIsPurchasing] = useState(false);
    const [errorMessage, setErrorMessage] = useState(null);

    const handlePurchase = async () => {
        setIsPurchasing(true);
        setErrorMessage(null);

        if (!publicKey) {
            setErrorMessage("Wallet not connected.");
            setIsPurchasing(false);
            return;
        }

        try {
            // 1. Get associated token accounts for both the purchaser and the recipient
            const purchaserAssociatedTokenAccount = await getOrCreateAssociatedTokenAccount(
                connection,                // connection
                publicKey,                   // payer (fee payer)
                new PublicKey(craftTokenMintAddress),  // mint
                publicKey                    // owner
            );

            const recipientAssociatedTokenAccount = await getOrCreateAssociatedTokenAccount(
                connection,                // connection
                publicKey,                   // payer (fee payer)
                new PublicKey(craftTokenMintAddress),  // mint
                new PublicKey("YOUR_RECIPIENT_PUBLIC_KEY"),                    // owner - VERY IMPORTANT:  Use recipient's wallet public key for the ATA owner
            );

             // 2. Calculate the amount to transfer (in token units)
            const amountInTokenUnits = amount * (10 ** decimals); // Assuming you have 'decimals' available

            // 3. Create the transfer instruction
            const transferInstruction = createTransferInstruction(
                purchaserAssociatedTokenAccount.address, // source
                recipientAssociatedTokenAccount.address,   // destination
                publicKey,                                  // owner/authority (signer)
                amountInTokenUnits,                         // amount
                [],                                         // multiSigners (optional)
                TOKEN_PROGRAM_ID                             // The SPL Token Program ID
            );

            const transaction = new Transaction().add(transferInstruction);
            transaction.feePayer = publicKey;
            transaction.recentBlockhash = (await connection.getLatestBlockhash()).blockhash;

            const signature = await sendTransaction(transaction, connection);

            //Call backend to verify the transaction
             const response = await axios.post('/verify_payment', { //Adjust URL - Change this to backend url
                 transactionSignature: signature,
                 userPublicKey: publicKey.toString(),
                 amount: amount,
                 craftTokenMintAddress: craftTokenMintAddress
             });

            if (response.data.success) {
                onPurchaseSuccess(response.data.nft_data); //Pass NFT data to parent component
            } else {
                setErrorMessage(response.data.error || "Payment verification failed.");
            }


            setIsPurchasing(false);

        } catch (error) {
            console.error("Purchase error:", error);
            setErrorMessage(error.message || "An error occurred during purchase.");
            setIsPurchasing(false);
        }

    };

    return (
        <div>
            <button onClick={handlePurchase} disabled={isPurchasing}>
                {isPurchasing ? "Purchasing..." : `Purchase NFT (${amount} CRAFT)`}
            </button>
            {errorMessage && <div style={{ color: 'red' }}>Error: {errorMessage}</div>}
        </div>
    );
};

export default PurchaseButton;
```

*   **`frontend/src/utils/solana.js`**

```javascript
//Used for connection on the PurchaseButton.js
import { clusterApiUrl, Connection } from '@solana/web3.js';

//The solana network you want to connect to
const network = clusterApiUrl("devnet");

//Creating the connection to the Solana network
export const connection = new Connection(network);
```

*   **`frontend/src/App.css`**

```css
/* frontend/src/App.css */
.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: calc(10px + 2vmin);
  color: white;
}

.App-link {
  color: #61dafb;
}
```

*   **`frontend/src/index.js`**

```javascript
// frontend/src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
```

**4. Environment Variables Configuration:**

*   **`backend/.env`** - **Critical Steps:**
    *   `DATABASE_URL`:  This is your PostgreSQL (or SQLite) database connection string. For PostgreSQL, it will look something like: `postgresql://username:password@host:port/database_name`.  **Replace with your actual credentials.**  For local testing with SQLite, you can use `sqlite:///./test.db` (this will create a `test.db` file in your `backend` directory).
    *   `SOLANA_RPC_URL`:  This is the URL of the Solana RPC node your application will communicate with.  For development, `https://api.devnet.solana.com` is commonly used.  You can use other providers like QuickNode, or build you own Solana Node.
    *   `CRAFT_TOKEN_MINT_ADDRESS`:  **Replace with the actual mint address** of the CRAFT token on the Solana network you're using.
    *   `ADMIN_WALLET_PRIVATE_KEY`:  **Replace with the actual private key**  of the wallet that will receive the CRAFT tokens. **This is extremely sensitive data. Handle it with utmost care.** Convert your private key to a list format.
    *   `ADMIN_WALLET_PUBLIC_KEY`:  **Replace with the public key** of the admin wallet. This correspond to the `ADMIN_WALLET_PRIVATE_KEY`.
    *   `IPFS_GATEWAY_URL`: The URL of the IPFS gateway that will be used to access the NFT images and metadata. Public gateways like `https://ipfs.io/ipfs` can be used for testing.
    *   `EMAIL_ADDRESS`:  **Replace with your actual email address.**  This address will be used to send the NFT purchase confirmation emails.
    *   `EMAIL_PASSWORD`:  **Replace with your actual email password.** If you're using Gmail, you'llOkay, I understand. I will take the previous outputs, incorporate the suggested improvements from the code review, and produce a single, complete, and fully functional code output with explanations. I will not leave anything out.

**Please provide me with the following:**

1.  **The first iteration of the code.** (The initial code you want me to finalize)
2.  **The code review with suggested improvements.** (Feedback on how to improve the initial code)

Once you provide these, I will generate the final, working code.
