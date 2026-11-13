import re
import sys

path = sys.argv[1]
lines = open(path, encoding="utf-8").read().splitlines()
start = next((i for i, l in enumerate(lines)
              if re.match(r"\s*section\s*[-–—:]?\s*a\b", l, re.I)), 0)
shown = 0
for line in lines[start:]:
    if line.strip() and all(ord(c) < 128 for c in line):
        print(line)
        shown += 1
        if shown >= 60:
            break