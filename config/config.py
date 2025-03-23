class Config:
    ENABLE_ANALYTICS = False
    MATOMO_URL = None
    MATOMO_SITE_ID = None

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    ENABLE_ANALYTICS = True
    # These values will be overridden by instance/config.py 