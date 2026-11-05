"""Generate index.svg from the Eve holiday report.

Usage:
    python generate_svg.py            # generate once
    python generate_svg.py --watch    # regenerate when source files change
"""

import argparse
import html
import os
import time
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = ["eve.py", "eve_output.txt", "index.html"]
TARGET = os.path.join(HERE, "index.svg")


def build_svg() -> str:
    import importlib.util
    spec = importlib.util.spec_from_file_location("eve", os.path.join(HERE, "eve.py"))
    eve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eve)

    entries = eve.read_eve_output()

    y = 190
    text_nodes = []
    for name, eves in entries:
        text_nodes.append(
            f'<text x="40" y="{y}" font-family="Segoe UI, sans-serif" font-size="18" fill="#52634b" font-weight="bold">{html.escape(name)} Is In</text>'
        )
        y += 24
        words = eves.split()
        chunk = []
        cur_y = y
        for w in words:
            chunk.append(w)
            if len(" ".join(chunk)) > 95:
                text_nodes.append(
                    f'<text x="60" y="{cur_y}" font-family="Consolas, monospace" font-size="11" fill="#796b5a">{html.escape(" ".join(chunk))}</text>'
                )
                chunk = []
                cur_y += 14
        if chunk:
            text_nodes.append(
                f'<text x="60" y="{cur_y}" font-family="Consolas, monospace" font-size="11" fill="#796b5a">{html.escape(" ".join(chunk))}</text>'
            )
            cur_y += 14
        y = cur_y + 16

    height = max(y + 40, 1000)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="100%" height="100%" viewBox="0 0 1000 {height}" preserveAspectRatio="xMidYMid meet">
  <title>Eve - Holidays in Eves</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fffaf0"/>
      <stop offset="100%" stop-color="#f5efe3"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <text x="40" y="48" font-family="Georgia, serif" font-size="34" fill="#34291f" font-weight="bold">EVE</text>
  <text x="40" y="76" font-family="Segoe UI, sans-serif" font-size="13" fill="#796b5a">Every holiday is a little reason to gather around the table.</text>
  <g transform="translate(790 12) scale(.72)">
    <path d="M25 82 110 18l85 64v71H25z" fill="#c98255"/>
    <path d="m15 84 95-72 95 72-9 12-86-65-86 65z" fill="#754536"/>
    <path d="M89 96h42v57H89z" fill="#70513d"/>
    <circle cx="121" cy="126" r="2.5" fill="#f3d28a"/>
    <path d="M43 98h29v30H43zM148 98h29v30h-29z" fill="#f4d38b"/>
    <path d="M57 98v30m-14-15h29m90-15v30m-14-15h29" stroke="#fff4d9" stroke-width="4"/>
    <path d="M100 45h20V20h-20z" fill="#754536"/>
    <path d="M16 154h188" stroke="#52634b" stroke-width="7" stroke-linecap="round"/>
    <path d="M36 153q0-20 13-27 13 7 13 27m94 0q0-20 13-27 13 7 13 27" fill="#71815b"/>
  </g>
  {chr(10).join(text_nodes)}
</svg>
'''
    return svg
    return svg


def write_svg():
    svg = build_svg()
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {TARGET}")


def watch():
    mtimes = {}
    for src in SOURCES + ["generate_svg.py"]:
        p = os.path.join(HERE, src)
        if os.path.exists(p):
            mtimes[src] = os.path.getmtime(p)
    write_svg()
    print("Watching for changes... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
            changed = False
            for src in SOURCES + ["generate_svg.py"]:
                p = os.path.join(HERE, src)
                if os.path.exists(p):
                    m = os.path.getmtime(p)
                    if mtimes.get(src) != m:
                        mtimes[src] = m
                        changed = True
            if changed:
                write_svg()
    except KeyboardInterrupt:
        print("Stopped.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Regenerate on file changes.")
    args = parser.parse_args()
    if args.watch:
        watch()
    else:
        write_svg()


if __name__ == "__main__":
    main()
