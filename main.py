import os
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Final

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from commands.free_slots_command import *
from commands.cancel_command import *

# Ensure the logs directory exists
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Enable logging
logging.basicConfig(
    level=logging.INFO,  # Set the base logging level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create a timed rotating file handler for monthly log rotation
file_handler = TimedRotatingFileHandler(
    os.path.join(logs_dir, "bot.log"), when="S", interval=30, backupCount=0
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))

# Get the root logger and add the file handler
logger = logging.getLogger()
logger.addHandler(file_handler)

# Suppress overly verbose logs from external libraries (like httpx)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Example usage
logger.info("Logging setup complete. Bot is starting...")

#region Config file loading

secrets_filename = 'secrets.json'
secrets = {}
with open(secrets_filename, 'r') as file:
    secrets = json.loads(file.read())
TOKEN: Final = secrets["TELEGRAM_BOT_TOKEN"]
del secrets

#endregion


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHECKAVAILABILITY: [MessageHandler(filters.Regex("^\d\d/\d\d$"), check_availability)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()