"""
nurture_drip.py — Post-opt-in WhatsApp nurture drip for SiteCraft SA.
Runs AFTER a lead replies "SITECRAFT" (i.e. they opted in / initiated contact).

WHATSAPP RULES (read before sending):
  - Twilio WhatsApp (or Meta WABA) lets you reply FREE-FORM only within 24h of the
    lead's last inbound message. Steps that fire AFTER 24h need an approved template.
    Set TWILIO_TEMPLATE_SID to a pre-approved template for steps with day_offset > 1,
    or keep the drip inside 24h (steps 0-1) for free-form.
  - This script NEVER messages cold leads. opted_in.csv is a list of people who replied.

SETUP:
  pip install twilio
  export TWILIO_SID=... TWILIO_TOKEN=... TWILIO_FROM=whatsapp:+27XXXX
  export TWILIO_TEMPLATE_SID=...   # optional, for >24h steps
  python nurture_drip.py            # dry-run by default (no send)
  python nurture_drip.py --send     # actually send

INPUT  outreach/opted_in.csv  columns:
  phone, name, business, town, step, last_sent, wa_number
  - phone: 27XXXXXXXXX (E.164, no +)
  - step:  integer, next drip step to send (0 = first). Blank/0 = start.
  - last_sent: YYYY-MM-DD of last message sent (blank if none)

OUTPUT: updates opted_in.csv (advances step, sets last_sent), and prints a log.
"""
import os, csv, sys, argparse
from datetime import date, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
OPTED = os.path.join(HERE, "opted_in.csv")
FIELDS = ["phone","name","business","town","step","last_sent","wa_number"]

# Drip sequence: each step fires when (today >= last_sent + day_offset) and step matches.
# text uses {name},{business},{town},{inv_link} placeholders.
DRIP = [
    {"offset": 0, "key": "invoice",
     "text": "Thanks {name}! Thabang from SiteCraft SA here. Your free sample is live: "
             "https://thabs1234.github.io/sitecraft-sa/samples/townships/ — want the REAL site? "
             "Invoice (R1,500 setup + R450/mo): [send invoice link or PDF]. Reply PAID with proof to start."},
    {"offset": 1, "key": "details",
     "text": "Almost there {name}! To build your {business} site, just reply with: "
             "1) what you sell 2) area ({town}) 3) your WhatsApp for the site button 4) any logo/photos. I handle the rest."},
    {"offset": 3, "key": "followup",
     "text": "Hi {name} 👋 still keen on your {business} website? I've got capacity this week — "
             "reply your details and I'll have it live in 5 days. R1,500 + R450/mo, cancel anytime."},
    {"offset": 7, "key": "value",
     "text": "{name}, quick tip: businesses with a WhatsApp button on their site get ~3x more enquiries. "
             "Want me to add one to your {business} page? Just say go."},
]

def fmt(text, row):
    return text.format(name=row.get("name",""), business=row.get("business",""),
                        town=row.get("town",""), inv_link="")

def load():
    if not os.path.exists(OPTED):
        return []
    with open(OPTED, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save(rows):
    with open(OPTED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--send", action="store_true")
    args = ap.parse_args()
    do_send = args.send
    SID=os.environ.get("TWILIO_SID"); TOK=os.environ.get("TWILIO_TOKEN"); FR=os.environ.get("TWILIO_FROM")
    TPL=os.environ.get("TWILIO_TEMPLATE_SID")
    client = None
    if do_send:
        if not (SID and TOK and FR):
            print("MISSING ENV for --send: set TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM. Stopping.")
            return
        try:
            from twilio.rest import Client; client = Client(SID, TOK)
        except Exception as e:
            print("twilio import failed:", e); return
    rows = load()
    today = date.today()
    updated = 0
    for row in rows:
        ph = row.get("phone","").strip()
        if not ph:
            continue
        try: step = int(row.get("step") or 0)
        except: step = 0
        if step >= len(DRIP):
            continue
        # due?
        last = row.get("last_sent","").strip()
        due = True
        if last:
            try:
                due = today >= (date.fromisoformat(last) + timedelta(days=DRIP[step]["offset"]))
            except: due = True
        if not due:
            continue
        text = fmt(DRIP[step]["text"], row)
        label = f"[step {step}:{DRIP[step]['key']}] -> {ph}"
        if do_send:
            try:
                kw = {"from_": FR, "to": f"whatsapp:+{ph}", "body": text}
                if step >= 1 and TPL:
                    kw["content_sid"] = TPL  # use approved template for >24h steps
                client.messages.create(**kw)
                print("SENT", label)
            except Exception as e:
                print("FAIL", label, "->", e); continue
        else:
            print("DRYRUN", label, "::", text[:80], "...")
        row["step"] = str(step + 1)
        row["last_sent"] = today.isoformat()
        updated += 1
    if updated:
        save(rows)
        print(f"Updated {updated} lead(s) in opted_in.csv")
    else:
        print("Nothing due. All caught up.")

if __name__ == "__main__":
    main()
