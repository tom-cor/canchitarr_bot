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
        for index, slot in enumerate(court.get("available_slots", []), start=1):
            if slot.get("start", "Unknown start time") == previous_slot:
                message = message_list.pop()
                message_list.append(f"{message}, {get_slot_duration(slot, previous_slot, court_name)}")
                continue
            start_time = slot.get("start", "Unknown start time")
            duration = slot.get("duration", 0)
            logger.info(f"Slot #{index}: Start time: {start_time}, Duration: {duration}")
            duration_link = get_slot_duration(slot, start_time, court_name)
            start_time_obj = datetime.fromisoformat(start_time)
            message_list.append(f"  - Start: {start_time_obj.strftime('%H:%M')}, Duration: {duration_link}")
            previous_slot = start_time
    return message_list

def get_slot_duration(slot, start_time, court_name):
    duration = slot.get("duration", 0)
    date_only = start_time.split("T")[0]
    start_hour = start_time.split("T")[1].split("-")[0].split(":")[0]
    start_minutes = start_time.split("T")[1].split("-")[0].split(":")[1]

    if str(start_minutes) != "00":
        start_hour += "%3A30"
    else:
        start_hour += "%3A00"
    court_id = get_court_id(court_name)
    beelup_available = get_beelup_available(court_name)

    link = f'https://atcsports.io/checkout/678?day={date_only}&court={court_id}&sport_id=7&duration={duration}&start={start_hour}&end=&is_beelup={beelup_available}'

    return f'<a href="{link}">{duration} mins</a>'

def get_court_id(court_name):
    court_id = 0
    if court_name == "Cancha 1 Techada":
        court_id = 2194
    elif court_name == "Cancha 2 Descubierta":
        court_id = 2195
   
    return court_id

def get_beelup_available(court_name):
    beelup_available = 'false'
    if court_name == "Cancha 1 Techada":
        beelup_available = 'true'
    return beelup_available
