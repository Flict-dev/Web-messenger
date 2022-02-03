from secrets import token_hex


class Settings:
    API_V1_STR: str = "/api/v1"
    # in prod use token_hex
    SECRET_KEY: str = token_hex(32)
    CSRF_SECRET_KEY: str = token_hex(32)
    JWT_TIME_LIVE: int = 10800
    DBURL: str = "sqlite:///sqlite.db"
    # turn of in production
    DEBUG: bool = False
    PROJECT_NAME: str = "Web Messenger"
    PROJECT_VERSION: str = "1.0.0"


settings = Settings()
