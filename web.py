"""Serve the Eve holiday countdown as a small local web page."""

import argparse
import datetime as dt
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from eve import HOLIDAYS, next_occurrence, read_eve_output


def render_page(today=None):
    if today is None:
        today = dt.date.today()

    holiday_dates = dict(HOLIDAYS)
    cards = []
    for name, eves in read_eve_output():
        date_fn = holiday_dates.get(name)
        if date_fn is None:
            raise ValueError(f"Unknown holiday in eve_output.txt: {name}")
        holiday_date = next_occurrence(date_fn, today)
        eve_count = len(eves.split())
        countdown = "Today" if eve_count == 0 else f"In {eve_count} Eves"
        cards.append(
            "<article class=\"holiday\">"
            f"<div class=\"holiday-copy\"><h2>{escape(name)}</h2>"
            f"<p>{holiday_date.strftime('%A, %B')} {holiday_date.day}</p></div>"
            f"<div class=\"countdown\">{escape(countdown)}"
            "<small>until the celebration</small>"
            f"<span class=\"eves\">{escape(eves)}</span></div>"
            "</article>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Eve | A cozy holiday countdown</title>
  <style>
    :root {{ color-scheme: light; font-family: "Segoe UI", system-ui, sans-serif;
      --paper: #fffdf8; --ink: #34291f; --muted: #796b5a; --green: #52634b;
      --rust: #a64f32; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; color: var(--ink); background:
      radial-gradient(ellipse at 50% 0%, #fffaf0 0%, transparent 58%), #f5efe3; }}
    header {{ min-height: 490px; padding: 3rem 1.25rem 4rem; display: grid;
      place-content: center; justify-items: center; text-align: center;
      background: linear-gradient(180deg, transparent 78%, #f5efe3); }}
    .eyebrow {{ color: var(--green); font-size: .78rem; font-weight: 700;
      letter-spacing: .18em; text-transform: uppercase; }}
    .cottage {{ display: block; width: clamp(150px, 27vw, 210px); margin: 1rem auto .3rem;
      filter: drop-shadow(0 12px 10px rgba(79, 56, 35, .13)); }}
    h1 {{ margin: 0; color: var(--ink); font: 700 clamp(3.2rem, 10vw, 6rem)/.95 Georgia, serif;
      letter-spacing: .08em; }}
    header p {{ max-width: 36rem; margin: .8rem auto 0; color: var(--muted);
      font-size: 1.05rem; line-height: 1.6; }}
    main {{ max-width: 820px; margin: -1rem auto 0; padding: 1rem 1.25rem 4rem; }}
    .list-intro {{ margin-bottom: 1.2rem; }}
    .list-intro h2 {{ margin: 0; font: 700 clamp(1.7rem, 5vw, 2.3rem)/1.1 Georgia, serif; }}
    .list-intro p {{ margin: .5rem 0 0; color: var(--muted); font-size: .9rem; }}
    .holiday {{ display: flex; align-items: center; justify-content: space-between;
      gap: 1rem; margin: .75rem 0; padding: 1.15rem 1.3rem;
      background: var(--paper); border: 1px solid #e8dece; border-radius: 16px;
      box-shadow: 0 4px 14px rgba(79, 56, 35, .045); }}
    h2 {{ margin: 0; }}
    .holiday-copy h2 {{ font: 600 1.05rem/1.35 "Segoe UI", system-ui, sans-serif; }}
    .holiday p {{ margin: .35rem 0 0; color: var(--muted); font-size: .9rem; }}
    .countdown {{ display: grid; flex: 0 0 auto; gap: .25rem; color: var(--rust);
      font-weight: 700; text-align: right; }}
    .countdown small {{ color: var(--green); font-size: .74rem; font-weight: 500; }}
    .eves {{ max-width: 32rem; color: var(--muted); font-size: .72rem;
      font-weight: 400; line-height: 1.5; overflow-wrap: anywhere; }}
    footer {{ padding: 1rem 1rem 3rem; color: var(--muted); text-align: center; font-size: .85rem; }}
    @media (max-width: 520px) {{
      header {{ min-height: 440px; }}
      .holiday {{ align-items: flex-start; flex-direction: column; }}
      .countdown {{ text-align: left; }}
      .eves {{ max-width: 100%; }}
    }}
  </style>
</head>
<body>
  <header>
      <div class="eyebrow">A cozy place for what's coming</div>
      <svg class="cottage" viewBox="0 0 220 170" role="img" aria-label="A cozy little cottage">
        <path d="M25 82 110 18l85 64v71H25z" fill="#c98255"/>
        <path d="m15 84 95-72 95 72-9 12-86-65-86 65z" fill="#754536"/>
        <path d="M89 96h42v57H89z" fill="#70513d"/>
        <circle cx="121" cy="126" r="2.5" fill="#f3d28a"/>
        <path d="M43 98h29v30H43zM148 98h29v30h-29z" fill="#f4d38b"/>
        <path d="M57 98v30m-14-15h29m90-15v30m-14-15h29" stroke="#fff4d9" stroke-width="4"/>
        <path d="M100 45h20V20h-20z" fill="#754536"/>
        <path d="M16 154h188" stroke="#52634b" stroke-width="7" stroke-linecap="round"/>
        <path d="M36 153q0-20 13-27 13 7 13 27m94 0q0-20 13-27 13 7 13 27" fill="#71815b"/>
      </svg>
      <h1>Eve</h1>
      <p>Every holiday is a little reason to gather around the table.</p>
  </header>
  <main>
    <div class="list-intro">
      <h2>Coming home soon</h2>
      <p>One eve for every day until the celebration.</p>
    </div>
    {''.join(cards)}
  </main>
  <footer>Save a seat. The next celebration is on its way.</footer>
</body>
</html>"""


class EveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/eve_output.txt":
            content = Path(__file__).with_name("eve_output.txt").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-16le")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path == "/index.html":
            content = Path(__file__).with_name("index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
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
