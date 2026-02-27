import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

REPORTS_DIR = Path("reports")
PDFS_DIR = Path("pdfs")
PHOTOS_DIR = Path("photos")

(
    DATE_TIME,
    DRIVER_NAME,
    DRIVER_PHONE,
    COMPANY_NAME,
    TRUCK_UNIT,
    TRAILER_NUMBER,
    PLATE_NUMBER,
    LOCATION,
    CITY_STATE,
    ACCIDENT_TYPE,
    DESCRIPTION,
    INJURIES,
    INJURIES_NOTE,
    POLICE_CALLED,
    POLICE_REPORT,
    OTHER_NAME,
    OTHER_PHONE,
    OTHER_COMPANY,
    OTHER_PLATE,
    OTHER_INSURANCE,
    WITNESS,
    DAMAGE,
    PHOTOS,
) = range(23)

ACCIDENT_TYPES = [["rear-end", "backing"], ["lane change", "weather"], ["other"]]
YES_NO = [["Yes", "No"]]
DONE_KEYBOARD = [["done"]]


def ensure_directories() -> None:
    for directory in (REPORTS_DIR, PDFS_DIR, PHOTOS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def is_valid_phone(value: str) -> bool:
    return bool(re.fullmatch(r"[+\d][\d\-\s()]{6,}", value.strip()))


def empty_to_none(value: str) -> Optional[str]:
    cleaned = value.strip()
    if not cleaned or cleaned.lower() in {"n/a", "none", "no"}:
        return None
    return cleaned


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    context.user_data["photos"] = []
    await update.message.reply_text(
        "🚛 Accident Report Started.\n"
        "Please enter accident date & time in format YYYY-MM-DD HH:MM (or type 'now')."
    )
    return DATE_TIME


async def get_date_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    if text.lower() == "now":
        context.user_data["accident_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        try:
            parsed = datetime.strptime(text, "%Y-%m-%d %H:%M")
            context.user_data["accident_datetime"] = parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            await update.message.reply_text("Invalid format. Use YYYY-MM-DD HH:MM or 'now'.")
            return DATE_TIME

    await update.message.reply_text("Driver full name:")
    return DRIVER_NAME


async def get_driver_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["driver_name"] = update.message.text.strip()
    await update.message.reply_text("Driver phone number:")
    return DRIVER_PHONE


async def get_driver_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    phone = update.message.text.strip()
    if not is_valid_phone(phone):
        await update.message.reply_text("Please enter a valid phone number.")
        return DRIVER_PHONE

    context.user_data["driver_phone"] = phone
    await update.message.reply_text("Company name:")
    return COMPANY_NAME


async def get_company_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["company_name"] = update.message.text.strip()
    await update.message.reply_text("Truck/unit number:")
    return TRUCK_UNIT


async def get_truck_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["truck_unit_number"] = update.message.text.strip()
    await update.message.reply_text("Trailer number (optional, or type N/A):")
    return TRAILER_NUMBER


async def get_trailer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["trailer_number"] = empty_to_none(update.message.text)
    await update.message.reply_text("Plate number (optional, or type N/A):")
    return PLATE_NUMBER


async def get_plate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["plate_number"] = empty_to_none(update.message.text)
    await update.message.reply_text(
        "Send exact location. You can:\n"
        "1) Share Telegram location\n"
        "2) Type full address"
    )
    return LOCATION


async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.location:
        location = update.message.location
        context.user_data["location"] = {
            "type": "telegram_location",
            "latitude": location.latitude,
            "longitude": location.longitude,
        }
    elif update.message.text:
        context.user_data["location"] = {
            "type": "typed_address",
            "address": update.message.text.strip(),
        }
    else:
        await update.message.reply_text("Please share location or type an address.")
        return LOCATION

    await update.message.reply_text("City and State:")
    return CITY_STATE


async def get_city_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["city_state"] = update.message.text.strip()
    await update.message.reply_text(
        "Type of accident:",
        reply_markup=ReplyKeyboardMarkup(ACCIDENT_TYPES, one_time_keyboard=True, resize_keyboard=True),
    )
    return ACCIDENT_TYPE


async def get_accident_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    accident_type = update.message.text.strip().lower()
    valid = {"rear-end", "backing", "lane change", "weather", "other"}
    if accident_type not in valid:
        await update.message.reply_text("Choose one of the provided options.")
        return ACCIDENT_TYPE

    context.user_data["accident_type"] = accident_type
    await update.message.reply_text("Detailed description of what happened:", reply_markup=ReplyKeyboardRemove())
    return DESCRIPTION


async def get_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["description"] = update.message.text.strip()
    await update.message.reply_text(
        "Were there injuries?",
        reply_markup=ReplyKeyboardMarkup(YES_NO, one_time_keyboard=True, resize_keyboard=True),
    )
    return INJURIES


async def get_injuries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip().lower()
    if answer not in {"yes", "no"}:
        await update.message.reply_text("Please choose Yes or No.")
        return INJURIES

    context.user_data["injuries"] = answer == "yes"
    if context.user_data["injuries"]:
        await update.message.reply_text("Short injury note:")
        return INJURIES_NOTE

    context.user_data["injuries_note"] = None
    await update.message.reply_text(
        "Was police called?",
        reply_markup=ReplyKeyboardMarkup(YES_NO, one_time_keyboard=True, resize_keyboard=True),
    )
    return POLICE_CALLED


async def get_injuries_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["injuries_note"] = empty_to_none(update.message.text)
    await update.message.reply_text(
        "Was police called?",
        reply_markup=ReplyKeyboardMarkup(YES_NO, one_time_keyboard=True, resize_keyboard=True),
    )
    return POLICE_CALLED


async def get_police_called(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip().lower()
    if answer not in {"yes", "no"}:
        await update.message.reply_text("Please choose Yes or No.")
        return POLICE_CALLED

    context.user_data["police_called"] = answer == "yes"
    if context.user_data["police_called"]:
        await update.message.reply_text("Police report number:")
        return POLICE_REPORT

    context.user_data["police_report_number"] = None
    await update.message.reply_text("Other party name:", reply_markup=ReplyKeyboardRemove())
    return OTHER_NAME


async def get_police_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["police_report_number"] = empty_to_none(update.message.text)
    await update.message.reply_text("Other party name:", reply_markup=ReplyKeyboardRemove())
    return OTHER_NAME


async def get_other_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["other_party_name"] = empty_to_none(update.message.text)
    await update.message.reply_text("Other party phone:")
    return OTHER_PHONE


async def get_other_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["other_party_phone"] = empty_to_none(update.message.text)
    await update.message.reply_text("Other party company:")
    return OTHER_COMPANY


async def get_other_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["other_party_company"] = empty_to_none(update.message.text)
    await update.message.reply_text("Other party plate:")
    return OTHER_PLATE


async def get_other_plate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["other_party_plate"] = empty_to_none(update.message.text)
    await update.message.reply_text("Other party insurance:")
    return OTHER_INSURANCE


async def get_other_insurance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["other_party_insurance"] = empty_to_none(update.message.text)
    await update.message.reply_text("Witness information (optional, type N/A if none):")
    return WITNESS


async def get_witness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["witness_information"] = empty_to_none(update.message.text)
    await update.message.reply_text("Damage description:")
    return DAMAGE


async def get_damage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["damage_description"] = update.message.text.strip()
    await update.message.reply_text(
        "Upload accident photos (you can send multiple).\n"
        "When finished, type 'done'.",
        reply_markup=ReplyKeyboardMarkup(DONE_KEYBOARD, one_time_keyboard=False, resize_keyboard=True),
    )
    return PHOTOS


async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photos: List[str] = context.user_data.setdefault("photos", [])
    photo = update.message.photo[-1]
    file = await photo.get_file()

    report_temp_id = context.user_data.setdefault("temp_id", uuid4().hex[:8])
    photo_dir = PHOTOS_DIR / f"tmp_{report_temp_id}"
    photo_dir.mkdir(parents=True, exist_ok=True)

    filename = f"photo_{len(photos) + 1}_{uuid4().hex[:6]}.jpg"
    destination = photo_dir / filename
    await file.download_to_drive(custom_path=str(destination))

    photos.append(str(destination))
    await update.message.reply_text(f"Photo saved ({len(photos)}). Send more or type 'done'.")
    return PHOTOS


async def photos_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.strip().lower() != "done":
        await update.message.reply_text("Please upload a photo or type 'done'.")
        return PHOTOS

    try:
        report_id = generate_report_id(update.effective_user.id)
        report_payload = build_report_payload(context.user_data, report_id)

        json_path = REPORTS_DIR / f"{report_id}.json"
        pdf_path = PDFS_DIR / f"{report_id}.pdf"

        finalized_photos = move_photos_to_report_folder(report_payload["photos"], report_id)
        report_payload["photos"] = finalized_photos

        with json_path.open("w", encoding="utf-8") as file_obj:
            json.dump(report_payload, file_obj, ensure_ascii=False, indent=2)

        generate_pdf(report_payload, pdf_path)

        await notify_admin(context, report_payload, pdf_path)

        await update.message.reply_text(
            f"✅ Report submitted successfully.\nReport ID: {report_id}",
            reply_markup=ReplyKeyboardRemove(),
        )
    except Exception:
        logger.exception("Failed to finalize report")
        await update.message.reply_text(
            "❌ Failed to create the report due to an internal error. Please try again later.",
            reply_markup=ReplyKeyboardRemove(),
        )
    finally:
        context.user_data.clear()

    return ConversationHandler.END


def move_photos_to_report_folder(photo_paths: List[str], report_id: str) -> List[str]:
    if not photo_paths:
        return []

    report_photo_dir = PHOTOS_DIR / report_id
    report_photo_dir.mkdir(parents=True, exist_ok=True)

    finalized: List[str] = []
    for photo_path in photo_paths:
        source = Path(photo_path)
        if not source.exists():
            continue
        destination = report_photo_dir / source.name
        source.replace(destination)
        finalized.append(str(destination))

    parent = Path(photo_paths[0]).parent
    if parent.exists() and parent.name.startswith("tmp_"):
        try:
            parent.rmdir()
        except OSError:
            logger.debug("Temporary photo folder not empty: %s", parent)

    return finalized


def build_report_payload(data: Dict[str, Any], report_id: str) -> Dict[str, Any]:
    return {
        "report_id": report_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "accident_datetime": data.get("accident_datetime"),
        "driver": {
            "full_name": data.get("driver_name"),
            "phone": data.get("driver_phone"),
            "company_name": data.get("company_name"),
            "truck_unit_number": data.get("truck_unit_number"),
            "trailer_number": data.get("trailer_number"),
            "plate_number": data.get("plate_number"),
        },
        "location": {
            **(data.get("location") or {}),
            "city_state": data.get("city_state"),
        },
        "accident": {
            "type": data.get("accident_type"),
            "description": data.get("description"),
            "injuries": data.get("injuries"),
            "injuries_note": data.get("injuries_note"),
            "police_called": data.get("police_called"),
            "police_report_number": data.get("police_report_number"),
            "damage_description": data.get("damage_description"),
        },
        "other_party": {
            "name": data.get("other_party_name"),
            "phone": data.get("other_party_phone"),
            "company": data.get("other_party_company"),
            "plate": data.get("other_party_plate"),
            "insurance": data.get("other_party_insurance"),
        },
        "witness_information": data.get("witness_information"),
        "photos": data.get("photos", []),
    }


def generate_report_id(user_id: int) -> str:
    return f"AR-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{user_id}"


def draw_wrapped_text(pdf: canvas.Canvas, text: str, x: int, y: int, max_width: int, line_height: int = 14) -> int:
    words = (text or "").split()
    if not words:
        pdf.drawString(x, y, "-")
        return y - line_height

    line = ""
    for word in words:
        test = f"{line} {word}".strip()
        if pdf.stringWidth(test, "Helvetica", 10) <= max_width:
            line = test
        else:
            pdf.drawString(x, y, line)
            y -= line_height
            line = word
    if line:
        pdf.drawString(x, y, line)
        y -= line_height
    return y


def generate_pdf(report_data: Dict[str, Any], output_path: Path) -> None:
    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    y = height - 50

    pdf.setFont("Helvetica-Bold", 18)
    pdf.setFillColor(colors.darkblue)
    pdf.drawString(50, y, f"{report_data['driver']['company_name']} - Accident Report")
    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.black)
    pdf.drawString(50, y, f"Report ID: {report_data['report_id']}")
    y -= 16
    pdf.drawString(50, y, f"Generated: {report_data['created_at']}")
    y -= 24

    sections = [
        ("Accident Date/Time", report_data.get("accident_datetime")),
        ("Driver Name", report_data["driver"].get("full_name")),
        ("Driver Phone", report_data["driver"].get("phone")),
        ("Truck/Unit", report_data["driver"].get("truck_unit_number")),
        ("Trailer", report_data["driver"].get("trailer_number")),
        ("Plate", report_data["driver"].get("plate_number")),
        ("Location", json.dumps(report_data.get("location"), ensure_ascii=False)),
        ("Accident Type", report_data["accident"].get("type")),
        ("Description", report_data["accident"].get("description")),
        (
            "Injuries",
            f"{report_data['accident'].get('injuries')} | Note: {report_data['accident'].get('injuries_note')}",
        ),
        (
            "Police",
            f"Called: {report_data['accident'].get('police_called')} | Report #: {report_data['accident'].get('police_report_number')}",
        ),
        ("Other Party", json.dumps(report_data.get("other_party"), ensure_ascii=False)),
        ("Witness Info", report_data.get("witness_information")),
        ("Damage", report_data["accident"].get("damage_description")),
    ]

    for label, value in sections:
        if y < 90:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 10)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(50, y, f"{label}:")
        pdf.setFont("Helvetica", 10)
        y = draw_wrapped_text(pdf, str(value or "-"), 170, y, int(width - 220))
        y -= 4

    if report_data.get("photos"):
        pdf.showPage()
        y = height - 50
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "Accident Photos")
        y -= 25

        for index, photo_path in enumerate(report_data["photos"], start=1):
            path = Path(photo_path)
            if not path.exists():
                continue
            if y < 220:
                pdf.showPage()
                y = height - 50
            pdf.setFont("Helvetica", 10)
            pdf.drawString(50, y, f"Photo {index}: {path.name}")
            y -= 12

            try:
                image = ImageReader(str(path))
                img_width, img_height = image.getSize()
                max_width = width - 100
                max_height = 180
                scale = min(max_width / img_width, max_height / img_height)
                draw_w = img_width * scale
                draw_h = img_height * scale
                pdf.drawImage(image, 50, y - draw_h, width=draw_w, height=draw_h, preserveAspectRatio=True)
                y -= draw_h + 25
            except Exception:
                logger.exception("Failed to add photo %s to PDF", photo_path)

    pdf.save()


async def notify_admin(context: ContextTypes.DEFAULT_TYPE, report_data: Dict[str, Any], pdf_path: Path) -> None:
    if not ADMIN_CHAT_ID:
        logger.warning("ADMIN_CHAT_ID is not configured; skipping admin notification")
        return

    admin_chat_id = int(ADMIN_CHAT_ID)
    message = (
        "🚨 New Trucking Accident Report\n"
        f"Report ID: {report_data['report_id']}\n"
        f"Driver: {report_data['driver']['full_name']}\n"
        f"Company: {report_data['driver']['company_name']}\n"
        f"Type: {report_data['accident']['type']}\n"
        f"City/State: {report_data['location'].get('city_state')}"
    )

    await context.bot.send_message(chat_id=admin_chat_id, text=message)
    with pdf_path.open("rb") as pdf_file:
        await context.bot.send_document(chat_id=admin_chat_id, document=pdf_file, filename=pdf_path.name)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Report cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled exception while processing update", exc_info=context.error)


def build_application() -> Application:
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Add it to .env.")

    ensure_directories()
    app = Application.builder().token(BOT_TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("report", start)],
        states={
            DATE_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date_time)],
            DRIVER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_driver_name)],
            DRIVER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_driver_phone)],
            COMPANY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_company_name)],
            TRUCK_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_truck_unit)],
            TRAILER_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_trailer)],
            PLATE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_plate)],
            LOCATION: [
                MessageHandler(filters.LOCATION, get_location),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_location),
            ],
            CITY_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city_state)],
            ACCIDENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_accident_type)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            INJURIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_injuries)],
            INJURIES_NOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_injuries_note)],
            POLICE_CALLED: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_police_called)],
            POLICE_REPORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_police_report)],
            OTHER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other_name)],
            OTHER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other_phone)],
            OTHER_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other_company)],
            OTHER_PLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other_plate)],
            OTHER_INSURANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_other_insurance)],
            WITNESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_witness)],
            DAMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_damage)],
            PHOTOS: [
                MessageHandler(filters.PHOTO, receive_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, photos_done),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )

    app.add_handler(conversation)
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_error_handler(error_handler)
    return app


def main() -> None:
    app = build_application()
    logger.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
