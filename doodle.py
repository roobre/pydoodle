#!/usr/bin/env python3

import argparse
import os
import sys
import json
import math
from datetime import datetime, timedelta
from urllib import request


def main():
    parser = argparse.ArgumentParser(description='Create DATE polls for meetings and other events, effortlessly')
    parser.add_argument('name', nargs=1, help='Name or topic of the meeting')
    parser.add_argument('--description', type=str, nargs='?', default='', help='Description of the meeting')
    parser.add_argument('--after', type=int, nargs='?', default=9, help='Start meeting after this hour')
    parser.add_argument('--before', type=int, nargs='?', default=17, help='End meeting before or at this hour')
    parser.add_argument('--duration', type=int, nargs='?', default=60, help='Duration of the meeting in minutes')
    parser.add_argument('--slot', type=int, nargs='?', default=0,
                        help='Create slots set this minutes apart. By default will round duration up to hours')
    parser.add_argument('--weekdays', action='store_true', default=False, help='Create meeting on weekdays only')
    parser.add_argument('--weekends', action='store_true', default=False, help='Create meeting on weekends only')
    parser.add_argument('--tz', type=str, nargs='?', default=os.getenv('TZ', 'Europe/Madrid'), help='Timezone')
    parser.add_argument('--maybe', action='store_true', default=False, help='Allow "Yes, if need to be" answer')
    parser.add_argument('--dates', type=str, nargs='?', default=":+3",
                        help='Date range [isodate|+ndays]:<isodate|+mdays>. "ndays" is relative to today, mdays to first date.')
    parser.add_argument('--organizer', nargs='?', default='Pyydle', help='Name of the organizer')
    parser.add_argument('--email', type=str, nargs='?', default='nobody@devnullmail.com', help='Author email')
    parser.add_argument('--notify', action='store_true', default=False, help='Send notifications to author')
    parser.add_argument('--sure', action='store_true', default=False, help='Confirm creation despite weirdness')
    parser.add_argument('--dry-run', action='store_true', default=False, help='Just print the request')
    args = parser.parse_args()

    dates = dates_from_arg(args)

    if len(dates) > 5 * 8 and not args.sure:
        print(f'Specified constraints will yield {len(dates)} possible slots.', file=sys.stderr)
        print('Please confirm you really want to do this by passing --sure', file=sys.stderr)
        exit(1)

    if args.slot == 0:
        slot = timedelta(hours=math.ceil(args.duration / 60))
    else:
        slot = timedelta(minutes=args.slot)

    options = []
    for day in dates_from_arg(args):
        start = day.replace(hour=args.after)
        while True:
            end = start + timedelta(minutes=args.duration)
            if end > day.replace(hour=args.before):
                break

            if datetime.now() < start:
                options.append({
                    "allday": False,
                    "start": int(start.timestamp()) * 1000,
                    "end": int(end.timestamp()) * 1000,
                })

            start += slot

    create_doodle(options, args)


# Parse date string and return date and whether it was relative or not
def derelativize_date(datestr: str, base=datetime.now()):
    relative = False

    if not datestr.startswith('+'):
        return datetime.strptime(datestr, '%Y-%m-%d'), relative

    else:
        relative = True
        date = base.replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            # Try to add date
            date = date + timedelta(days=int(datestr[1:]))
        except ValueError:
            # Leave the date as it is.
            date = date

        return date, relative


def append_dates(
    days: int, weekday: int, relative: bool,
    start_date: datetime.date, is_weekdays: bool = False,
    has_args: bool = True
):
    i = 0
    dates = []
    if has_args:
        condition = weekday < 5 if is_weekdays else weekday >= 5
        while i < days:
            if condition:
                dates.append(start_date)
            elif relative:
                # Do not count non-matching days if end date was relative
                i -= 1

            start_date += timedelta(days=1)
            i += 1

    else:
        while i < days:
            dates.append(start_date)

            start_date += timedelta(days=1)
            i += 1

    return dates


def dates_from_arg(args):
    parts = str(args.dates).split(':')
    if len(parts) != 2:
        raise Exception('Malformed date string. See -h')

    start, _ = derelativize_date(parts[0])
    end, relative = derelativize_date(parts[1], start)
    ndays = (end - start).days + 1  # Number of days to generate slots on

    weekday = start.weekday()
    dates = []

    is_weekdays = True if args.weekdays else False
    has_args = True if args.weekdays or args.weekends else False
    dates = append_dates(
        ndays, weekday, relative, start,
        is_weekdays=is_weekdays, has_args=has_args
    )

    return dates


def create_doodle(options: list, args):
    body = {
        "initiator": {
            "name": args.organizer,
            "email": args.email,
            "notify": False,
            "timeZone": args.tz
        },
        "participants": [],
        "comments": [],
        "options": options,
        "type": "DATE",
        "title": args.name[0],
        "description": args.description,
        "timeZone": True,
        "preferencesType": "YESNOMAYBE" if args.maybe else "YESNO",
        "hidden": False,
        "remindInvitees": False,
        "askAddress": False,
        "askEmail": False,
        "askPhone": False,
        "locale": "en"
    }

    if args.dry_run:
        print(json.dumps(body))
        return

    req = request.Request(
        'https://doodle.com/api/v2.0/polls',
        method='POST',
        data=json.dumps(body).encode('utf-8'),
        headers={
            "User-Agent": "doodle.py",
            "Content-Type": 'application/json',
            "Origin": "https://doodle.com",
            "Accept": "application/json",
            "DNT": "1",
        },
    )

    with request.urlopen(req) as f:
        if f.status != 200:
            print(f"Error creating poll: {f.reason}")
            return
        response = json.load(f)
        print(f"https://doodle.com/poll/{response['id']}")


if __name__ == "__main__":
    main()
