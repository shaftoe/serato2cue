#!/usr/bin/env python3
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from pprint import pprint
from os import environ
from sys import argv, stderr

DEBUG = False


@dataclass
class Track:
    index: int
    title: str
    author: str
    start_time: datetime
    end_time: datetime
    elapsed: timedelta

    @property
    def length(self) -> timedelta:
        return self.end_time - self.start_time

    @staticmethod
    def formatted_time(duration: timedelta) -> str:
        debug(f"processing time string `{duration}`")
        stringified = f"{duration}"
        hours, minutes, seconds = [int(field) for field in stringified.split(":")]
        return f"{(hours * 60) + minutes:02}:{seconds:02}:00"

    def __str__(self) -> str:
        if DEBUG:
            pprint(self, stderr)

        out = '''\n  TRACK {0.index:02} AUDIO
    TITLE "{0.title}"
    PERFORMER "{0.author}"'''.format(self)
        out += f"\n    INDEX 00 {self.formatted_time(self.elapsed)}"
        if DEBUG:
            out += f"\n    DEBUG START   {self.start_time}"
            out += f"\n    DEBUG END     {self.end_time}"
            out += f"\n    DEBUG LENGTH  {self.length}"
            out += f"\n    DEBUG ELAPSED {self.elapsed}"
        return out


'''Return a datetime object from a Serato CSV-exported time string, e.g: 20:10:29 GMT-4.'''
def time_from_string(data: str, date: datetime) -> datetime:
    return datetime.strptime(date+data[:8], "%d/%m/%Y%H:%M:%S")


def print_debug_warning() -> None:
    if DEBUG:
        stderr.write("\n###########################\n")
        stderr.write("###### DEBUG ENABLED ######\n")
        stderr.write("###########################\n")


def debug(msg: str) -> None:
    if DEBUG:
        stderr.write(msg+"\n")


def main() -> None:
    print_debug_warning()

    tracks = []
    recorded_date = None
    elapsed = timedelta(0)
    out = f'''REM COMMENT "Recorded by Serato DJ"
REM DATE {recorded_date}"
FILE "noname.wav" WAV'''

    for num, row in enumerate(reader, start=-1):
        debug("\nprocessing row %d" % (num+2))
        if DEBUG:
            pprint(row)

        if num == -1: # Ignore the header row
            continue

        if num == 0: # Grab the date
            recorded_date = row[0]
            continue

        tracks.append(
            Track(
                index=num,
                title=row[0],
                author=row[1],
                start_time=time_from_string(row[2], recorded_date),
                end_time=time_from_string(row[3], recorded_date),
                elapsed=elapsed,
            ))

    if DEBUG:
        pprint(tracks, stderr)

    for num, track in enumerate(tracks):
        if num >= len(tracks)-1:
            break
        track.end_time = tracks[num+1].start_time

    for track in tracks:
        debug(f"\nprocessing track {track.index}")
        track.elapsed = elapsed
        out += str(track)
        elapsed += track.length

    debug("")
    print(out)
    print_debug_warning()


if __name__ == '__main__':
    try:
        reader = csv.reader(open(argv[1], 'r'), delimiter=',')
    except IndexError:
        stderr.write("Usage: %s <serato_exported_session.csv>\n" % argv[0])
        exit(1)

    if environ.get("DEBUG") and environ["DEBUG"] == "y":
        DEBUG = True

    main()
