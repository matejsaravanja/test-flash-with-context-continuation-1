# test-flash-with-context-continuation-1

## About
This code was generated by [CodeCraftAI](https://codecraft.name)

**User requests:**
I want you to build me an app for buying premium NFTs. I want user to pay me 100 CRAFT (of course, user has to sign transaction). That transaction and user ownership of certain NFT should be stored somewhere. CRAFT is a Solana-based token btw. Once paid, user has to get access to that NFT in form of web, mail and image. For NFTs, generate some nice svg images.
- Can you add backend-required docker files as well as frontend-required docker files. I'd also love to be able to deploy it via github actions.

Check OUTPUT.md for the complete unaltered output.

## Project Plan
```
Okay, based on the project requirements and the clarifications needed, here's a project plan for building the NFT purchase app:

**Project Name:** NFT Purchase App

**Overall Goal:** Develop a web application enabling users to purchase premium NFTs using CRAFT tokens on the Solana blockchain and access them via web, email, and image download.

**Assumptions:**

*   We will receive answers to all questions listed in the "Constraints and Clarifications Needed" section promptly.
*   Dependencies (e.g., libraries, APIs) will be readily available.
*   The CRAFT token is already deployed on the Solana blockchain (awaiting Mint Address).

**I.  Project Setup & Infrastructure (Sprint 0 - 1 week)**

*   **Tasks:**
    *   **1.1 Requirements Gathering & Documentation Finalization:**
        *   **Subtasks:**  Finalize answers to the "Constraints and Clarifications Needed" questions.  Document all project requirements and assumptions in detail.
    *   **1.2 Infrastructure Setup:** *(Requires answers from Constraints)*
        *   **Subtasks:**
            *   Set up the development environment (React frontend, Python backend framework, database).
            *   Configure the chosen email service provider.
            *   Establish a connection to the Solana blockchain (using a Solana SDK / Library).
            *   Choose and configure NFT storage solution (centralized or IPFS).
        *   **Technical Considerations:** Dependency management (pip, npm), cloud provider considerations (if any), setting up API keys and environment variables securely.
    *   **1.3 Project Structure & Code Repository:**
        *   **Subtasks:**
            *   Create a GitHub (or similar) repository for the project.
            *   Establish a clear project directory structure for both frontend and backend.
            *   Implement basic CI/CD pipeline for testing and deployment (optional for initial MVP).
        *   **Technical Considerations:** Version control (Git), branch management strategy.

**II. Core Functionality Development (Sprint 1-3 - 3-4 weeks)**

*   **Module 1: Solana Wallet Integration & CRAFT Token Payment (1.5 weeks)**
    *   **Tasks:**
        *   **2.1 Wallet Adapter Implementation:** Integrate chosen Solana wallet(s) into the React frontend.
        *   **2.2 CRAFT Token Balance Display:** Display the user's CRAFT token balance.
        *   **2.3 Transaction Signing Functionality:** Implement logic for users to sign transactions using their Solana wallet.
        *   **2.4 Backend Payment Verification:**  Backend verifies the signed transaction and confirms the CRAFT token transfer.
        *   **2.5 Error Handling:** Handle common wallet connection and transaction errors gracefully.
    *   **Technical Considerations:** Using Solana web3.js library, Phantom SDK, Solflare SDK (or similar, based on wallet choice).  Transaction fee calculation.  Error handling and user feedback. Preventing double-spending vulnerabilities by verifying transactions with multiple Solana RPC Nodes/Providers.

*   **Module 2: NFT Generation & Storage (1 week)**
    *   **Tasks:**
        *   **3.1 SVG Generation Logic:**  Develop a Python script to generate unique SVG images for each NFT.
        *   **3.2 NFT Metadata Creation:**  Create JSON metadata for each NFT.
        *   **3.3 Storage Integration:** Upload the SVG image and metadata to the chosen storage solution (IPFS or centralized storage).
        *   **3.4 Database Integration** Store all the metadata to the database of choice
        *   **3.5 Retrieve from Database** Retrieve generated Metadata associated with User
    *   **Technical Considerations:** SVG generation library (e.g., Pillow in Python), IPFS integration (if chosen), API integration with storage provider, Metadata standards (e.g., ERC-721 compatible).  Ensuring unique NFT generation.

*   **Module 3: NFT Access & Delivery (1 week)**
    *   **Tasks:**
        *   **4.1 Web Interface Display:**  Display the user's owned NFTs within the web application.
        *   **4.2 Downloadable SVG Implementation:**  Provide functionality to download the NFT as an SVG file.
        *   **4.3 Email Integration:**  Send an email to the user containing a link to view their NFT or embed the NFT data/image (depending on requirements).
    *   **Technical Considerations:**  Frontend image rendering, email template design, API calls to retrieve NFT metadata and storage URLs.

**III. Data Storage & Tracking (Sprint 4 - 1 week)**

*   **Tasks:**
    *   **5.1 Database Schema Design:** Design the database schema to store transaction history and NFT ownership information.
    *   **5.2 Transaction History Logging:** Log all successful purchase transactions to the database (transaction ID, user, NFT ID).
    *   **5.3 Ownership Tracking:** Update the database to reflect NFT ownership based on successful purchases.
    *   **5.4 Implement API endpoints for storing and retrieving the transactions.**
    *   **5.5 Implement front end components for display.**
*   **Technical Considerations:** Choosing appropriate data types and indexes for efficient querying, database connection management, security considerations for storing sensitive data.

**IV. Testing & Quality Assurance (Sprint 5 - 1 week)**

*   **Tasks:**
    *   **6.1 Unit Testing:** Write unit tests for individual components and functions.
    *   **6.2 Integration Testing:**  Test the integration between different modules (e.g., payment flow, NFT generation, email delivery).
    *   **6.3 User Acceptance Testing (UAT):**  Have users test the application and provide feedback.
    *   **6.4 Security Audits:** Look for vulnerabilities in the system.
    *   **6.5 Bug Fixing:** Fix discovered bugs.
*   **Technical Considerations:**  Choosing appropriate testing frameworks, writing comprehensive test cases, addressing security vulnerabilities.

**V. Deployment & Monitoring (Sprint 6 - 1 week)**

*   **Tasks:**
    *   **7.1 Deployment:** Deploy the application to a production environment.
    *   **7.2 Monitoring:** Set up monitoring tools to track application performance and errors.
    *   **7.3 Documentation:** Create user and developer documentation.
*   **Technical Considerations:**  Choosing a deployment platform (e.g., cloud provider, server hosting), configuring servers and databases, setting up logging and alerting.

**Technical Considerations (General):**

*   **Security:**  Prioritize security throughout the development process. Implement measures to prevent common web application vulnerabilities (e.g., XSS, SQL injection). Securely store API keys and sensitive data.  Regularly audit the codebase for security flaws.
*   **Scalability:** (Address this *after* receiving feedback on projected user base) Design the application with scalability in mind, especially considering the potential for a large number of users and NFT purchases.  Consider using a scalable database and infrastructure.
*   **Error Handling:**  Implement robust error handling to gracefully handle unexpected errors and provide informative feedback to the user.
*   **Code Quality:**  Maintain high code quality by following coding standards, writing clear and concise code, and using code linting tools.

**Communication & Reporting:**

*   Daily stand-up meetings to discuss progress and blockers.
*   Weekly sprint reviews to demo completed work.
*   Regular communication with stakeholders to provide updates and gather feedback.

**Success Metrics:**

*   Successful NFT purchases and deliveries.
*   High application uptime and performance.
*   Positive user feedback.
*   Adherence to security best practices.

**Dependencies:**

*   Completion of requirements gathering (answers to outstanding clarification points).
*   Availability of necessary APIs and libraries (Solana SDK, email service provider API, etc.).

This project plan provides a high-level framework for developing the NFT purchase app.  It will be refined and adjusted based on feedback and evolving requirements.

```
