import datetime
import logging
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

logger = logging.getLogger(__name__)

async def check_availability_for_date(date: str, user):
    url = f"https://alquilatucancha.com/api/v3/availability/sportclubs/678?date={date}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            availability_data = response.json()
            message_list = format_free_slots(availability_data)
            message = "\n".join(message_list)
            logger.info(f"{user.first_name} retrieved the info correctly")
        else:
            message = "Error fetching availability data."
            logger.warning(f"{user.first_name} couldn't retrieve the info")

    return message

def format_free_slots(availability_data):
    available_courts = availability_data.get("available_courts", [])
    message_list = ["Available slots:"]
    previous_slot = ""
    for court in available_courts:
        court_name = court.get("name", "Unknown court")
        message_list.append(f"\n{court_name}:")
        for slot in court.get("available_slots", []):
            if slot.get("start", "Unknown start time") == previous_slot:
                message = message_list.pop()
                message_list.append(f"{message}, {slot.get('duration', 0)} mins")
                continue
            start_time = slot.get("start", "Unknown start time")
            duration = slot.get("duration", 0)
            start_time_obj = datetime.fromisoformat(start_time)
            message_list.append(f"  - Start: {start_time_obj.strftime('%H:%M')}, Duration: {duration} mins")
            previous_slot = start_time
    return message_list