import logging

import os

from ctb.bot import QuoteBot
from ctb.quote import QuoteLoader, LoadScheduler

logging.getLogger(__name__).addHandler(logging.NullHandler())

token = os.environ['TELEGRAM_TOKEN']

logging.info("Starting bot")

with QuoteLoader() as loader, QuoteBot(token, loader) as bot:

    LoadScheduler(60, loader, bot.run).start()
    logging.info("Scheduler started")

    bot.listen()
    logging.info("Bot terminated")
