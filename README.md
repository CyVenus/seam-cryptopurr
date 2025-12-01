<div align="center">

![Seam CryptoPurr Logo](assets/logo.jpg)

# Seam CryptoPurr 🐱💰

**A Comprehensive Multi-Agent Cryptocurrency Assistant**

*Powered by Google Agent Development Kit (ADK) & Gemini 2.5*

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![ADK](https://img.shields.io/badge/ADK-0.1.0+-green.svg)](https://developers.google.com/adk)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Problem Statement](#-problem-statement)
- [Problem Solution](#-problem-solution)
- [Architecture](#-architecture)
- [Essential Tools and Utilities](#-essential-tools-and-utilities)
- [Installation](#-installation)
- [Project Structure](#-project-structure)
- [Workflow](#-workflow)
- [Value Statement](#-value-statement)
- [Conclusion](#-conclusion)

---

## 🎯 Project Overview

**Seam CryptoPurr** is an intelligent, multi-agent cryptocurrency assistant system that leverages specialized AI agents to provide comprehensive crypto market analysis, on-chain security checks, portfolio management, news aggregation, and educational content.

The system uses a sophisticated routing architecture where a master router agent intelligently delegates user queries to specialized sub-agents, each expert in their domain. This modular approach ensures accurate, efficient, and context-aware responses to all cryptocurrency-related inquiries.

### Key Capabilities

- 📊 **Real-time Market Data** - Live prices, charts, and market metrics
- 🔒 **On-Chain Security Analysis** - Token safety verification and risk assessment
- 🔗 **Multi-Chain Transaction Checking** - Bitcoin, EVM chains, and Solana support
- 💼 **Portfolio Management** - Multi-wallet tracking and aggregation
- 📰 **News Aggregation** - Real-time crypto news from major outlets
- 📈 **Market Sentiment** - Fear & Greed Index and mood analysis
- 🎓 **Crypto Education** - Beginner-friendly explanations
- 🔔 **Price Alerts** - Custom alerts with email notifications
- 🎭 **Entertainment** - Memes and fun crypto content

---

## ❓ Problem Statement

The cryptocurrency ecosystem is complex and fragmented, presenting several challenges for users:

1. **Information Fragmentation**: Crypto data is scattered across multiple platforms, APIs, and services, making it difficult to get a comprehensive view.

2. **Security Concerns**: Users need to verify token safety, check for rug pulls, and assess on-chain risks before investing, but this requires technical expertise and access to multiple tools.

3. **Time-Consuming Research**: Gathering market data, news, and analysis from different sources is time-consuming and inefficient.

4. **Lack of Unified Interface**: No single platform provides market data, security analysis, portfolio tracking, news, and education in one place.

5. **Technical Barriers**: Many crypto tools require technical knowledge, API keys, and complex setups that deter casual users.

6. **Real-Time Monitoring**: Users need to constantly monitor prices, news, and market conditions, which is impractical without automation.

---

## 💡 Problem Solution

**Seam CryptoPurr** solves these challenges through a **multi-agent architecture** that:

### 1. **Unified Intelligence Hub**
   - Single entry point for all crypto-related queries
   - Intelligent routing to specialized agents
   - No need to switch between multiple tools or platforms

### 2. **Specialized Agent Expertise**
   - Each agent is an expert in its domain
   - Agents can work sequentially or in parallel
   - Complex workflows are handled automatically

### 3. **Comprehensive Data Integration**
   - Integrates multiple APIs and data sources:
     - CoinGecko MCP for market data
     - DexScreener for on-chain analysis
     - Etherscan, Blockstream, Solscan for blockchain data
     - RSS feeds (CoinDesk, Decrypt, CoinTelegraph) for news
     - Google Search for additional context

### 4. **Automated Workflows**
   - Parallel data fetching for efficiency
   - Sequential processing for complex analysis
   - Automated alert checking and notifications

### 5. **User-Friendly Interface**
   - Natural language interaction
   - No technical knowledge required
   - Simple setup with minimal configuration

### 6. **Extensible Architecture**
   - Easy to add new agents
   - Modular design for maintenance
   - Tool-based integration for new services

---

## 🏗️ Architecture

![System Architecture Flow](assets/flow.jpg)

### High-Level Architecture

Seam CryptoPurr follows a **hierarchical multi-agent architecture**:

```
ROOT AGENT (router_agent)
├── AgentTool → Market Data Agent
├── AgentTool → On-Chain Analysis Agent (Sequential)
├── AgentTool → Blockchain Checker Agent (Sequential)
├── AgentTool → Portfolio Manager Agent
├── AgentTool → News Research Agent (Sequential)
├── AgentTool → Sentiment Agent
├── AgentTool → Crypto Education Agent
├── AgentTool → Crypto Memes Agent
├── AgentTool → Toss Agent
└── AgentTool → Alerts Agent
```

### Agent Types

1. **Router Agent (LlmAgent)**
   - Main entry point and intelligent router
   - Analyzes user queries and routes to appropriate sub-agents
   - Never answers directly - always delegates to specialists

2. **Sequential Agents**
   - Execute sub-agents in sequence
   - Used for multi-step workflows (fetch → analyze → summarize)
   - Example: On-Chain Analysis Agent

3. **Parallel Agents**
   - Execute sub-agents concurrently
   - Used for independent data fetching
   - Example: News Research Agent (fetches from multiple sources simultaneously)

4. **LlmAgents with Tools**
   - Specialized agents with domain-specific tools
   - Can call APIs, access databases, or perform computations
   - Example: Market Data Agent with CoinGecko MCP

### Detailed Agent Breakdown

#### 1. Market Data Agent
- **Type**: LlmAgent
- **Tool**: CoinGecko MCP (via StreamableHTTP)
- **Function**: Real-time price quotes, charts, market metrics

#### 2. On-Chain Analysis Agent
- **Type**: SequentialAgent
- **Flow**:
  1. `onchain_fetch_agent` → DexScreener API → `onchain_raw_data`
  2. `onchain_summary_agent` → Google Search + Analysis → Security Report

#### 3. Blockchain Checker Agent
- **Type**: SequentialAgent
- **Flow**:
  1. `blockchain_scan_agent` → Multi-chain APIs → `blockchain_scan_snapshot`
  2. `blockchain_summary_agent` → Formatted transaction/wallet report

#### 4. Portfolio Manager Agent
- **Type**: LlmAgent
- **Tools**: `add_to_portfolio_tool`, `refresh_portfolio_tool`
- **Database**: SQLite (`portfolio.db`)
- **Function**: Multi-wallet tracking and aggregation

#### 5. News Research Agent
- **Type**: SequentialAgent
- **Flow**:
  1. `overall_news_parallel_agent` (Parallel):
     - `headlines_fetch_agent` → CoinDesk + Decrypt RSS
     - `altcoins_fetch_agent` → CoinTelegraph RSS
     - `google_news_fetch_agent` → Google Search
  2. `news_summary_agent` → Comprehensive news digest

#### 6. Sentiment Agent
- **Type**: LlmAgent
- **Tool**: `fear_greed_tool` → Alternative.me API
- **Function**: Market sentiment analysis

#### 7. Crypto Education Agent
- **Type**: LlmAgent
- **Tool**: Google Search
- **Function**: Educational content and explanations

#### 8. Crypto Memes Agent
- **Type**: LlmAgent
- **Tool**: Google Search
- **Function**: Crypto memes and entertainment

#### 9. Toss Agent
- **Type**: LlmAgent
- **Tool**: `toss_tool`
- **Function**: Random coin flip decisions

#### 10. Alerts Agent
- **Type**: LlmAgent
- **Tools**: `add_alert_tool`, `cancel_alert_tool`, `list_alerts_tool`, `test_email_tool`, `run_alert_checker_tool`
- **Database**: SQLite (`alerts.db`)
- **External**: SMTP (Gmail), CoinGecko API
- **Function**: Price alerts with email notifications

### Design Patterns

- **Sequential Processing**: For workflows requiring ordered steps
- **Parallel Processing**: For independent data fetching
- **Tool Integration**: Custom Python tools and MCP servers
- **State Management**: Shared state between agents in a sequence
- **Error Handling**: Graceful degradation and retry logic

---

## 🛠️ Essential Tools and Utilities

### External APIs & Services

| Service | Purpose | Authentication |
|---------|---------|----------------|
| **CoinGecko MCP** | Market data, prices, charts | MCP (coingecko) |
| **DexScreener API** | On-chain DEX data, liquidity | Public |
| **Etherscan API** | Ethereum blockchain data | etherscan |
| **Blockstream API** | Bitcoin blockchain data | Public |
| **Solscan API** | Solana blockchain data | Public |
| **Alternative.me** | Fear & Greed Index | Public |
| **RSS Feeds** | CoinDesk, Decrypt, CoinTelegraph | Public |
| **Google Search** | Additional context and verification | ADK Tool |
| **SMTP (Gmail)** | Email alerts | User credentials |

### Custom Tools

#### Market Data Tools
- `CoinGecko MCP Toolset` - Market data via MCP protocol

#### On-Chain Analysis Tools
- `dexscreener_tool` - DEX pair and liquidity data
- `google_search` - Scam/rug detection via web search

#### Blockchain Tools
- `evm_scan_tool` - EVM chain transaction scanning
- `btc_scan_tool` - Bitcoin transaction scanning
- `sol_scan_tool` - Solana transaction scanning

#### Portfolio Tools
- `add_to_portfolio_tool` - Add wallet addresses
- `refresh_portfolio_tool` - Update portfolio balances

#### News Tools
- `coindesk_decrypt_tool` - RSS feed aggregation
- `cointelegraph_tool` - Altcoin news feed
- `google_search` - Topic-specific news search

#### Alert Tools
- `add_alert_tool` - Create price alerts
- `cancel_alert_tool` - Remove alerts
- `list_alerts_tool` - View all alerts
- `test_email_tool` - Test email configuration
- `run_alert_checker_tool` - Check and trigger alerts

#### Utility Tools
- `fear_greed_tool` - Market sentiment index
- `toss_tool` - Random coin flip

### Databases

- **SQLite (`portfolio.db`)**: Stores wallet addresses and portfolio data
- **SQLite (`alerts.db`)**: Stores price alert configurations

### Helper Utilities

Located in `sub_agents/helper_func_tools/`:
- `general_helper_tools.py` - Blockchain scanning utilities
- `alert_storage.py` - Alert database operations
- `alert_tools.py` - Alert management functions
- `smtp_tools.py` - Email notification utilities

---

## 🚀 Installation

### Prerequisites

- **Python 3.11+**
- **Google Agent Development Kit (ADK)**
- **API Keys** (optional, for enhanced features)

### Step-by-Step Setup

1. **Navigate to the project directory:**
   ```bash
   cd "./Seam-CryptoPurr"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables (optional):**
   
   Create a `.env` file in the project root:
   ```env
   # Blockchain APIs (optional)
   ETHERSCAN_API_KEY=your_etherscan_key_here
   
   # Email alerts (optional)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASS=your_app_password
   
   # CoinGecko MCP (optional, defaults to public URL)
   COINGECKO_MCP_URL=https://mcp.api.coingecko.com/mcp
   ```

5. **Run the agent:**
   ```bash
   adk web
   ```

   The web interface will open at `http://localhost:8000`

### Verification

Test the installation by asking:
- "What's the price of Bitcoin?"
- "Show me the latest crypto news"
- "What's the market sentiment?"

---

## 📁 Project Structure

```
Seam_CryptoPurr/
├── __init__.py                    # Package initialization
├── agent.py                       # Main router agent
├── config.py                      # Configuration settings
├── README.md                      # This file
├── requirements.txt               # Python dependencies
│
├── assets/                        # Project assets
│   ├── logo.jpg                   # Project logo
│   └── flow.jpg                   # Architecture diagram
│
├── sub_agents/                    # Specialized sub-agents
│   ├── __init__.py
│   │
│   ├── market_data_agent.py       # Market data & prices
│   ├── onchain_analysis_agent.py  # Token security analysis
│   ├── blockchain_checker_agent.py # Multi-chain transaction checker
│   ├── portfolio_manager_agent.py  # Portfolio tracking
│   ├── news_research_agent.py     # News aggregation
│   ├── sentiment_agent.py         # Market sentiment
│   ├── crypto_education_agent.py  # Educational content
│   ├── crypto_memes_agent.py      # Entertainment
│   ├── toss_agent.py              # Random decisions
│   ├── alerts_agent.py            # Price alerts
│   │
│   ├── helper_func_tools/         # Shared utilities
│   │   ├── __init__.py
│   │   ├── general_helper_tools.py  # Blockchain utilities
│   │   ├── alert_storage.py         # Alert database ops
│   │   ├── alert_tools.py            # Alert management
│   │   └── smtp_tools.py             # Email utilities
│   │
│   └── scripts/                   # Utility scripts
│       └── alert_check_script.py   # Alert checker script
│
└── tests/                         # Test suite
    ├── __init__.py
    ├── test_agent.py              # Integration tests
    └── README.md                  # Testing documentation
```

### Key Files

- **`agent.py`**: Defines the root router agent and routing logic
- **`config.py`**: Centralized configuration (models, API keys, database paths)
- **`sub_agents/*.py`**: Individual agent implementations
- **`helper_func_tools/*.py`**: Reusable utility functions

---

## 🔄 Workflow

### Request Flow

1. **User Query** → Router Agent receives natural language query

2. **Intent Analysis** → Router analyzes query to determine intent:
   - Market data request?
   - Security check?
   - News query?
   - Portfolio operation?
   - etc.

3. **Agent Selection** → Router selects the most appropriate sub-agent:
   - Uses `AgentTool` wrapper for tool-based invocation
   - Ensures no nested function calling issues

4. **Agent Execution**:
   - **Simple Agents**: Execute directly with their tools
   - **Sequential Agents**: Execute sub-agents in order, passing state
   - **Parallel Agents**: Execute sub-agents concurrently

5. **Data Processing**:
   - Agents fetch data from APIs, databases, or tools
   - Process and analyze the data
   - Format results for user consumption

6. **Response Generation** → Agent returns formatted response to user

### Example Workflows

#### Market Data Query
```
User: "What's the price of Bitcoin?"
  ↓
Router Agent → Market Data Agent
  ↓
Market Data Agent → CoinGecko MCP Tool
  ↓
Response: "Bitcoin (BTC) is currently trading at $XX,XXX..."
```

#### On-Chain Security Check
```
User: "Is this token safe? 0x123..."
  ↓
Router Agent → On-Chain Analysis Agent (Sequential)
  ↓
Step 1: onchain_fetch_agent → DexScreener API
  ↓
Step 2: onchain_summary_agent → Google Search + Analysis
  ↓
Response: "Security Assessment: [Risk Score] [Details]..."
```

#### News Aggregation
```
User: "Show me the latest crypto news"
  ↓
Router Agent → News Research Agent (Sequential)
  ↓
Step 1: Parallel Fetch (3 agents simultaneously)
  - headlines_fetch_agent → CoinDesk + Decrypt
  - altcoins_fetch_agent → CoinTelegraph
  - google_news_fetch_agent → Google Search
  ↓
Step 2: news_summary_agent → Combine & Format
  ↓
Response: "Latest Crypto News: [Comprehensive Digest]..."
```

#### Portfolio Management
```
User: "Add this address to my portfolio: bc1q..."
  ↓
Router Agent → Portfolio Manager Agent
  ↓
Portfolio Manager Agent → add_to_portfolio_tool
  ↓
Tool → SQLite Database (portfolio.db)
  ↓
Response: "Address added. Current balance: [Amount]..."
```

### State Management

- **Sequential Agents** share state between steps
- **Parallel Agents** collect results independently
- **Output Keys** allow agents to store/retrieve data from state
- **State Persistence** for portfolio and alerts via SQLite

---

## 💎 Value Statement

### For Users

✅ **One-Stop Solution**: All crypto needs in one intelligent assistant  
✅ **Time-Saving**: No need to switch between multiple tools  
✅ **Security**: Built-in risk assessment and verification  
✅ **Accessibility**: Natural language interface, no technical knowledge required  
✅ **Comprehensive**: Market data, news, analysis, education, and more  
✅ **Automation**: Price alerts and portfolio tracking  

### For Developers

✅ **Modular Architecture**: Easy to extend and maintain  
✅ **Best Practices**: Follows ADK design patterns  
✅ **Well-Documented**: Clear structure and comprehensive docs  
✅ **Extensible**: Simple to add new agents or tools  
✅ **Type-Safe**: Python type hints throughout  
✅ **Testable**: Modular design enables unit and integration testing  

### For Organizations

✅ **Scalable**: Multi-agent architecture handles complex workflows  
✅ **Reliable**: Error handling and graceful degradation  
✅ **Maintainable**: Clean separation of concerns  
✅ **Cost-Effective**: Efficient use of API calls and resources  
✅ **Future-Proof**: Easy to integrate new services and APIs  

---

## 🎓 Conclusion

**Seam CryptoPurr** represents a comprehensive solution to the fragmented cryptocurrency information landscape. By leveraging Google's Agent Development Kit and a sophisticated multi-agent architecture, it provides users with:

- **Intelligent Routing**: Smart delegation to specialized agents
- **Comprehensive Coverage**: Market data, security, news, education, and more
- **Efficient Processing**: Parallel and sequential workflows optimized for performance
- **User-Friendly Interface**: Natural language interaction with no technical barriers
- **Extensible Design**: Easy to add new capabilities and integrate new services

The system demonstrates the power of multi-agent AI architectures in solving complex, real-world problems by breaking them down into specialized, manageable components.

### Future Enhancements

- 🔮 **Advanced Analytics**: Technical indicators and chart analysis
- 🔮 **Social Integration**: Twitter/X sentiment analysis
- 🔮 **DeFi Integration**: Yield farming and staking information
- 🔮 **NFT Support**: NFT portfolio tracking and analysis
- 🔮 **Multi-Language**: Support for multiple languages
- 🔮 **Voice Interface**: Voice-activated interactions

---

## 📚 Additional Resources

- [Google Agent Development Kit Documentation](https://developers.google.com/adk)
- [Gemini API Documentation](https://ai.google.dev/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [DexScreener API](https://docs.dexscreener.com/)

---

## 📄 License

This project is licensed under the **Apache 2.0 License**.

---

## 🙏 Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://developers.google.com/adk)
- Powered by **Gemini 2.5** models
- Data sources: CoinGecko, DexScreener, Etherscan, Blockstream, Solscan, CoinDesk, Decrypt, CoinTelegraph

---

<div align="center">

**Happy CryptoPurr Analysis! 🚀**

</div>
