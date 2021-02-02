#!/usr/bin/env python3

import argparse
import os
import json

import math
from datetime import date, datetime, timedelta


def create_doodle(options: list, args):
    req = {
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
    return req


def dates_from_arg(args):
    parts = str(args.dates).split(':')
    if len(parts) != 2:
        raise Exception('Malformed date string. See -h')

    if len(parts[0]) == 0:
        start = datetime.now()
    else:
        start = datetime.strptime(parts[0], '%Y-%m-%d')
    start.replace(hour=0, minute=0, second=0, microsecond=0)

    if parts[1].startswith('+'):
        ndays = int(parts[1][1:])
    else:
        ndays = (start - datetime.strptime(parts[1], '%Y-%m-%d')).days

    dates = []
    for d in range(0, ndays):
        dates.append(start + timedelta(days=d))

    return dates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('name', nargs=1, help='Name or topic of the meeting')
    parser.add_argument('--description', type=str, nargs='?', default='', help='Description of the meeting')
    parser.add_argument('--after', type=int, nargs='?', default=9, help='Start meeting after this hour')
    parser.add_argument('--before', type=int, nargs='?', default=17, help='End meeting before or at this hour')
    parser.add_argument('--duration', type=int, nargs='?', default=60, help='Duration of the meeting in minutes')
    parser.add_argument('--align', type=bool, nargs='?', default=True, help='Align start meetings to start at :00')
    parser.add_argument('--workdays', type=bool, nargs='?', default=True, help='Create meeting on workdays only')
    parser.add_argument('--tz', type=str, nargs='?', default=os.getenv('TZ', 'Europe/Madrid'), help='Timezone')
    parser.add_argument('--maybe', type=bool, nargs='?', default=False, help='Allow "Yes, if need to be" answer')
    parser.add_argument('--dates', type=str, nargs='?', default=":+3", help='Date range [isodate]:<isodate|+ndays>')
    parser.add_argument('--organizer', nargs='?', default='Pyddle', help='Name of the organizer')
    parser.add_argument('--email', type=str, nargs='?', default='nobody@devnullmail.com', help='Author email')
    parser.add_argument('--notify', type=bool, nargs='?', default=False, help='Send notifications to author')
    args = parser.parse_args()

    options = []
    for day in dates_from_arg(args):
        start = day.replace(hour=args.after)
        while True:
            end = start + timedelta(minutes=args.duration)
            if end > day.replace(hour=args.before):
                break
            options.append({
                "allday": False,
                "start": int(start.timestamp()),
                "end": int(end.timestamp()),
            })
            if args.align:
                start += timedelta(hours=math.ceil(args.duration/60))
            else:
                start = end

    print(json.dumps(create_doodle(options, args)))
