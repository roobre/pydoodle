# pydoodle
A simple CLI to create `DATE` polls on doodle dot com, with less typing and clicks.

## Rationale
Most of the time I spent creating polls was adding the same hours and then clicking days. This automates the process.

## Usage

Create a poll for a 45m meeting, with slots from 10h to 18h, in the next 5 days (starting today):

```shell
./doodle.py MyMeeting --duration 45 --dates :+5 --after 10 --before 19
```

Same but start tomorrow:

```shell
./doodle.py MyMeeting --duration 45 --dates +1:+5 --after 10 --before 19
```

Manually specify dates

```shell
./doodle.py MyMeeting --duration 45 --dates 2020-01-15:2020-01-18 --after 10 --before 19
```

Create 1h meetings (default `--duration`) but create slots every 30m for extra flexibility:

```shell
./doodle.py MyMeeting --slot 30 --dates 2020-01-15:2020-01-18
```


Many other tweaks and endless possibilities can be achieved by reading the help:

```
> $ doodle.py --help                                                                                                                                                                                                                          
usage: doodle.py [-h] [--description [DESCRIPTION]] [--after [AFTER]] [--before [BEFORE]] [--duration [DURATION]] [--slot [SLOT]] [--weekdays] [--weekends] [--tz [TZ]] [--maybe] [--dates [DATES]] [--organizer [ORGANIZER]]
                 [--email [EMAIL]] [--notify] [--sure] [--dry-run]
                 name

Create DATE polls for meetings and other events, effortlessly

positional arguments:
  name                  Name or topic of the meeting

optional arguments:
  -h, --help            show this help message and exit
  --description [DESCRIPTION]
                        Description of the meeting
  --after [AFTER]       Create slots after this hour
  --before [BEFORE]     Do not create slots past this hour. Values greater than 23 will loop through the next day
  --duration [DURATION]
                        Duration of the meeting in minutes
  --slot [SLOT]         Time in minutes between slots start dates, that is, the size of the slot. Usually the same as --duration. By default will round --duration up to hours
  --weekdays            Create meeting on weekdays only
  --weekends            Create meeting on weekends only
  --tz [TZ]             Timezone. Defaults to $TZ from env, or "Europe/Madrid if empty
  --maybe               Allow "Yes, if need to be" answer
  --dates [DATES]       Date range [isodate|+ndays]:<isodate|+mdays>. "ndays" is relative to today, mdays is relative to the first date.
  --organizer [ORGANIZER]
                        Name of the organizer
  --email [EMAIL]       Organizer email
  --notify              Send notifications to organizer
  --sure                Force creation even if supplied parameters do not seem ok
  --dry-run             Print the request to doodle servers and do not create the doodle
```
