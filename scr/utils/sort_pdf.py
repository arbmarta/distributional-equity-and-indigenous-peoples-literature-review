import os
import re
import shutil
import pandas as pd
from PyPDF2 import PdfReader
from tqdm import tqdm

PDF_DIR = "../../data/included_studies"
OUTPUT_CSV = "../../data/keyword_matches.csv"

# Create output folders
FOLDER_INDIGENOUS = "indigenous_variables"
FOLDER_RACE_ETHNICITY = "race_ethnicity_variables"
FOLDER_NO_KEYWORDS = "no_race_variables"

KEYWORDS = [
    "White",
    "Black",
    "Hispanic",
    "Situational Vulnerability",
    "Indigenous",
    "Indian",
    "First Nation",
    "Métis",
    "Metis",
    "Inuit",
    "reserve",
    "American Indian",
    "Alaska Native",
    "Enrolled Tribe",
    "Principal Tribe",
    "Native Hawaiian",
    "Samoan",
    "Chamorro",
    "Pacific Islander"
]

INDIGENOUS_COLS = [
    "Indigenous",
    "Indian",
    "First Nation",
    "Métis",
    "Metis",
    "Inuit",
    "reserve",
    "American Indian",
    "Alaska Native",
    "Enrolled Tribe",
    "Principal Tribe",
    "Native Hawaiian",
    "Samoan",
    "Chamorro",
    "Pacific Islander"
]

CENSUS_KEYWORDS = [
    "census",
    "community survey"
]

def extract_pdf_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text.lower()
    except Exception as e:
        print(f"[ERROR] Could not read {pdf_path}: {e}")
        return ""

keyword_patterns = {
    kw: re.compile(rf'\b{re.escape(kw.lower())}\b')
    for kw in KEYWORDS
}

census_patterns = [
    re.compile(rf'\b{re.escape(k)}\b', re.IGNORECASE)
    for k in CENSUS_KEYWORDS
]

# create output folders if they don't exist
os.makedirs(FOLDER_INDIGENOUS, exist_ok=True)
os.makedirs(FOLDER_RACE_ETHNICITY, exist_ok=True)
os.makedirs(FOLDER_NO_KEYWORDS, exist_ok=True)

rows = []
matched_files = []
no_census_files = []

# track files for each category
indigenous_files = []
race_ethnicity_files = []
no_keyword_files = []

pdf_files = sorted(
    f for f in os.listdir(PDF_DIR)
    if f.lower().endswith(".pdf")
)

for filename in tqdm(pdf_files, desc="Scanning PDFs", unit="pdf"):
    path = os.path.join(PDF_DIR, filename)
    text = extract_pdf_text(path)

    if not text:
        continue

    # census / community survey check
    if not any(p.search(text) for p in census_patterns):
        no_census_files.append(filename)

    # keyword logic
    row = {"Citation": filename[:-4]}
    found_any = False
    found_indigenous = False

    for kw, pattern in keyword_patterns.items():
        count = len(pattern.findall(text))
        row[kw] = 1 if count > 0 else 0
        if count > 0:
            found_any = True
            # Check if this keyword is in the indigenous list
            if kw in INDIGENOUS_COLS:
                found_indigenous = True

    if found_any:
        matched_files.append(filename)

    # Categorize the file
    if found_indigenous:
        indigenous_files.append(filename)
    elif found_any:
        race_ethnicity_files.append(filename)
    else:
        no_keyword_files.append(filename)

    rows.append(row)

# move files to appropriate folders
print("\nMoving files to subfolders...")

for filename in tqdm(indigenous_files, desc="Indigenous variables", unit="file"):
    src = os.path.join(PDF_DIR, filename)
    dst = os.path.join(FOLDER_INDIGENOUS, filename)
    if os.path.exists(src):
        shutil.copy2(src, dst)

for filename in tqdm(race_ethnicity_files, desc="Race/ethnicity variables", unit="file"):
    src = os.path.join(PDF_DIR, filename)
    dst = os.path.join(FOLDER_RACE_ETHNICITY, filename)
    if os.path.exists(src):
        shutil.copy2(src, dst)

for filename in tqdm(no_keyword_files, desc="No race variables", unit="file"):
    src = os.path.join(PDF_DIR, filename)
    dst = os.path.join(FOLDER_NO_KEYWORDS, filename)
    if os.path.exists(src):
        shutil.copy2(src, dst)

print(f"\nFiles moved:")
print(f"  - Indigenous variables: {len(indigenous_files)} files → {FOLDER_INDIGENOUS}/")
print(f"  - Race/ethnicity variables (non-Indigenous): {len(race_ethnicity_files)} files → {FOLDER_RACE_ETHNICITY}/")
print(f"  - No race variables: {len(no_keyword_files)} files → {FOLDER_NO_KEYWORDS}/")

# print census/community survey results
print("\nFILES WITHOUT 'CENSUS' OR 'COMMUNITY SURVEY':\n")
for f in no_census_files:
    print(f)

print(f"\nTotal files without census/community survey terms: {len(no_census_files)}\n")

# save keyword matches
df_kw = pd.DataFrame(rows)
df_kw = df_kw[["Citation"] + KEYWORDS]
df_kw.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"Wrote {OUTPUT_CSV}")
print(f"PDFs with at least one keyword match: {len(matched_files)}")
