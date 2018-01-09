"""
Cryptocoin telegram bot
"""
import logging
import os

from ctb.bot import QuoteBot
from ctb.quote import QuoteService

logging.getLogger(__name__).addHandler(logging.NullHandler())

TOKEN = os.environ['TELEGRAM_TOKEN']

logging.info("Starting bot")

service = QuoteService()
for q in service.updated_quotes():
    logging.debug("Initializing %s", q.symbol)

with QuoteBot(TOKEN, service) as bot:

    logging.info("Bot service started")
    bot.listen()
    logging.info("Bot terminated")
