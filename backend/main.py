
import httpx
from pathlib import Path
from typing import Literal
import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agents import run_workflow, frontend_recommendation


# -------------------------
# PROJECT PATHS
# -------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DB_PATH = BASE_DIR / "backend" / "nxtwatt.db"


# -------------------------
# DEMO CHARGERS AND SLOTS
# -------------------------

BOOKING_CHARGERS = {
    1: {
        "name": "GreenNest Home Charger",
        "price": 12,
        "slots": ["6:00 PM", "7:00 PM", "8:30 PM"],
    },
    2: {
        "name": "Sunrise Society EV Point",
        "price": 15,
        "slots": ["5:30 PM", "7:30 PM", "9:00 PM"],
    },
    3: {
        "name": "ParkView Smart Socket",
        "price": 9,
        "slots": ["Tomorrow 8 AM", "Tomorrow 10 AM"],
    },
    4: {
        "name": "HarbourCharge Home",
        "price": 13,
        "slots": ["6:30 PM", "8:00 PM"],
    },
    5: {
        "name": "EcoLane Charging",
        "price": 20,
        "slots": ["7:00 PM", "8:00 PM", "9:30 PM"],
    },
}


# -------------------------
# DATABASE
# -------------------------

def get_db():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_booking_database():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                charger_id INTEGER NOT NULL,
                charger_name TEXT NOT NULL,
                slot TEXT NOT NULL,
                energy_kwh REAL NOT NULL,
                total_cost REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                created_at TEXT NOT NULL,
                UNIQUE(charger_id, slot)
            )
        """)


initialize_booking_database()


# -------------------------
# FASTAPI APP
# -------------------------

app = FastAPI(
    title="NXTWATT API",
    description="Community-powered EV charging prototype with Gemma AI",
    version="1.1.0",
)

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


# -------------------------
# REQUEST MODELS
# -------------------------

class DriverRequest(BaseModel):
    battery_percent: int = Field(ge=1, le=100)
    remaining_range_km: int = Field(ge=1, le=500)
    needed_kwh: int = Field(ge=1, le=40)
    connector: Literal["Type 2", "CCS2", "GB/T", "Not sure"]


class FrontendRecommendationRequest(BaseModel):
    priority: Literal[
        "balanced", "price", "speed", "green", "distance"
    ] = "balanced"
    budget: float = Field(default=16, ge=0, le=1000)


class BookingRequest(BaseModel):
    charger_id: int = Field(ge=1, le=5)
    slot: str
    energy_kwh: float = Field(gt=0, le=40)


class GemmaChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


# -------------------------
# WEBSITE AND HEALTH CHECK
# -------------------------

@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "NXTWATT backend is running",
    }


# -------------------------
# EXISTING AI WORKFLOW
# -------------------------

@app.post("/recommend")
def recommend(request: DriverRequest):
    return run_workflow(
        battery=request.battery_percent,
        range_km=request.remaining_range_km,
        energy_kwh=request.needed_kwh,
        connector=request.connector,
    )


@app.post("/api/recommend")
def recommend_for_frontend(
    request: FrontendRecommendationRequest,
):
    return frontend_recommendation(
        priority=request.priority,
        budget=request.budget,
    )


# -------------------------
# CHECK AVAILABLE BOOKING SLOTS
# -------------------------

@app.get("/api/bookings/slots/{charger_id}")
def get_booking_slots(charger_id: int):
    charger = BOOKING_CHARGERS.get(charger_id)

    if not charger:
        raise HTTPException(
            status_code=404,
            detail="Charger not found",
        )

    with get_db() as connection:
        rows = connection.execute(
            """
            SELECT slot
            FROM bookings
            WHERE charger_id = ?
              AND status = 'confirmed'
            """,
            (charger_id,),
        ).fetchall()

    booked_slots = {row["slot"] for row in rows}

    available_slots = [
        slot for slot in charger["slots"]
        if slot not in booked_slots
    ]

    return {
        "charger_id": charger_id,
        "charger_name": charger["name"],
        "available_slots": available_slots,
        "booked_slots": sorted(booked_slots),
    }


# -------------------------
# CREATE A BOOKING
# -------------------------

@app.post("/api/bookings", status_code=201)
def create_booking(request: BookingRequest):
    charger = BOOKING_CHARGERS.get(request.charger_id)

    if not charger:
        raise HTTPException(
            status_code=404,
            detail="Charger not found",
        )

    if request.slot not in charger["slots"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid charging slot",
        )

    total_cost = round(
        request.energy_kwh * charger["price"], 2
    )

    try:
        with get_db() as connection:
            connection.execute("BEGIN IMMEDIATE")

            cursor = connection.execute(
                """
                INSERT INTO bookings (
                    charger_id,
                    charger_name,
                    slot,
                    energy_kwh,
                    total_cost,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, 'confirmed', ?)
                """,
                (
                    request.charger_id,
                    charger["name"],
                    request.slot,
                    request.energy_kwh,
                    total_cost,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            booking_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=(
                "This slot has already been booked. "
                "Please choose another slot."
            ),
        )

    return {
        "success": True,
        "booking_id": booking_id,
        "charger_name": charger["name"],
        "slot": request.slot,
        "energy_kwh": request.energy_kwh,
        "total_cost": total_cost,
        "status": "confirmed",
        "message": "Demo booking saved successfully.",
    }


# -------------------------
# GEMMA AI CHAT ENDPOINT
# -------------------------

@app.post("/api/gemma")
async def gemma_chat(request: GemmaChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty",
        )

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://127.0.0.1:11434/api/chat",
                json={
                    "model": "gemma3:1b",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are NXTWATT AI, an assistant for an "
                                "EV charging platform. Give concise, useful "
                                "answers about EV charging, affordability, "
                                "energy use, and sustainability. You may "
                                "explain how to choose a charger, but do not "
                                "invent live prices, availability, or bookings. "
                                "Only describe data actually provided to you."
                            ),
                        },
                        {
                            "role": "user",
                            "content": message,
                        },
                    ],
                    "stream": False,
                },
            )

        response.raise_for_status()
        data = response.json()

        return {
            "success": True,
            "reply": data["message"]["content"],
            "model": "gemma3:1b",
        }

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Gemma took too long to respond. Please try again.",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Make sure Ollama is running.",
        )
    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Ollama returned an error. Check that gemma3:1b is installed.",
        )
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=502,
            detail="Unexpected response received from Ollama.",
        )
