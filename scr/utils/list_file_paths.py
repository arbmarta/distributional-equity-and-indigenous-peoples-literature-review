import os
import csv

directory = "../../included_studies_sorted"
output_file = "../../data/included_studies_file_list.csv"

with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["file_path"])
    for root, dirs, files in os.walk(directory):
        for file in files:
            writer.writerow([os.path.join(root, file)])

print(f"Saved to {output_file}")
