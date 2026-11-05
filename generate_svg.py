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

    report = eve.build_report()
    lines = report.splitlines()

    y = 80
    text_nodes = []
    for line in lines:
        name, _, eves = line.partition(" Is In ")
        text_nodes.append(
            f'<text x="40" y="{y}" font-family="Segoe UI, sans-serif" font-size="18" fill="#7aa2ff" font-weight="bold">{html.escape(name)} Is In</text>'
        )
        y += 24
        words = eves.split()
        chunk = []
        cur_y = y
        for w in words:
            chunk.append(w)
            if len(" ".join(chunk)) > 95:
                text_nodes.append(
                    f'<text x="60" y="{cur_y}" font-family="Consolas, monospace" font-size="11" fill="#9aa4bf">{html.escape(" ".join(chunk))}</text>'
                )
                chunk = []
                cur_y += 14
        if chunk:
            text_nodes.append(
                f'<text x="60" y="{cur_y}" font-family="Consolas, monospace" font-size="11" fill="#9aa4bf">{html.escape(" ".join(chunk))}</text>'
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
      <stop offset="0%" stop-color="#1a2340"/>
      <stop offset="100%" stop-color="#0b0f1a"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bg)"/>
  <text x="40" y="40" font-family="Segoe UI, sans-serif" font-size="28" fill="#ffffff" font-weight="bold">EVE</text>
  <text x="40" y="62" font-family="Segoe UI, sans-serif" font-size="13" fill="#9aa4bf">All the holidays, but days away are shown as that many eves.</text>
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
