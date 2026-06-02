import os
import requests
import asyncio
import time
from telegram import Bot
from datetime import datetime
from zoneinfo import ZoneInfo

BOT_TOKEN=os.getenv("BOT_TOKEN")
API_KEY=os.getenv("AVIATIONSTACK_KEY")
CHAT_ID="1026439077"

bot=Bot(token=BOT_TOKEN)

tz=ZoneInfo("America/Santo_Domingo")


def convert_time(t):

    if not t:
        return None

    try:

        utc=datetime.fromisoformat(
            t.replace("Z","+00:00")
        )

        rd=utc.astimezone(tz)

        return rd

    except:
        return None


def fmt(dt):

    if not dt:
        return "N/A"

    return dt.strftime("%I:%M %p AST")


def delay_text(std,etd):

    if not std or not etd:
        return ""

    diff=int(
        (etd-std).total_seconds()/60
    )

    if diff > 5:
        return f"\n🔴 Delay: +{diff} min"

    elif diff < -5:
        return f"\n🟢 Early: {diff} min"

    return ""


def get_flights(dep,arr):

    url=f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&dep_iata={dep}&arr_iata={arr}"

    r=requests.get(url).json()

    flights=[]

    seen=set()

    counts={
        "SCHEDULED":0,
        "ACTIVE":0,
        "LANDED":0,
        "DELAYED":0,
        "CANCELLED":0
    }

    for f in r.get("data",[]):

        airline=f.get(
            "airline",{}
        ).get("name","")

        if airline!="American Airlines":
            continue

        flight=f.get(
            "flight",{}
        ).get("iata","N/A")

        status=f.get(
            "flight_status",
            "UNKNOWN"
        ).upper()

        if flight in seen:
            continue

        seen.add(flight)

        if status in counts:
            counts[status]+=1

        icons={
            "SCHEDULED":"🟢 SCHEDULED",
            "ACTIVE":"🟡 ACTIVE",
            "LANDED":"✅ LANDED",
            "DELAYED":"🔴 DELAYED",
            "CANCELLED":"❌ CANCELLED"
        }

        status_display=icons.get(
            status,status
        )

        std=convert_time(
            f.get("departure",{})
            .get("scheduled")
        )

        etd=convert_time(
            f.get("departure",{})
            .get("estimated")
        )

        sta=convert_time(
            f.get("arrival",{})
            .get("scheduled")
        )

        eta=convert_time(
            f.get("arrival",{})
            .get("estimated")
        )

        aircraft=(
            f.get("aircraft",{})
            .get("registration")
        )

        msg=f"""
✈️ {flight} | {status_display}

STD {fmt(std)}
ETD {fmt(etd)}

STA {fmt(sta)}
ETA {fmt(eta)}
"""

        msg += delay_text(
            std,
            etd
        )

        if aircraft:
            msg += (
                f"\nAircraft: {aircraft}"
            )

        flights.append(msg)

    return flights,counts


async def main():

    now=datetime.now(
        tz
    ).strftime(
        "%d-%b-%Y | %I:%M %p AST"
    )

    mia,mc=get_flights(
        "MIA",
        "SDQ"
    )

    sdq,sc=get_flights(
        "SDQ",
        "MIA"
    )

    msg=f"""📅 {now}

🇺🇸 AMERICAN AIRLINES — LIVE STATUS

🛬 MIA→SDQ
🟢 Scheduled: {mc['SCHEDULED']}
🟡 Active: {mc['ACTIVE']}
✅ Landed: {mc['LANDED']}
🔴 Delayed: {mc['DELAYED']}

🛫 SDQ→MIA
🟢 Scheduled: {sc['SCHEDULED']}
🟡 Active: {sc['ACTIVE']}
✅ Landed: {sc['LANDED']}
🔴 Delayed: {sc['DELAYED']}

━━━━━━━━━━━━━━
🛬 MIA → SDQ
━━━━━━━━━━━━━━
"""

    msg+="\n".join(mia)

    msg += """

━━━━━━━━━━━━━━
🛫 SDQ → MIA
━━━━━━━━━━━━━━
"""

    msg+="\n".join(sdq)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=msg[:4000]
    )


while True:

    asyncio.run(main())

    time.sleep(600)
