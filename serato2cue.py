#!/usr/bin/env python3
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from sys import argv
from os import environ

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
        stringified = f"{duration}"
        hours, minutes, seconds = [int(field) for field in stringified.split(":")]
        return f"{(hours * 60) + minutes:02}:{seconds:02}:00"

    def __str__(self) -> str:
        out = '''\n  TRACK {0.index:02} AUDIO
    TITLE "{0.title}"
    PERFORMER "{0.author}"'''.format(self)
        out += f"\n    INDEX 00 {self.formatted_time(self.elapsed)}"
        out += f"\n    INDEX 01 {self.formatted_time(self.length+self.elapsed)}"
        if DEBUG:
            out += f"\n    DEBUG START  {self.start_time}"
            out += f"\n    DEBUG END    {self.end_time}"
            out += f"\n    DEBUG LENGTH {self.length}"
        return out


'''Return a datetime object from a Serato CSV-exported time string, e.g: 20:10:29 GMT-4.'''
def time_from_string(data: str, date: datetime) -> datetime:
    return datetime.strptime(date+data[:8], "%d/%m/%Y%H:%M:%S")

def print_debug_warning() -> None:
    if DEBUG:
        print("\n###########################")
        print("###### DEBUG ENABLED ######")
        print("###########################\n")


if __name__ == '__main__':
    try:
        reader = csv.reader(open(argv[1], 'r'), delimiter=',')
    except IndexError:
        print("Usage: %s <serato_exported_session.csv>" % argv[0])
        exit(1)

    if environ.get("DEBUG") and environ["DEBUG"] == "y":
        DEBUG = True
        print_debug_warning()

    tracks = []
    recorded_date = None

    for num, row in enumerate(reader, start=-1):
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
                elapsed=timedelta(0),
            ))

    out = f'REM COMMENT "Recorded by Serato DJ"'
    out += f"\nREM DATE {recorded_date}"
    out += '\nFILE "noname.wav" WAV'

    for num, track in enumerate(tracks):
        if num >= len(tracks)-1:
            break
        track.end_time = tracks[num+1].start_time

    elapsed = timedelta(0)
    for track in tracks:
        track.elapsed = elapsed
        out += str(track)
        elapsed += track.length

    print(out)
    print_debug_warning()
