from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str
    
    # Postgres
    PG_PORT: str
    PG_DB: str
    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str

    # Redis
    RD_PORT: str
    RD_PASSWORD: str
    RD_HOST: str

    # Clickhouse
    CL_HOST: str
    CL_PORT: str
    CL_USER: str
    CL_PASSWORD: str
    CL_DB: str

    GOOGLE_API_KEY: str
    BASE_URL: str
    
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )


settings = Settings()
