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
            } else {\n                setLoading(false);
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