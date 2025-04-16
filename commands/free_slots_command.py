import datetime
import logging
import locale
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, constants, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from utils.venues_util import check_availability_for_date

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(f"{user.first_name} with id {user.id} started a conversation")

    # Generate the reply keyboard with weekdays
    today = datetime.today()
    keyboard_options =   [
                    f"{(today + timedelta(days=i)).strftime('%d/%m')} ({(today + timedelta(days=i)).strftime('%A').capitalize()})" 
                    for i in range(1, 8)
                ]    
    
    reply_keyboard = [
            keyboard_options[0:3],
            keyboard_options[3:6],
            keyboard_options[6:7],
    ]

    await update.message.reply_text(
        "Qué hace mostro? Acá respetamos a los jugadores de padel y no hacemos memes de ellos. "
        "Podes escribir /cancel si se te resbaló el dedo.\n\n"
        "Para qué fecha (dd/mm) queres que te diga los turnos disponibles?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="dd/mm",
        ),
    )

    return CHECKAVAILABILITY


CHECKAVAILABILITY = range(1)

async def check_availability(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    
    try:
        date_string = f"{update.message.text.split(' ')[0]}/{datetime.today().year}"
        date_object = datetime.strptime(date_string, "%d/%m/%Y")  
    except:
        await update.message.reply_text("Te crees piola? Ingresá bien la fecha, payaso.", reply_markup=ReplyKeyboardRemove())
        return CHECKAVAILABILITY

    formatted_date = date_object.strftime("%Y-%m-%d")
    message = await check_availability_for_date(formatted_date, user)

    await update.message.reply_text(f"{message}", reply_markup=ReplyKeyboardRemove(), parse_mode=constants.ParseMode.HTML)
    logger.info(f"{user.first_name} finished the conversation")
    return ConversationHandler.END