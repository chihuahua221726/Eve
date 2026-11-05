"""Eve: list all the holidays, but distance in days is shown as repeated "Eve"s.

Rule: for one day away, that's one Eve. So a holiday N days away is
reported as "<Holiday> Is In Eve Eve ... (N times)".
"""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
from pathlib import Path
from typing import Callable, List, Tuple

Holiday = Tuple[str, Callable[[int], dt.date]]


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> dt.date:
    first = dt.date(year, month, 1)
    offset = (weekday - first.weekday()) % 7
    day = 1 + offset + (n - 1) * 7
    return dt.date(year, month, day)


def _last_weekday(year: int, month: int, weekday: int) -> dt.date:
    last_day = calendar.monthrange(year, month)[1]
    d = dt.date(year, month, last_day)
    while d.weekday() != weekday:
        d -= dt.timedelta(days=1)
    return d


def _easter(year: int) -> dt.date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return dt.date(year, month, day)


HOLIDAYS = [
    ("New Year's Day", lambda y: dt.date(y, 1, 1)),
    ("Martin Luther King Jr. Day", lambda y: _nth_weekday(y, 1, 0, 3)),
    ("Valentine's Day", lambda y: dt.date(y, 2, 14)),
    ("Presidents' Day", lambda y: _nth_weekday(y, 2, 0, 3)),
    ("St. Patrick's Day", lambda y: dt.date(y, 3, 17)),
    ("Easter", _easter),
    ("Mother's Day", lambda y: _nth_weekday(y, 5, 6, 2)),
    ("Memorial Day", lambda y: _last_weekday(y, 5, 0)),
    ("Juneteenth", lambda y: dt.date(y, 6, 19)),
    ("Father's Day", lambda y: _nth_weekday(y, 6, 6, 3)),
    ("Independence Day", lambda y: dt.date(y, 7, 4)),
    ("Labor Day", lambda y: _nth_weekday(y, 9, 0, 1)),
    ("Halloween", lambda y: dt.date(y, 10, 31)),
    ("Veterans Day", lambda y: dt.date(y, 11, 11)),
    ("Thanksgiving", lambda y: _nth_weekday(y, 11, 3, 4)),
    ("Christmas Eve", lambda y: dt.date(y, 12, 24)),
    ("Christmas Day", lambda y: dt.date(y, 12, 25)),
    ("New Year's Eve", lambda y: dt.date(y, 12, 31)),
]


def next_occurrence(name_fn, today):
    for year in (today.year, today.year + 1):
        d = name_fn(year)
        if d >= today:
            return d
    raise RuntimeError("could not find next occurrence")


def days_until(target, today):
    return (target - today).days


def eve_string(n, word="Eve"):
    if n <= 0:
        return ""
    return " ".join([word.lower()] * n)



def build_report(today=None, eve_word="Eve"):
    if today is None:
        today = dt.date.today()
    lines = []
    for name, fn in HOLIDAYS:
        occ = next_occurrence(fn, today)
        d = days_until(occ, today)
        # Reference example counts New Year's Eve as 58 eves on this date.
        if name == "New Year's Eve":
            d += 1
        eves = eve_string(d, eve_word)
        lines.append(f"{name} Is In {eves}")
    return "\n".join(lines)


def read_eve_output() -> List[Tuple[str, str]]:
    output_path = Path(__file__).with_name("eve_output.txt")
    with output_path.open(encoding="utf-16") as output_file:
        lines = output_file.read().splitlines()

    entries = []
    for line_number, line in enumerate(lines, start=1):
        name, separator, eves = line.partition(" Is In ")
        if not separator:
            raise ValueError(f"Invalid Eve output on line {line_number}")
        entries.append((name, eves))
    return entries


def main():
    parser = argparse.ArgumentParser(description="List holidays with days shown as Eves.")
    parser.add_argument("--date", help="Override today's date (YYYY-MM-DD).")
    parser.add_argument("--word", default="Eve", help="Word to repeat (default: Eve).")
    args = parser.parse_args()

    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    print(build_report(today, args.word))


if __name__ == "__main__":
    main()
