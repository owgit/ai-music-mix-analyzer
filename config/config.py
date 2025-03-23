"""
Base configuration file
Private settings should be placed in config/private_config.py
"""

class Config:
    """Base config class"""
    DEBUG = False
    TESTING = False
    ENABLE_ANALYTICS = False
    MATOMO_URL = None
    MATOMO_SITE_ID = None

    @classmethod
    def init_app(cls, app):
        """Initialize app configuration"""
        try:
            from config.private_config import (
                ENABLE_ANALYTICS,
                MATOMO_URL,
                MATOMO_SITE_ID
            )
            app.config['ENABLE_ANALYTICS'] = ENABLE_ANALYTICS
            app.config['MATOMO_URL'] = MATOMO_URL
            app.config['MATOMO_SITE_ID'] = MATOMO_SITE_ID
        except ImportError:
            if isinstance(cls, ProductionConfig):
                raise RuntimeError(
                    "Production environment requires config/private_config.py. "
                    "Please copy config/private_config.py.example to config/private_config.py "
                    "and update with your settings."
                )
            # In development/testing, use defaults
            pass

class DevelopmentConfig(Config):
    """Development config"""
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    """Production config"""
    # Analytics settings will be loaded from private_config.py
    pass

class TestingConfig(Config):
    """Testing config"""
    TESTING = True
    DEBUG = True 