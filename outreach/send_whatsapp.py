"""
send_whatsapp.py — Hands-free outreach sender (Twilio WhatsApp API).
READ BEFORE RUNNING:
  - WhatsApp Business API (Twilio/Meta) REQUIRES opt-in. Cold-messaging strangers
    violates Meta's ToS and will get your number BANNED. Only use this on an
    opted-in list, or with an approved WhatsApp template for the first touch.
  - For the 247 township leads (unsolicited), use wa.me click-to-chat links
    (see township_leads_wa.csv) sent manually from your WhatsApp Business app.
    That path is free and ban-safe.

Setup:
  pip install twilio
  export TWILIO_SID=... TWILIO_TOKEN=... TWILIO_FROM=whatsapp:+27XXXX TWILIO_TO_CSV=outreach/opted_in.csv
  python send_whatsapp.py

opted_in.csv needs columns: phone, message  (phone in 27XXXXXXXXX format)
"""
import os, csv, time
from twilio.rest import Client

SID  = os.environ.get("TWILIO_SID")
TOK  = os.environ.get("TWILIO_TOKEN")
FR   = os.environ.get("TWILIO_FROM")      # e.g. whatsapp:+14155238886 (Twilio sandbox) or your WABA number
CSV  = os.environ.get("TWILIO_TO_CSV", "outreach/opted_in.csv")
LIMIT = int(os.environ.get("SEND_LIMIT", "50"))   # safety cap per run

def main():
    if not (SID and TOK and FR):
        print("MISSING ENV: set TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM. Stopping.")
        return
    if not os.path.exists(CSV):
        print(f"NO LIST: {CSV} not found. Build an opted-in list first. Stopping.")
        return
    client = Client(SID, TOK)
    sent = 0
    with open(CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            to = row.get("phone", "")
            msg = row.get("message", "")
            if not to or not msg:
                continue
            try:
                client.messages.create(
                    from_=FR,
                    to=f"whatsapp:+{to}",
                    body=msg,
                )
                sent += 1
                print(f"sent -> {to}")
            except Exception as e:
                print(f"FAIL {to}: {e}")
            if sent >= LIMIT:
                print(f"LIMIT {LIMIT} reached; stop. Re-run to continue.")
                break
            time.sleep(1)  # rate-limit friendliness
    print(f"DONE sent={sent}")

if __name__ == "__main__":
    main()
