#!/usr/bin/env python3
"""SiteCraft SA — Playwright preview gate for generated sample sites.

Renders a generated HTML page in real Chromium (via the installed
`playwright-cli` + chromium browser) and saves a full-page PNG screenshot.

Why this exists: `playwright-cli` BLOCKS the file:// protocol, so we serve the
site over a local HTTP server and screenshot http://127.0.0.1. Also, the CLI
mangles absolute paths with slashes on Windows, so screenshots must use a
relative filename resolved from the CWD.

This is the "visual screenshot gate" the installed img2threejs / taste-skill
workflows require: a real rendered PNG as evidence a generated site looks right.

Usage:
  python preview_site.py <input.html> [output.png]

Requires: `playwright-cli` on PATH (npm i -g @playwright/cli) and chromium
installed (playwright-cli install-browser chromium).
"""
import os
import sys
import time
import signal
import subprocess
import urllib.request

HTTP_PORT = 8765
HTTP_HOST = "127.0.0.1"


def _free_port_already_up():
    try:
        urllib.request.urlopen(f"http://{HTTP_HOST}:{HTTP_PORT}/", timeout=1)
        return True
    except Exception:
        return False


def preview(input_html, output_png=None):
    input_html = os.path.abspath(input_html)
    if not os.path.isfile(input_html):
        raise FileNotFoundError(input_html)
    out_name = output_png or (os.path.splitext(os.path.basename(input_html))[0] + ".png")

    serve_dir = os.path.dirname(input_html)
    fname = os.path.basename(input_html)

    # ALWAYS start our own server in the input file's directory on a fresh port.
    # Never reuse a foreign server (a stale one could be serving a different dir
    # and we'd screenshot the wrong file). Find a free port.
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port)],
        cwd=serve_dir,
    )
    own_server = True
    base = f"http://127.0.0.1:{port}"
    for _ in range(20):
        try:
            urllib.request.urlopen(base + "/", timeout=1)
            break
        except Exception:
            time.sleep(0.25)
    else:
        server.send_signal(signal.SIGTERM)
        raise RuntimeError("local http server did not start")

    url = f"{base}/{urllib.request.quote(fname)}"
    try:
        cwd = os.getcwd()
        proc = subprocess.run(
            f'playwright-cli open "{url}" && playwright-cli screenshot --filename "{out_name}" --full-page',
            shell=True, cwd=cwd, capture_output=True, text=True,
        )
        if proc.returncode != 0 and "Error" in (proc.stderr or ""):
            sys.stderr.write(proc.stderr)
        out_path = os.path.join(cwd, out_name)
        if os.path.isfile(out_path):
            return out_path
        alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), out_name)
        return alt if os.path.isfile(alt) else None
    finally:
        if server is not None:
            server.send_signal(signal.SIGTERM)
            try:
                server.wait(timeout=5)
            except Exception:
                server.kill()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python preview_site.py <input.html> [output.png]")
        sys.exit(1)
    out = preview(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    if out and os.path.isfile(out):
        print("screenshot:", out, os.path.getsize(out), "bytes")
    else:
        print("FAILED to produce screenshot", file=sys.stderr)
        sys.exit(1)
