import logging.config
from pathlib import Path
import sys

def setup_logging():
    Path("logs").mkdir(exist_ok=True)
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d '
                        '[PID:%(process)d] %(message)s'
            },
            'simple': {'format': '%(levelname)s - %(message)s'}
        },
        'filters': {
            'no_sqlalchemy': {
                '()': 'app.utils.logging.NoSQLAlchemyFilter'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'stream': sys.stdout
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,
                'backupCount': 14,
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filters': ['no_sqlalchemy']
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        },
        'loggers': {
            'app': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'app.http': {
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'sqlalchemy.engine': {
                'level': 'WARNING',
                'handlers': ['console', 'file'],
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(config)

class NoSQLAlchemyFilter(logging.Filter):
    def filter(self, record):
        if 'sqlalchemy.engine' in record.name and record.levelno < logging.WARNING:
            return False
        if any(x in record.getMessage() for x in ['BEGIN', 'COMMIT', 'raw sql', '[generated', '[cached']):
            return False
        return True
