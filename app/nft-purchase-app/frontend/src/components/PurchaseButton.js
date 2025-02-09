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