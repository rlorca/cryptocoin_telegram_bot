import logging

from telegram.ext import CommandHandler, Updater

logging.getLogger(__name__).addHandler(logging.NullHandler())

class Subscribers:

    def __init__(self):
        self._subscribers = {}
        self.empty = frozenset()

    def add(self, symbol, user_id):

        symbol_sub = self._subscribers.get(symbol, None)

        if not symbol_sub:
            symbol_sub = set()
            self._subscribers[symbol] = symbol_sub

        symbol_sub.add(user_id)

    def for_symbol(self, symbol):

        return self._subscribers.get(symbol, self.empty)

    def remove(self, symbol, user_id):

        symbol_sub = self._subscribers.get(symbol, None)

        if symbol_sub and id in symbol_sub:
            symbol_sub.remove(user_id)
            return True

class QuoteBot:

    def __init__(self, token, loader):
        self.loader = loader
        self.updater = Updater(token=token)
        self.subscriptions = Subscribers()

    def __enter__(self):
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("follow", self.follow, pass_args=True))
        dp.add_handler(CommandHandler("unfollow", self.unfollow, pass_args=True))
        dp.add_handler(CommandHandler("quote", self.quote, pass_args=True))
        dp.add_handler(CommandHandler("help", self.help))

        dp.
        dp.add_error_handler(self.error)

        self.updater.start_polling()

        logging.info("Started telegram polling")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.updater.stop()
        logging.info("Telegram terminated")

    def listen(self):
        self.updater.idle()

    def follow(self, bot, update, args):

        symbol = args[0].upper()
        chat_id = update.effective_chat.id

        logging.debug("User %s from chat %s is now following %s",
                      update.effective_user.id,
                      update.effective_chat.id,
                      symbol)

        quote = self.loader.latest(symbol)

        if quote:
            self.subscriptions.add(symbol, chat_id)

            msg = f"You are now receiving updates for {symbol} - {quote.name}\n" + self.format_quote(quote)
        else:
            msg = f"Coin {symbol} unknown"

        update.message.reply_text(msg)

    def quote(self, _, update, args):

        symbol = args[0]
        quote = self.loader.latest(symbol)
        msg = self.format_quote(quote) if quote else f"Coin '{symbol}' not found"
        update.message.reply_text(msg)

    def unfollow(self, _, update, args):

        symbol = args[0]
        chat_id = update.effective_chat.id

        if self.subscriptions.remove(symbol, chat_id):
            msg = f"You are not following {symbol} anymore!"
        else:
            msg = f"You were not following {symbol}"

        update.message.reply_text(msg)

    @staticmethod
    def help( _, update):

        msg = "This bot provides quotes of crypto currencies \n" \
              "/follow SYMBOL - receives updates whenever there's a new quote for the coin\n" \
              "/unfollow SYMBOL - stops receiving quotes for that coin\n" \
              "/quote SYMBOL - gets current quote for the coin"

        update.message.reply_text(msg)

    @staticmethod
    def error(update, error):
        logging.error("Error detected in chat %d: %s", update.effective_chat.id, error)

    @staticmethod
    def format_quote(quote):

        return f"{quote.symbol}: " \
               f"$ {quote.price_usd} " \
               f"1h:{quote.percent_change_1h}% " \
               f"24h:{quote.percent_change_24h}%"

    def run(self, quote):

        msg = self.format_quote(quote)

        for chat in self.subscriptions.for_symbol(quote.symbol):
            self.updater.bot.send_message(chat_id=chat, text=msg)