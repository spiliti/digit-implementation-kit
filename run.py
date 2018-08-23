#!/usr/bin/env python
import io
import re

pattern1 = re.compile(r'(?<={)([a-z]+)=', re.I)
pattern2 = re.compile(r':([a-z][^,{}. [\]]+)', re.I)
pattern3 = re.compile(r'\\"', re.I)

with io.open("test.csv") as f:
    headers = list(map(lambda f: f.strip(), f.readline().split(",")))
    for line in f.readlines():
        orig_line = line
        data = []
        for i, l in enumerate(line.split('","')):
            data.append(headers[i] + ":" + re.sub('^"|"$', "", l))

        line = "{" + ','.join(data) + "}"
        line = pattern1.sub(r'"\1":', line)
        line = pattern2.sub(r':"\1"', line)
        print(line)