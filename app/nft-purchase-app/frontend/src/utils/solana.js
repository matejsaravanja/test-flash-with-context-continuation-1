//Used for connection on the PurchaseButton.js
import { clusterApiUrl, Connection } from '@solana/web3.js';

//The solana network you want to connect to
const network = clusterApiUrl("devnet");

//Creating the connection to the Solana network
export const connection = new Connection(network);