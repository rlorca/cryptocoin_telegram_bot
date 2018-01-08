import logging

from ctb.quote import CoinSymbol

logging.getLogger(__name__).addHandler(logging.NullHandler())

class Subscribers:
    """
    Class that keep track of coin subscriptions.
    """

    def __init__(self):
        self._subscribers = {}
        self.empty = frozenset()

    def add(self, symbol: CoinSymbol, user_id: str):

        symbol_sub = self._subscribers.get(symbol, None)

        # creates a new set of subscribers
        if not symbol_sub:
            symbol_sub = set()
            self._subscribers[symbol] = symbol_sub

        symbol_sub.add(user_id)

    def remove(self, symbol: CoinSymbol, user_id: str):

        symbol_sub = self._subscribers.get(symbol, self.empty)

        if user_id in symbol_sub:
            symbol_sub.discard(user_id)
            return True

    def for_symbol(self, symbol: CoinSymbol):
        yield from self._subscribers.get(symbol, self.empty)


class QuoteBot:
    """
    Class responsible for communication with Telegram.
    """

    def __init__(self, token, quote_service):
        self.quote_service = quote_service
        self.updater = Updater(token=token)
        self.subscriptions = Subscribers()

    def __enter__(self):
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler("follow", self.command_follow, pass_args=True))
        dp.add_handler(CommandHandler("unfollow", self.command_unfollow, pass_args=True))
        dp.add_handler(CommandHandler("quote", self.command_quote, pass_args=True))
        dp.add_handler(CommandHandler("help", self.command_help))
        dp.add_handler(CommandHandler("list", self.command_list_coins))

        dp.add_error_handler(self.error)

        # schedule quote update
        self.updater.job_queue.run_repeating(self.scheduler_callback, 60)

        self.updater.start_polling()

        logging.info("Started telegram polling")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.updater.stop()
        logging.info("Telegram terminated")

    def scheduler_callback(self, _bot, _queue):
        """
        Called by the scheduler at fixed intervals to retrieve new quotes.
        """

        # retrieve all quotes that were updated
        for q in self.quote_service.updated_quotes():
            msg = self.format_quote(q)

            # notify all chats subscribed
            for chat in self.subscriptions.for_symbol(q.symbol):
                self.updater.bot.send_message(chat_id=chat, text=msg)

    def listen(self):
        self.updater.idle()

    def command_quote(self, _, update, args):

        if len(args) != 1:
            update.message.reply_text("Wrong command format. Usage\n/quote $symbol")
            return

        symbol = CoinSymbol(args[0])
        quote = self.quote_service.latest_quote(symbol)
        msg = self.format_quote(quote) if quote else f"Coin '{symbol}' not found"
        update.message.reply_text(msg)

    def command_follow(self, bot, update, args):

        if len(args) != 1:
            update.message.reply_text("Wrong command format. Usage\n/follow $symbol")
            return

        symbol = CoinSymbol(args[0])
        chat_id = update.effective_chat.id

        logging.debug("User %s from chat %s is now following %s",
                      update.effective_user.id,
                      update.effective_chat.id,
                      symbol)

        quote = self.quote_service.latest_quote(symbol)

        if quote:
            self.subscriptions.add(symbol, chat_id)

            msg = f"You are now receiving updates for {symbol} - {quote.name}\n" + self.format_quote(quote)
        else:
            msg = f"Coin {symbol} unknown"

        update.message.reply_text(msg)

    def command_unfollow(self, _, update, args):

        if len(args) != 1:
            update.message.reply_text("Wrong command format. Usage\n/follow $symbol")
            return

        symbol = CoinSymbol(args[0])
        chat_id = update.effective_chat.id

        if self.subscriptions.remove(symbol, chat_id):
            msg = f"You are not following {symbol} anymore!"
        else:
            msg = f"You were not following {symbol}"

        update.message.reply_text(msg)

    def command_list_coins(self, _, update):

        coins = self.quote_service.coins_available()

        msg = f"Coins available: {len(coins)}\n" + "\n".join(str(c) for c in self.quote_service.coins_available())
        update.message.reply_text(msg)


    @staticmethod
    def command_help(_, update):

        msg = "This bot provides quotes of crypto currencies \n" \
              "/follow SYMBOL - receives updates whenever there's a new quote for the coin\n" \
              "/unfollow SYMBOL - stops receiving quotes for that coin\n" \
              "/quote SYMBOL - gets current quote for the coin\n" \
              "/list - list all symbols available"

        update.message.reply_text(msg)

    @staticmethod
    def error(bot, update, error):
        logging.error("Error detected in chat: %s", error)

    @staticmethod
    def format_quote(quote):

        return f"{quote.symbol}: " \
               f"$ {quote.price_usd} " \
               f"1h:{quote.percent_change_1h}% " \
               f"24h:{quote.percent_change_24h}%"
