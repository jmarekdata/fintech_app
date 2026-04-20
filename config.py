class Settings(BaseSettings):
    DATABASE_URL: str
    STRIPE_SECRET_KEY_SANDBOX: str
    AIRALO_API_KEY: str = "MOCK_KEY" 
    AIRALO_API_SECRET: str = "MOCK_SECRET"
    USE_AIRALO_MOCK: bool = True 

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")