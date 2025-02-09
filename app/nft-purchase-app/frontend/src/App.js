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