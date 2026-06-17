"""Acquire raw foreign-student data from official Korean sources."""
import os
import requests

# data.go.kr file dataset detail page for KEDI "Foreign Student Status by University".
# The direct download URL is resolved during Task 3 discovery and pasted here.
BULK_XLSX_URL = "https://www.data.go.kr/download/15050054/fileData.do"


def download_bulk_xlsx(dest_dir: str) -> str:
    """Download the KEDI bulk XLSX into dest_dir and return the saved path."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, "foreign_students.xlsx")
    resp = requests.get(BULK_XLSX_URL, timeout=60)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)
    return path
