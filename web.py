"""Serve the Eve holiday countdown as a small local web page."""

import argparse
import datetime as dt
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from eve import HOLIDAYS, days_until, next_occurrence


def render_page(today=None):
    if today is None:
        today = dt.date.today()

    cards = []
    for name, date_fn in HOLIDAYS:
        holiday_date = next_occurrence(date_fn, today)
        days = days_until(holiday_date, today)
        countdown = "Today" if days == 0 else f"In {days} Eves"
        cards.append(
            "<article class=\"holiday\">"
            f"<div><h2>{escape(name)}</h2>"
            f"<p>{holiday_date.strftime('%A, %B')} {holiday_date.day}</p></div>"
            f"<span class=\"countdown\">{escape(countdown)}</span>"
            "</article>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eve | Holiday countdown</title>
  <style>
    :root {{ color-scheme: light; font-family: system-ui, sans-serif; }}
    body {{ margin: 0; background: #f5f2eb; color: #24231f; }}
    main {{ max-width: 760px; margin: 0 auto; padding: 3rem 1.25rem; }}
    header {{ margin-bottom: 2rem; }}
    h1 {{ margin: 0; font-size: clamp(2.5rem, 8vw, 4rem); letter-spacing: -.06em; }}
    header p {{ color: #68645b; font-size: 1.1rem; }}
    .holiday {{ display: flex; align-items: center; justify-content: space-between;
      gap: 1rem; padding: 1rem 1.2rem; margin: .7rem 0; background: white;
      border: 1px solid #e8e3d9; border-radius: 14px; }}
    h2 {{ margin: 0; font-size: 1.05rem; }}
    .holiday p {{ margin: .35rem 0 0; color: #777267; font-size: .9rem; }}
    .countdown {{ flex: 0 0 auto; max-width: 52%; color: #7454bd; font-weight: 700;
      overflow-wrap: anywhere; text-align: right; }}
    @media (max-width: 520px) {{
      main {{ padding-top: 2rem; }}
      .holiday {{ align-items: flex-start; flex-direction: column; }}
      .countdown {{ max-width: 100%; text-align: left; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Eve</h1>
      <p>Every holiday, counted down in Eves.</p>
    </header>
    {''.join(cards)}
  </main>
</body>
</html>"""


class EveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        content = render_page().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    parser = argparse.ArgumentParser(description="Serve the Eve countdown locally.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: localhost).")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000).")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), EveHandler)
    print(f"Serving Eve at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
