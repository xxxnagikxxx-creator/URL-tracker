from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, computed_field

class DatabaseSettings(BaseModel):
    db_host: str 
    db_port: int 
    db_user: str 
    db_password: str 
    db_name: str 
    
    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

class RedisSettings(BaseModel):
    redis_host: str
    redis_port: int
    redis_password: str
    
    @computed_field
    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"

class JWTSettings(BaseModel):
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str

class TelegramSettings(BaseModel):
    telegram_bot_token: str

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        env_nested_delimiter="__", 
        extra="ignore"
    )
    
    db_host: str 
    db_port: int 
    db_user: str 
    db_password: str 
    db_name: str 
    
    redis_host: str
    redis_port: int
    redis_password: str
    
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str
    
    telegram_bot_token: str

    @computed_field
    @property
    def db_settings(self) -> DatabaseSettings:
        return DatabaseSettings(
            db_host=self.db_host,
            db_port=self.db_port,
            db_user=self.db_user,
            db_password=self.db_password,
            db_name=self.db_name
        )

    @computed_field
    @property
    def redis_settings(self) -> RedisSettings:
        return RedisSettings(
            redis_host=self.redis_host,
            redis_port=self.redis_port,
            redis_password=self.redis_password
        )

    @computed_field
    @property
    def jwt_settings(self) -> JWTSettings:
        return JWTSettings(
            jwt_algorithm=self.jwt_algorithm,
            access_token_expire_minutes=self.access_token_expire_minutes,
            refresh_token_expire_days=self.refresh_token_expire_days,
            secret_key=self.secret_key
        )

    @computed_field
    @property
    def telegram_settings(self) -> TelegramSettings:
        return TelegramSettings(
            telegram_bot_token=self.telegram_bot_token
        )

settings = Settings()
