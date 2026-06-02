import os
import requests
import asyncio
from telegram import Bot
from datetime import datetime
import pytz

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("AVIATIONSTACK_KEY")
CHAT_ID = "1026439077"

bot = Bot(token=BOT_TOKEN)
tz = pytz.timezone("America/Santo_Domingo")

def get_flights(dep, arr):
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&dep_iata={dep}&arr_iata={arr}"
    r = requests.get(url).json()

    flights = []

    for f in r.get("data", []):
        airline = f.get("airline", {}).get("name", "")

        if airline != "American Airlines":
            continue

        flight = f.get("flight", {}).get("iata", "N/A")
        status = f.get("flight_status", "N/A")

        etd = f.get("departure", {}).get("estimated", "N/A")
        eta = f.get("arrival", {}).get("estimated", "N/A")

        aircraft = f.get("aircraft", {}).get("registration", "N/A")

        flights.append(
            f"""✈️ {flight}
Route: {dep} → {arr}
Status: {status}

ETD: {etd}
ETA: {eta}

Aircraft: {aircraft}
"""
        )

    return flights

async def main():

    now = datetime.now(tz).strftime("%d-%b-%Y %I:%M %p AST")

    msg = f"📅 {now}\n\n🇺🇸 AMERICAN AIRLINES STATUS\n\n"

    msg += "\n".join(get_flights("MIA","SDQ"))
    msg += "\n"
    msg += "\n".join(get_flights("SDQ","MIA"))

    await bot.send_message(chat_id=CHAT_ID, text=msg[:4000])

asyncio.run(main())
