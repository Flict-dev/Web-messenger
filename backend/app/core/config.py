from secrets import token_hex


class Settings:
    API_V1_STR: str = "/api/v1"
    # in prod use token_hex
    SECRET_KEY: str = "9057e8f415a4ed8b2f01deaaad52baf7d30e59604939e3e4cce324444ec4acfb"
    CSRF_SECRET_KEY: str = "e95ff35efa414a5872edcd0dbf4d5d6a108c4a673673cf03acaebe5ab2a13f2e"
    JWT_TIME_LIVE: int = 10800
    DBURL: str = "sqlite:///sqlite.db"
    # turn of in production
    DEBUG: bool = True
    PROJECT_NAME: str = "Web Messenger"
    PROJECT_VERSION: str = "1.0.0"


settings = Settings()
