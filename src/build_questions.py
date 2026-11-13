import glob
import os
import re

import pandas as pd

# Symbols that only show up in the broken Hindi font, never in normal English
GARBLE = re.compile("[{}$~|`\u00a1\u00a5\u00f0\u00a9\u00cc\u00ec\u00cf\u00ef]")
FOOTER = re.compile(r"P\.T\.O|^\s*---\s*page|^\s*\d{1,3}-\d+/\d+/\d+|CCeennttrraall", re.I)
SECTION = re.compile(r"^\s*section\s*[-:\u2013\u2014]?\s*([a-e])\b", re.I)
QSTART = re.compile(r"^\s*(\d{1,2})(?:\s*[.)]\s+|\s+(?=[A-Z]))(\S.*)$")

def is_junk(line):
    s = line.strip()
    if not s:
        return True
    if GARBLE.search(s) or FOOTER.search(s):
        return True
    return bool(re.fullmatch(r"[\d\s]+", s))  # stray marks / subscripts


def split_questions(text):
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if GARBLE.search(s):
            m = re.match(r"^(\d{1,2})\s*[.)]\s", s)
            if m:  # numbered Hindi line: keep only the question number
                lines.append(f"{m.group(1)}. @@")
            continue
        if not is_junk(raw):
            lines.append(s)
    questions, current, expected, section = [], None, 1, ""
    for line in lines:
        sec = SECTION.match(line)
        if sec and len(line) <= 14:  # a standalone "SECTION A" header
            if current:
                questions.append(current)
            current, section = None, sec.group(1).upper()
            continue
        m = QSTART.match(line)
        n = int(m.group(1)) if m else 0
        if m and section and expected <= n <= expected + 2:
            if current:
                questions.append(current)
            current = {"section": section, "qno": n, "text": m.group(2)}
            expected = n + 1
        elif current:
            current["text"] += " " + line
    if current:
        questions.append(current)
    return questions


rows = []
files = sorted(glob.glob("data/processed/paper_*.txt")
               + glob.glob("data/processed/sample_paper_*.txt"))
for path in files:
    name = os.path.splitext(os.path.basename(path))[0]
    year = int(re.search(r"(\d{4})", name).group(1))
    with open(path, encoding="utf-8") as f:
        qs = split_questions(f.read())
    for q in qs:
        rows.append({
            "paper": name, "year": year, "section": q["section"],
            "qno": q["qno"],
            "text": re.sub(r"\s+", " ", q["text"].replace("@@", "")).strip(),
            "label": "",
        })
    nums = [q["qno"] for q in qs]
    gaps = [n for n in range(1, max(nums, default=0) + 1) if n not in nums]
    print(f"{name:22} {len(qs)} questions, last Q{max(nums, default=0)}, missing {gaps}")

df = pd.DataFrame(rows)
df.to_csv("data/processed/questions_raw.csv", index=False, encoding="utf-8-sig")
print("total:", len(df))
if len(df):
    print(df[df.year == 2024].head(5)[["qno", "text"]].to_string(max_colwidth=100))