import glob
import os
import pdfplumber

os.makedirs("data/processed", exist_ok=True)
scanned = {"paper_2016", "paper_2020", "paper_2022", "paper_2026"}  # need OCR later

for path in sorted(glob.glob("data/raw/*.pdf")):
    name = os.path.splitext(os.path.basename(path))[0]
    if name in scanned:
        continue
    parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            parts.append(f"\n--- page {i} ---\n" + (page.extract_text() or ""))
    with open(f"data/processed/{name}.txt", "w", encoding="utf-8") as f:
        f.write("".join(parts))
    print("saved", name)