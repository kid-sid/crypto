from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HELIUS_API_KEY: str = ""
    BIRDEYE_API_KEY: str = ""
    SOLCAN_API_KEY: str = ""
    MORALIS_API_KEY: str = ""

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    CACHE_EXPIRATION_SECONDS: int = 300

    HELIUS_API_URL: str = "https://api.helius.xyz"
    TOKEN_ADDRESS: str = ""
    
    # Additional fields that might be in environment
    MORALIS_URL: str = "https://solana-gateway.moralis.io/token/mainnet/holders/"
    BIRDEYE_URL: str = "https://public-api.birdeye.so/public/token/market-data?address="

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields

settings = Settings()