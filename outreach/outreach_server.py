"""
outreach_server.py — Zero-dependency local server for the SiteCraft SA outreach dashboard.
Serves dashboard.html and persists "sent" leads into active_clients.csv (the pipeline/recurring tracker).

Run:  cd C:/Users/Thabang/sitecraft-sa
       python outreach/outreach_server.py
Open:  http://127.0.0.1:8765/

Endpoints:
  GET  /            -> dashboard.html
  GET  /api/state   -> JSON {id:1, ...} of sent lead ids (from sent_ids.json)
  POST /api/sent    -> body {"id","name","town","phone"} ; appends to active_clients.csv (dedup) + sent_ids.json
"""
import json, os, csv
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # sitecraft-sa/
DASH = os.path.join(HERE, "dashboard.html")
ACTIVE = os.path.join(HERE, "active_clients.csv")
SENT = os.path.join(HERE, "sent_ids.json")
PORT = 8765

ACTIVE_FIELDS = ["date_joined","name","business","town","inv_no","setup_paid","month_paid","wa_number"]

def load_sent_ids():
    if os.path.exists(SENT):
        try: return json.load(open(SENT, encoding="utf-8"))
        except: return {}
    return {}

def save_sent_ids(d):
    json.dump(d, open(SENT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

def append_active(lead):
    # dedup by id stored in sent_ids
    ids = load_sent_ids()
    if lead.get("id") in ids:
        return False
    today = __import__("datetime").date.today().isoformat()
    row = {
        "date_joined": today, "name": lead.get("name",""), "business": lead.get("name",""),
        "town": lead.get("town",""), "inv_no": "", "setup_paid": "N",
        "month_paid": "", "wa_number": lead.get("phone",""),
    }
    write_header = not os.path.exists(ACTIVE) or os.path.getsize(ACTIVE) == 0
    with open(ACTIVE, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=ACTIVE_FIELDS)
        if write_header: w.writeheader()
        w.writerow(row)
    ids[lead.get("id")] = 1
    save_sent_ids(ids)
    return True

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers()
        self.wfile.write(body.encode("utf-8") if isinstance(body, str) else body)
    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            if os.path.exists(DASH):
                self._send(200, open(DASH, encoding="utf-8").read(), "text/html; charset=utf-8")
            else:
                self._send(404, "dashboard.html not found")
        elif p == "/api/state":
            self._send(200, json.dumps(load_sent_ids(), ensure_ascii=False))
        else:
            self._send(404, "not found")
    def do_POST(self):
        p = urlparse(self.path).path
        if p == "/api/sent":
            try:
                n = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            except Exception as e:
                self._send(400, json.dumps({"error": str(e)})); return
            added = append_active(data)
            self._send(200, json.dumps({"ok": True, "added": added}))
        else:
            self._send(404, "not found")
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"SiteCraft outreach server on http://127.0.0.1:{PORT}/")
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
