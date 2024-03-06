import feedparser
import csv
import schedule
import time

from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


TOKEN: Final = open('TOKEN', 'r').readline().strip()
BOT_USERNAME: Final = open('BOT_USERNAME', 'r').readline().strip()

quotes_feed=[]


def fetch_and_save():
    print("fetch_and_save()")
    global quotes_feed
    quotes_feed = fetch_quotes_from_rss()
    # save_quotes_to_csv(quotes_feed)


def fetch_quotes_from_rss():
    url = 'https://www.brainyquote.com/link/quotebr.rss'
    feed = feedparser.parse(url)

    quote_dict = []
    for entry in feed.entries:
        quote_dict.append({
            "title": entry.title,
            "link": entry.link,
            "summary": entry.summary,
        })

    return quote_dict


# def save_quotes_to_csv(feed):
#     print(feed)
#     with open('rss_data.csv', mode='w', newline='', encoding='utf-8') as csv_file:
#         fieldnames = ['title', 'link', 'summary']
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
#         for entry in feed:
#             writer.writerow(entry)


# Telegram Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("start_command()")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("help_command")


async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("custom_command")


async def quote_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global quotes_feed
    if not quotes_feed:
        await update.message.reply_text("Quotes not available")
    else:
        quote_dict = quotes_feed.pop(0)
        quote = f"{quote_dict['title']}\n{quote_dict['summary']}\n{quote_dict['link']}"
        await update.message.reply_text(quote)


# Telegram Responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    return "I don't understand"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print("Bot: ", response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


schedule.every().day.at("05:00").do(fetch_and_save)

schedule.every().day.at("06:00").do(quote_command)
schedule.every().day.at("07:00").do(quote_command)
schedule.every().day.at("08:00").do(quote_command)
schedule.every().day.at("09:00").do(quote_command)


if __name__ == '__main__':
    print("Starting bot")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('quote', quote_command))
    print("All commands loaded")

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Quotes
    quotes_feed = fetch_quotes_from_rss()
    # save_quotes_to_csv(quotes_feed)
    print("Quotes loaded")

    # Polls the bot
    print("Polling...")
    app.run_polling(poll_interval=3)

    while True:
        schedule.run_pending()
        time.sleep(1)