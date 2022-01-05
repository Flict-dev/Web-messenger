from secrets import token_hex


class Settings:
    API_V1_STR: str = '/api/v1'
    # in prod use token_hex
    SECRET_KEY: str = '9057e8f415a4ed8b2f01deaaad52baf7d30e59604939e3e4cce324444ec4acfb'
    DBURL: str = 'sqlite:///sqlite.db'
    # turn of in production
    DEBUG: bool = True
    PROJECT_NAME: str = 'Web Messenger'
    PROJECT_VERSION: str = '1.0.0'


settings = Settings()
