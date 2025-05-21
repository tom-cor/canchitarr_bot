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

async def check_availability_for_date(date: str, user, court_ids=None):
    if court_ids is None:
        court_ids = {"Cabildo Club": 678,
                     "Bequin": 397}  # Default to the original court if not provided

    message_list = []
    async with httpx.AsyncClient() as client:
        for club_name, club_id in court_ids.items():
            url = f"https://alquilatucancha.com/api/v3/availability/sportclubs/{club_id}?date={date}"
            response = await client.get(url)
            if response.status_code == 200:
                availability_data = response.json()
                message_list.extend(format_free_slots(availability_data))
                logger.info(f"{user.first_name} retrieved info for club id: {club_id} correctly")
            else:
                message_list.append(f"Error fetching availability data for club id:{club_id}.")
                logger.warning(f"{user.first_name} couldn't retrieve info for club id:{club_id}")

    return message_list

def format_free_slots(availability_data):
    available_courts = availability_data.get("available_courts", [])
    club_name = availability_data.get("name", "Unknown Club")
    message_list = []
    previous_slot = ""
    for court in available_courts:
        court_id = court.get("id", "Unknown court ID")
        court_name = court.get("name", "Unknown court")
        is_roofed = "🏠" if court.get("is_roofed", False) else "☔"
        is_beelup = "🎦✅" if court.get("is_beelup", False) else "🎦❌"
        has_lighting = "💡✅" if court.get("has_lighting", False) else "💡❌"
        message = [f"{club_name} - {court_name}: {is_roofed}, {is_beelup}, {has_lighting}\n"]
        for index, slot in enumerate(court.get("available_slots", []), start=1):
            duration = slot.get("duration", 0)
            if duration <= 60:
                continue  # Skip 60 min slots
            if slot.get("start", "Unknown start time") == previous_slot:
                msg = message.pop()
                message.append(f"{msg}, {get_slot_duration(slot, previous_slot, court_id, is_beelup)}")
                continue
            start_time = slot.get("start", "Unknown start time")
            logger.info(f"Slot #{index}: Start time: {start_time}, Duration: {duration}")
            duration_link = get_slot_duration(slot, start_time, court_id, is_beelup)
            start_time_obj = datetime.fromisoformat(start_time)
            message.append(f"\n- {start_time_obj.strftime('%H:%M')}, turnos: {duration_link}")
            previous_slot = start_time
        message_list.append("".join(message))
    if not message_list:
        message_list.append(f"No hay turnos disponibles para {club_name} en la fecha seleccionada")
    return message_list

def get_slot_duration(slot, start_time, court_id, is_beelup):
    duration = slot.get("duration", 0)
    date_only = start_time.split("T")[0]
    start_hour = start_time.split("T")[1].split("-")[0].split(":")[0]
    start_minutes = start_time.split("T")[1].split("-")[0].split(":")[1]

    if str(start_minutes) != "00":
        start_hour += "%3A30"
    else:
        start_hour += "%3A00"

    link = f'https://atcsports.io/checkout/678?day={date_only}&court={court_id}&sport_id=7&duration={duration}&start={start_hour}&end=&is_beelup={is_beelup}'

    return f'<a href="{link}">{duration} mins</a>'