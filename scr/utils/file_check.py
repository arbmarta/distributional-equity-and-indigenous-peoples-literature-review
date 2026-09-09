import os
import pandas as pd

# Paths
csv_path = "../../data/included_studies.csv"
pdf_root_dir = "../../data/included_studies_sorted"

# Load CSV
df = pd.read_csv(csv_path, encoding="latin1")

# Get expected PDF filenames from the citation column, assumes citation matches the PDF filename exactly (without .pdf)
expected_pdfs = set(df["Citation"].astype(str).str.strip() + ".pdf")

# Collect all existing PDF filenames from directory and subdirectories
found_pdfs = set()

for root, _, files in os.walk(pdf_root_dir):
    for file in files:
        if file.lower().endswith(".pdf"):
            found_pdfs.add(file)

# Find missing PDFs
missing_pdfs = sorted(expected_pdfs - found_pdfs)

# Print results
if missing_pdfs:
    print("Missing PDF files:")
    for pdf in missing_pdfs:
        print(f"- {pdf}")
else:
    print("All PDFs are present.")
