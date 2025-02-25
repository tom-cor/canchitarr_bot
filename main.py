import datetime
import json
import logging
from typing import Final
import httpx
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

#region Config file loading

secrets_filename = 'secrets.json'
secrets = {}
with open(secrets_filename, 'r') as file:
    secrets = json.loads(file.read())
TOKEN: Final = secrets["TELEGRAM_BOT_TOKEN"]
del secrets

#endregion




CHECKAVAILABILITY = range(1)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["27/02", "28/02", "29/02"]]

    await update.message.reply_text(
        "Qué hace mostro? Sacate el plug de la cola y prestame atención. "
        "Podes escribir /cancel si te hinchaste los huevos.\n\n"
        "Para qué fecha (dd/mm) queres que te diga los turnos disponibles?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="dd/mm"
        ),
    )

    return CHECKAVAILABILITY


async def check_availability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    try:
        date_string = f"{update.message.text}/{datetime.today().year}"
        date_object = datetime.strptime(date_string, "%d/%m/%Y")  
    except:
        await update.message.reply_text("Te crees piola? Ingresá bien la fecha, payaso.", reply_markup=ReplyKeyboardRemove())
        return CHECKAVAILABILITY

    formatted_date = date_object.strftime("%Y-%m-%d")
    url = f"https://alquilatucancha.com/api/v3/availability/sportclubs/678?date={formatted_date}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            availability_data = response.json()
            message_list = retrieve_free_slots(availability_data)
            message = "\n".join(message_list)
        else:
            message = "Error fetching availability data."

    await update.message.reply_text(f"{message}", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def retrieve_free_slots(availability_data):
    available_courts = availability_data.get("available_courts", [])
    message_list = ["Available slots:"]
    for court in available_courts:
        court_name = court.get("name", "Unknown court")
        message_list.append(f"\n{court_name}:")
        for slot in court.get("available_slots", []):
            start_time = slot.get("start", "Unknown start time")
            duration = slot.get("duration", 0)
            start_time_obj = datetime.fromisoformat(start_time)
            message_list.append(f"  - Start: {start_time_obj.strftime('%H:%M')}, Duration: {duration} mins")
    return message_list

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Conversación finalizada.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


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