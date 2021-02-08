import csv
from pathlib import Path


class Reader:
    header = []

    def __init__(self, file_name, has_header=False):
        self.file_name = file_name
        if has_header:
            self.header = self._get_header()


    def _get_header(self):
        with open(self.file_name) as in_file:
            rd = csv.reader(in_file)
            it = iter(rd)
            # don't use on empty files
            return next(it)


    def __enter__(self):
        self._in_file = open(self.file_name)
        return self


    def __exit__(self, type, value, traceback):
        self._in_file.close()


    def __iter__(self):
        self._it = csv.DictReader(filter(lambda row: row[0] != '#', self._in_file))
        return self._it