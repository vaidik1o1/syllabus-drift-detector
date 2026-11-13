import glob
import os
import pdfplumber

for path in sorted(glob.glob("data/raw/*.pdf")):
    with pdfplumber.open(path) as pdf:
        pages = len(pdf.pages)
        chars = sum(len(p.extract_text() or "") for p in pdf.pages)
    name = os.path.basename(path)
    print(f"{name:28} pages={pages:3}  chars={chars:7}  chars/page={chars // max(pages, 1)}")