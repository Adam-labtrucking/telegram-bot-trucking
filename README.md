# Trucking Accident Reporting Telegram Bot

Production-ready Telegram bot for collecting trucking accident details, saving structured JSON, generating professional PDF reports (with photos), and notifying an admin automatically.

## Features

- Guided, step-by-step accident intake flow.
- Captures all required fields:
  - Date & time
  - Driver full name and phone
  - Company name
  - Truck/unit number
  - Trailer number (optional)
  - Plate number (optional)
  - Exact location (Telegram location share or typed address)
  - City and State
  - Accident type (rear-end, backing, lane change, weather, other)
  - Detailed description
  - Injuries (Yes/No + note)
  - Police called (Yes/No + report number)
  - Other party data (name, phone, company, plate, insurance)
  - Witness info (optional)
  - Damage description
  - Multiple accident photos
- Saves data as structured JSON into `reports/`.
- Generates a formatted PDF into `pdfs/` using ReportLab.
- Embeds uploaded photos in PDF.
- Sends admin alert + PDF to admin chat ID.
- `/cancel` command to abort and clear current report.
- Logging + error handling.

## Project Structure

- `bot.py` - Main bot application.
- `requirements.txt` - Python dependencies.
- `.env.example` - Environment variable template.
- `reports/` - JSON outputs (auto-created).
- `pdfs/` - PDF outputs (auto-created).
- `photos/` - Uploaded photo files (auto-created).

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` with:

- `BOT_TOKEN`: Your BotFather token.
- `ADMIN_CHAT_ID`: Telegram ID where alerts and PDFs will be sent.

## Run

```bash
python bot.py
```

## Bot Commands

- `/start` - Start a new accident report.
- `/report` - Same as `/start`.
- `/cancel` - Cancel current report.

## Notes for Production

- Run behind a process manager (e.g. `systemd`, `supervisord`, or Docker restart policy).
- Persist `reports/`, `pdfs/`, and `photos/` using a mounted volume or persistent disk.
- Rotate logs externally if needed.

## Remotion video project

A Remotion project has been initialized in this repository with a starter **9:16 vertical composition** for TikTok/Reels.

### Files
- `remotion/index.ts` - Remotion entry point
- `remotion/Root.tsx` - Composition registration
- `remotion/VerticalStarter.tsx` - Vertical starter scene

### Run
```bash
npm run studio
```

### Render the starter video
```bash
npm run render
```

Output path:
- `out/vertical-starter.mp4`
