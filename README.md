# A solana meme token web UI

## Overview
A modern solana meme token with a FastAPI backend and static HTML frontend. The backend aggregates token data from multiple APIs (Moralis and Birdeye) with Redis caching, while the frontend provides a beautiful, responsive UI for displaying tokenomics metrics with a panda-themed design.

## Features

### Backend (FastAPI)
- 🔄 Multi-source data aggregation from Moralis and Birdeye APIs
- 💾 Redis caching with 5-minute TTL
- 🚀 Rate limit protection and concurrent processing
- 📊 RESTful API with automatic documentation
- 🔧 Environment-based configuration
- 🎯 Modern Python packaging with pyproject.toml

### Frontend (Static HTML + CSS + JavaScript)
- 🎨 Beautiful, responsive UI with panda-themed design
- 📊 Real-time tokenomics data display
- 🔄 Auto-refresh functionality
- 📱 Mobile-friendly design
- ⚡ Fast loading with error handling
- 🎭 Custom animations and visual effects

## Quick Start

### Prerequisites
- Python 3.8+
- Redis server
- Poetry (recommended) or pip

### Why Poetry?
- 🔒 **Dependency Locking**: Exact versions for reproducible builds
- 🚀 **Faster Installation**: Optimized dependency resolution
- 🛠️ **Better Development**: Virtual environment management
- 📦 **Modern Packaging**: PEP 517/518 compliant
- 🔧 **Scripts**: Easy command execution

### 1. Install Dependencies

#### Option A: Using Poetry (Recommended)
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Or use the setup script
python poetry_setup.py

# Install dependencies
poetry install

# For development dependencies
poetry install --with dev
```

#### Option B: Using pip (Legacy)
```bash
# Install the project in editable mode
pip install -e .

# For development dependencies (optional)
pip install -e .[dev]
```

### 2. Start Redis
```bash
docker run -d --name redis -p 6379:6379 redis
```

### 3. Configure Environment
Create a `.env` file in the root directory:
```bash
HELIUS_API_KEY=your_key_here
BIRDEYE_API_KEY=your_key_here
MORALIS_API_KEY=your_key_here
TOKEN_ADDRESS=8AKBy6SkaerTMWZAad47yQxZnvrEk59DvhcHLHUsbonk
```

### 4. Run the Application
```bash
# Using Poetry (Recommended)
poetry run crypto-app
poetry run dev  # Development mode with auto-reload

# Or using Python directly
python -m app.main
```

### 5. Access the Application
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Project Structure

```
crypto/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration and environment settings
│   ├── main.py            # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py     # Pydantic data models
│   │   └── stats.py       # Statistics models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── stats.py       # API endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── moralis.py     # Moralis API integration
│   │   ├── birdeye.py     # Birdeye API integration
│   │   ├── aggregator.py  # Data aggregation and caching
│   │   ├── redis.py       # Redis caching service
│   │   └── test.py        # Service testing script
│   ├── static/
│   │   ├── index.html     # Main dashboard page
│   │   └── panda.png      # Background image
│   └── utils/
│       ├── __init__.py
│       └── format.py      # Data formatting utilities
├── pyproject.toml         # Modern Python project configuration
├── install.py             # Installation helper script
├── requirements.txt       # Legacy requirements (can be removed)
└── README.md             # This documentation
```

## Architecture

### Frontend Design
The dashboard features a beautiful panda-themed design with:
- **Responsive Grid Layout**: 4-column grid for tokenomics metrics
- **Glass Morphism**: Semi-transparent cards with backdrop blur
- **Custom Animations**: Hover effects and smooth transitions
- **Mobile Optimization**: Responsive design for all screen sizes
- **Real-time Updates**: JavaScript-powered data fetching

### Backend Architecture
The FastAPI backend provides:
- **RESTful API**: Clean, documented endpoints
- **Static File Serving**: Serves the HTML dashboard
- **CORS Support**: Cross-origin request handling
- **Health Monitoring**: Built-in health check endpoint

## How It Works

### 1. Configuration (`app/config.py`)
- Uses `pydantic-settings` for environment variable management
- Loads API keys and configuration from `.env` file
- Provides default values for Redis, API URLs, and other settings

**Key Settings:**
- `HELIUS_API_KEY`, `BIRDEYE_API_KEY`, `MORALIS_API_KEY` - API authentication
- `TOKEN_ADDRESS` - Target Solana token address
- `REDIS_HOST`, `REDIS_PORT` - Redis connection settings
- `CACHE_EXPIRATION_SECONDS` - Cache duration (default: 300s)

### 2. API Services

#### Moralis Service (`app/services/moralis.py`)
- **Purpose**: Fetches token price, name, symbol, and market data
- **Endpoint**: `https://solana-gateway.moralis.io/token/mainnet/{token_address}/price`
- **Returns**: Token metadata, USD price, 24h price change, volume

#### Birdeye Service (`app/services/birdeye.py`)
- **Purpose**: Fetches market cap, total supply, and circulating supply
- **Endpoint**: `https://public-api.birdeye.so/defi/v3/token/market-data`
- **Returns**: Market cap, supply information

### 3. Data Aggregation (`app/services/aggregator.py`)
- **Function**: `aggregated_tokenomics()`
- **Process**:
  1. **Cache Check**: First checks Redis for existing data
  2. **API Calls**: If not cached, makes concurrent calls to Moralis and Birdeye
  3. **Data Merge**: Combines results from both APIs
  4. **Caching**: Stores result in Redis for 5 minutes
  5. **Return**: Returns unified token data

**Cache Strategy:**
- Uses MD5 hash of token address as cache key
- 5-minute expiration to balance freshness and API limits
- Reduces API calls and prevents rate limiting

### 4. Redis Caching (`app/services/redis.py`)
- **Purpose**: Reduces API calls and improves response times
- **Functions**:
  - `get_cache(key)`: Retrieves cached data
  - `set_cache(key, value, expiration)`: Stores data with TTL
- **Benefits**: 
  - Avoids rate limiting (429 errors)
  - Faster response times
  - Reduces external API costs

### 5. API Endpoints (`app/routes/stats.py`)

#### GET `/api/v1/tokenomics`
- **Purpose**: Main endpoint for token data
- **Process**:
  1. Calls `aggregated_tokenomics()` service
  2. Returns cached data if available
  3. Fetches fresh data if cache miss
  4. Returns formatted response with success message

#### GET `/health`
- **Purpose**: Health check endpoint
- **Returns**: API status and basic information

### 6. Data Models (`app/models/schemas.py`)

#### `SuccessResponse`
```python
class SuccessResponse(BaseModel):
    message: str
    data: Any
```

#### `CoinData`
```python
class CoinData(BaseModel):
    token_address: str
    token_name: str
    token_symbol: str
    price_usd: Decimal
    volume_24h: Decimal
    market_cap: Decimal
    # ... other fields
```

### 7. Utility Functions (`app/utils/`)

#### `to_fixed_str(value, decimals=6)`
- Converts numbers to fixed decimal string format
- Handles scientific notation (e.g., 5.4638e-05 → "0.000055")

#### `format_to_millions(value)`
- Formats large numbers in millions (e.g., 123456789 → "123.46M")

## Data Flow

### Request Flow:
```
Client Request → FastAPI Router → Stats Route → Aggregator Service → Cache Check
                                                                    ↓
API Response ← Formatted Data ← Data Merge ← API Calls ← Cache Miss
```

### Detailed Steps:
1. **Client Request**: `GET /api/v1/tokenomics`
2. **Route Handler**: `get_tokenomics()` function in `stats.py`
3. **Service Call**: `aggregated_tokenomics()` in `aggregator.py`
4. **Cache Check**: Redis lookup using token address hash
5. **Conditional Logic**:
   - **Cache Hit**: Return cached data immediately
   - **Cache Miss**: Proceed to API calls
6. **API Calls**: Concurrent requests to Moralis and Birdeye
7. **Data Processing**: Merge and format results
8. **Caching**: Store result in Redis for future requests
9. **Response**: Return unified data to client

## Rate Limiting Solution

### Problem:
- Birdeye API has strict rate limits (1-2 requests/second)
- Multiple rapid requests cause 429 "Too Many Requests" errors

### Solution:
1. **Redis Caching**: 5-minute cache prevents repeated API calls
2. **Concurrent Requests**: Uses `asyncio.gather()` for parallel API calls
3. **Error Handling**: Graceful handling of API failures
4. **Cache-First Strategy**: Always check cache before making API calls

## Testing

### Service Testing (`app/services/test.py`)
```bash
python -m app.services.test
```

**Tests:**
- Individual service testing (Moralis, Birdeye)
- Aggregator testing with caching
- Error handling verification

### API Testing
```bash
# Start the server
python -m app.main

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/tokenomics
```

## Development

### Code Quality Tools
The project includes several development tools configured in `pyproject.toml`:

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Linting
flake8 app/

# Run tests
pytest
```

### Project Dependencies

#### Core Dependencies:
- `fastapi>=0.104.0` - Web framework
- `pydantic>=2.0.0` - Data validation
- `httpx>=0.25.0` - HTTP client
- `loguru>=0.7.0` - Logging
- `python-dotenv>=1.0.0` - Environment management
- `redis>=5.0.0` - Caching
- `uvicorn[standard]>=0.24.0` - ASGI server
- `pydantic-settings>=2.0.0` - Settings management
- `requests>=2.31.0` - HTTP requests

#### Development Dependencies:
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing
- `black>=23.0.0` - Code formatting
- `isort>=5.12.0` - Import sorting
- `flake8>=6.0.0` - Linting
- `mypy>=1.0.0` - Type checking

## Environment Setup

### Required Services:
1. **Redis Server**: For caching
   ```bash
   docker run -d --name redis -p 6379:6379 redis
   ```

2. **Python Dependencies**:
   ```bash
   poetry install
   ```

3. **Environment Variables** (`.env` file):
   ```
   HELIUS_API_KEY=your_key_here
   BIRDEYE_API_KEY=your_key_here
   MORALIS_API_KEY=your_key_here
   TOKEN_ADDRESS=8AKBy6SkaerTMWZAad47yQxZnvrEk59DvhcHLHUsbonk
   ```

## API Response Example

```json
{
  "message": "Market data retrieved successfully",
  "data": {
    "token_name": "dogshit",
    "token_symbol": "dogshit",
    "price_usd": 5.4638e-05,
    "price_change_percentage_24h": -1.6329102529480541,
    "volume_24h": 5.5545e-05,
    "market_cap": 54570.76630662628,
    "total_supply": 999593117.559368,
    "circulating_supply": 999593117.559368
  }
}
```

## Key Features

1. **Multi-Source Data**: Aggregates data from Moralis and Birdeye APIs
2. **Intelligent Caching**: Redis-based caching with 5-minute TTL
3. **Rate Limit Protection**: Prevents API rate limiting through caching
4. **Concurrent Processing**: Parallel API calls for faster responses
5. **Error Handling**: Graceful handling of API failures
6. **Data Formatting**: Consistent number formatting and display
7. **Health Monitoring**: Built-in health check endpoint
8. **API Documentation**: Auto-generated docs at `/docs`
9. **Modern Packaging**: Uses pyproject.toml for dependency management
10. **Beautiful UI**: Panda-themed responsive dashboard

## Performance Optimizations

1. **Caching**: Reduces API calls by 90%+ for repeated requests
2. **Concurrent API Calls**: Parallel requests reduce total response time
3. **Connection Pooling**: Reuses HTTP connections for API calls
4. **Data Compression**: Efficient JSON serialization
5. **Memory Management**: Proper cleanup of async resources
6. **Static File Serving**: Fast delivery of frontend assets

## Monitoring and Debugging

### Cache Status:
- "Returning cached data" - Cache hit, no API calls
- "Fetching fresh data from APIs" - Cache miss, making API calls

### Error Handling:
- API failures are caught and logged
- Graceful degradation when services are unavailable
- Detailed error messages for debugging

## Deployment

### Local Development
```bash
# Install dependencies
poetry install

# Start Redis
docker run -d --name redis -p 6379:6379 redis

# Run the application
poetry run dev
```

### Production Deployment
1. Set up environment variables
2. Install dependencies: `poetry install --only main`
3. Start Redis server
4. Run with production ASGI server: `poetry run crypto-app`

This architecture provides a robust, scalable solution for cryptocurrency data aggregation with built-in performance optimizations, error handling, and a beautiful user interface. 
