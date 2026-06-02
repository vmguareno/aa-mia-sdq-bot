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

STATUS_MAP={
    "SCHEDULED":"SCHD",
    "ACTIVE":"ACTV",
    "LANDED":"LND",
    "DELAYED":"DLYD",
    "CANCELLED":"CNCL"
}


def convert(t):

    if not t:
        return None

    try:
        utc=datetime.fromisoformat(
            t.replace("Z","+00:00")
        )

        return utc.astimezone(tz)

    except:
        return None


def fmt(dt):

    if not dt:
        return "----"

    return dt.strftime("%H%M")


def get_flights(dep,arr):

    url=f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&dep_iata={dep}&arr_iata={arr}"

    r=requests.get(url).json()

    flights=[]
    seen=set()

    for f in r.get("data",[]):

        airline=f.get(
            "airline",{}
        ).get("name","")

        if airline!="American Airlines":
            continue

        flight=f.get(
            "flight",{}
        ).get("iata","AA---"
        )

        if flight in seen:
            continue

        seen.add(flight)

        status=STATUS_MAP.get(
            f.get(
                "flight_status",
                "UNKNOWN"
            ).upper(),
            "UNKN"
        )

        std=convert(
            f.get("departure",{})
            .get("scheduled")
        )

        etd=convert(
            f.get("departure",{})
            .get("estimated")
        )

        sta=convert(
            f.get("arrival",{})
            .get("scheduled")
        )

        eta=convert(
            f.get("arrival",{})
            .get("estimated")
        )

        if status=="LND":

            row=f"""
{flight:<7}{status}
OUT{fmt(etd)} IN{fmt(eta)}
"""

        elif status=="ACTV":

            row=f"""
{flight:<7}{status}
OUT{fmt(etd)} ETA{fmt(eta)}
"""

        else:

            row=f"""
{flight:<7}{status}
STD{fmt(std)} ETD{fmt(etd)}
STA{fmt(sta)} ETA{fmt(eta)}
"""

        flights.append(row)

    return "".join(flights)


async def main():

    now=datetime.now(tz)

    hdr=now.strftime(
        "%d%b%y/%H%MAST"
    ).upper()

    msg=f"""{hdr}   RGGSDQ AA OPS

ARR MIA-SDQ
────────────────────
"""

    msg += get_flights(
        "MIA",
        "SDQ"
    )

    msg += """

────────────────────
DEP SDQ-MIA
────────────────────
"""

    msg += get_flights(
        "SDQ",
        "MIA"
    )

    msg += f"""

LAST UPDATE {now.strftime("%H%MAST")}
"""

    await bot.send_message(
        chat_id=CHAT_ID,
        text=msg[:4000]
    )


while True:

    asyncio.run(main())

    time.sleep(600)
