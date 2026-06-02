import os
import requests
import asyncio
import time
from telegram import Bot
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("AVIATIONSTACK_KEY")
CHAT_ID = "1026439077"

bot = Bot(token=BOT_TOKEN)

tz = ZoneInfo("America/Santo_Domingo")


def convert_time(t):

    if not t:
        return "N/A"

    try:
        utc = datetime.fromisoformat(t.replace("Z","+00:00"))
        rd = utc.astimezone(tz)

        return rd.strftime("%I:%M %p AST")

    except:
        return "N/A"


def get_flights(dep, arr):

    url=f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&dep_iata={dep}&arr_iata={arr}"

    r=requests.get(url).json()

    flights=[]

    for f in r.get("data", []):

        airline=f.get("airline",{}).get("name","")

        if airline != "American Airlines":
            continue

        flight=f.get("flight",{}).get("iata","N/A")

        status=f.get("flight_status","UNKNOWN").upper()

        icons={
            "SCHEDULED":"🟢 SCHEDULED",
            "ACTIVE":"🟡 ACTIVE",
            "LANDED":"✅ LANDED",
            "DELAYED":"🔴 DELAYED",
            "CANCELLED":"❌ CANCELLED"
        }

        status_display=icons.get(status,status)

        std=convert_time(
            f.get("departure",{}).get("scheduled")
        )

        etd=convert_time(
            f.get("departure",{}).get("estimated")
        )

        sta=convert_time(
            f.get("arrival",{}).get("scheduled")
        )

        eta=convert_time(
            f.get("arrival",{}).get("estimated")
        )

        aircraft=(
            f.get("aircraft",{})
            .get("registration")
        )

        msg=f"""
✈️ {flight}
{status_display}

STD: {std}
ETD: {etd}

STA: {sta}
ETA: {eta}
"""

        if aircraft:
            msg += f"\nAircraft: {aircraft}"

        flights.append(msg)

    return flights


async def main():

    now=datetime.now(tz).strftime(
        "%d-%b-%Y | %I:%M %p AST"
    )

    msg=f"""📅 {now}

🇺🇸 AMERICAN AIRLINES — LIVE STATUS

━━━━━━━━━━━━━━
🛬 MIA → SDQ
━━━━━━━━━━━━━━
"""

    msg+="\n".join(
        get_flights("MIA","SDQ")
    )

    msg += """

━━━━━━━━━━━━━━
🛫 SDQ → MIA
━━━━━━━━━━━━━━
"""

    msg+="\n".join(
        get_flights("SDQ","MIA")
    )

    await bot.send_message(
        chat_id=CHAT_ID,
        text=msg[:4000]
    )


while True:

    asyncio.run(main())

    time.sleep(600)
