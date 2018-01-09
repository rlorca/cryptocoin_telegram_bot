"""
Telegram bot to monitor crypto coin valuation.
"""

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(thread)s -  %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
