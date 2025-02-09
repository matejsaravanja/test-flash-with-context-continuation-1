**This file consists of the entire unaltered output for reference.**

```json
{
  "nft-purchase-app/frontend/package.json": {
    "content": "{\n  \"name\": \"frontend\",\n  \"version\": \"0.1.0\",\n  \"private\": true,\n  \"dependencies\": {\n    \"@solana/wallet-adapter-base\": \"^0.9.22\",\n    \"@solana/wallet-adapter-react\": \"^0.15.32\",\n    \"@solana/wallet-adapter-react-ui\": \"^0.9.31\",\n    \"@solana/wallet-adapter-wallets\": \"^0.9.23\",\n    \"@solana/web3.js\": \"^1.78.4\",\n    \"axios\": \"^1.6.2\",\n    \"react\": \"^18.2.0\",\n    \"react-dom\": \"^18.2.0\",\n    \"react-scripts\": \"5.0.1\"\n  \",\n    \"web-vitals\": \"^2.1.4\"\n  },\n  \"scripts\": {\n    \"start\": \"react-scripts start\",\n    \"build\": \"react-scripts build\",\n    \"test\": \"react-scripts test\",\n    \"eject\": \"react-scripts eject\"\n  },\n  \"eslintConfig\": {\n    \"extends\": [\n      \"react-app\",\n      \"react-app/jest\"\n    ]\n  },\n  \"browserslist\": {\n    \"production\": [\n      \">0.2%\",\n      \"not dead\",\n      \"not op_mini all\"\n    ],\n    \"development\": [\n      \"last 1 chrome version\",\n      \"last 1 firefox version\",\n      \"last 1 safari version\"\n    ]\n  }\n}\n"
  },
  "nft-purchase-app/frontend/Dockerfile": {
    "content": "FROM node:16-alpine\n\nWORKDIR /app\n\nCOPY package*.json .\nRUN npm install\n\nCOPY . .\n\n# Add a command to set the background color to green\nCMD [\"sh\", \"-c\", \"export BACKGROUND_COLOR=green && npm start\"]"
  }
}
```