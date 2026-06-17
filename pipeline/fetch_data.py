"""Acquire raw foreign-student data from official Korean sources."""
import os
import requests

# data.go.kr dataset 15050054 is a LINK-OUT type (atchFileTyCode=DATD01).
# The file is NOT hosted on data.go.kr; it lives on academyinfo.go.kr.
# The guessed URL /download/15050054/fileData.do returns 404.
#
# Real viewer URL (renders data via UbiReport, not a direct file download):
BULK_XLSX_URL = (
    "https://www.academyinfo.go.kr/uipnh/unt/unmcom/RdViewer.do"
    "?paramSvyYr=2025&paramMjrItem1=00&paramFormClftCd=30&paramItemId=33"
    "&paramSchlDivCd=02&paramDiv=A&paramItemDivCd=01"
    "&paramItemTimeCd=&paramItemDetailDivCd=&paramSchlKindCd=99"
    "&paramSchlEstabCd=99&paramZoneCd=99&paramSortItem=SCHL_NM&paramSortMethod=ASC"
    "&paramMjrCd=00&paramMjrItem2=00&paramMjrItem3=00&paramMjrItem4=00"
    "&paramMjrItem1Act=N&paramMjrItem4Act=N&paramMjrUsStp=0"
    "&paramSearchItem=SEARCH_SCHL_NM&tabIdx=&pageIdx="
)

# Bulk download portal (requires browser session + user-type selection):
BULK_DOWNLOAD_PORTAL = "https://www.academyinfo.go.kr/popup/main0810/list.do"


def download_bulk_xlsx(dest_dir: str) -> str:
    """Download the KEDI bulk XLSX into dest_dir and return the saved path."""
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, "foreign_students.xlsx")
    resp = requests.get(BULK_XLSX_URL, timeout=60)
    resp.raise_for_status()
    with open(path, "wb") as f:
        f.write(resp.content)
    return path
