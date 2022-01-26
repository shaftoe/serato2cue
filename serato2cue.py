#!/usr/bin/env python3
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta
from sys import argv
from time import time


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
        return out


'''Return a datetime object from a Serato CSV-exported time string, e.g: 20:10:29 GMT-4.'''
def time_from_string(data: str) -> datetime:
    return datetime.strptime(data[:8], "%H:%M:%S")


if __name__ == '__main__':
    try:
        reader = csv.reader(open(argv[1], 'r'), delimiter=',')
    except IndexError:
        print("Usage: %s <serato_exported_session.csv>" % argv[0])
        exit(1)

    out = 'FILE "noname.wav" WAV'
    elapsed = timedelta(0)

    for num, row in enumerate(reader, start=-1):
        if num > 0: # Ignore the first 2 rows
            track = Track(num, row[0], row[1], time_from_string(row[2]), time_from_string(row[3]), elapsed)
            out += str(track)
            elapsed += track.length

    print(out)
