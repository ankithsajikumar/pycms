import os
import django
import logging
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pycms.settings')
django.setup()

logger = logging.getLogger('maintenance')

def clear_expired_entities():
    try:
        call_command('cleartokens')
        call_command('clearmessages')
        logger.info("Successfully cleared expired entities")
    except Exception as e:
        logger.error(f"Error clearing entities: {e}")

if __name__ == "__main__":
    clear_expired_entities()