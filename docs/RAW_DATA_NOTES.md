# Raw Data Notes

- Source: data.go.kr dataset 15050054 (KEDI foreign students by university)
- File: pipeline/data/raw/foreign_students.xlsx
- Sheet used: [NOT OBTAINED — see access barrier and schema notes below]
- University name column: [NOT OBTAINED — see below]
- Country representation: **NOT PRESENT** — this dataset does NOT contain a per-country/nationality breakdown. See DONE_WITH_CONCERNS section.
- Header row index (0-based): [NOT OBTAINED]
- Notes / quirks: [See below]

---

## Access Barrier

Dataset 15050054 is a **link-out type** dataset (`atchFileTyCode: DATD01`). The data is NOT
hosted on data.go.kr itself. The `atchFileId` and `fileDetailSn` fields returned by the
download API are both `null`. The actual data is served through academyinfo.go.kr using
the UbiReport proprietary report viewer.

### Download flow discovered

1. Dataset page: https://www.data.go.kr/data/15050054/fileData.do
2. API endpoint: `POST /tcs/dss/selectFileDataDownload.do` returns `status:true` but
   `atchFileId: null`, redirecting to:
   `https://www.academyinfo.go.kr/uipnh/unt/unmcom/RdViewer.do?paramSvyYr=2025&paramMjrItem1=00&paramFormClftCd=30&paramItemId=33&paramSchlDivCd=02&paramDiv=A&paramItemDivCd=01&...`
3. Bulk download portal: `https://www.academyinfo.go.kr/popup/main0810/list.do`
   - Endpoints: `selectDataList.do`, `fileInsert.do`, `selectReqRst.do`, `download.do`
   - `fileInsert.do` returns `{"result":"success"}` for anonymous requests
   - `selectReqRst.do` returns `{"exist":"0", "selFileArr":[]}` — no pre-generated file
   - `download.do` returns a **22-byte empty ZIP** (PK central directory end record only)
   - Conclusion: bulk download file generation requires an authenticated/session-tracked request

### Manual download step (for human operator)

To obtain the raw XLSX manually:
1. Open a browser and go to: https://www.academyinfo.go.kr/popup/main0810/list.do
2. In the grid on the left (공시항목/Disclosure Items), find "바-1. 외국학생 현황" (item_id=33,
   survey year 2025)
3. Click it to add to the selection grid on the right
4. Select your user type (e.g., 일반인 / General Public) and purpose (e.g., 데이터 활용)
5. Click the download button — the server generates a ZIP containing the XLSX
6. Save the ZIP and extract the XLSX to `pipeline/data/raw/foreign_students.xlsx`

---

## Schema Discovered (without the file)

The UbiReport viewer for item 33 (외국학생 현황, universities, 2025) embeds a compressed
`resultMaster` parameter that decodes to:

```
[{item_mstr_id=6935, form_clft_cd=30, row_num=3, col_num=32, form_ty_cd=}]
```

This means the report has:
- **3 header rows** (multi-level merged headers)
- **32 data columns** per university row

### What the 32 columns cover (from dataset description)

Based on the official dataset description on data.go.kr, the columns cover:

| Category | Sub-categories |
|---|---|
| 학위과정 (Degree program) | 재학생, 휴학생, 학사학위취득 유예 (enrolled, on leave, deferred graduation) |
| 교육과정 공동운영생 | Joint curriculum students with foreign universities |
| 연수과정-어학연수생 | Language training program students |
| 연수과정-교환학생 | Exchange students |
| 연수과정-방문학생 | Visiting students |
| 연수과정-기타 연수생 | Other training students |
| 언어능력-TOPIK 4급 이상 | Korean language test level 4+ (universities) |
| 언어능력-TOPIK 3급 이상 | Korean language test level 3+ (junior colleges) |
| 언어능력-영어트랙 TOEFL IBT 59+ | English track language requirement |

### CRITICAL: No per-country/nationality breakdown

The 32 columns cover student counts by **program type and language ability** — not by
country or nationality. There is no "국가" (country) or "국적" (nationality) column in
this dataset. The data shows university-level totals per student category only.

---

## Task 3b Required: Scraping per-university per-country data

Because the bulk XLSX lacks per-country data, Task 3b is needed. The
academyinfo.go.kr individual university disclosure pages may carry per-country breakdowns
via the UbiReport viewer for item 33. The per-university scraping approach should:

1. Enumerate university codes from the viewer grid
2. For each university, POST to the NewAcInfo.do UbiReport server to get table data
3. Parse the UbiReport response to extract student counts

Alternatively, the Ministry of Justice (법무부) dataset provides **national-level**
monthly foreign student counts by nationality (data.go.kr keyword: "법무부 외국인 유학생 국적별"),
but this does NOT have per-university breakdown.

---

## Confirmed Real URL (Viewer, not direct file)

```
VIEWER_URL = "https://www.academyinfo.go.kr/uipnh/unt/unmcom/RdViewer.do?paramSvyYr=2025&paramMjrItem1=00&paramFormClftCd=30&paramItemId=33&paramSchlDivCd=02&paramDiv=A&paramItemDivCd=01&paramItemTimeCd=&paramItemDetailDivCd=&paramSchlKindCd=99&paramSchlEstabCd=99&paramZoneCd=99&paramSortItem=SCHL_NM&paramSortMethod=ASC&paramMjrCd=00&paramMjrItem2=00&paramMjrItem3=00&paramMjrItem4=00&paramMjrItem1Act=N&paramMjrItem4Act=N&paramMjrUsStp=0&paramSearchItem=SEARCH_SCHL_NM&tabIdx=&pageIdx="
```

The guessed direct download URL `https://www.data.go.kr/download/15050054/fileData.do` returns 404.
The real mechanism is the academyinfo.go.kr bulk download portal (main0810).
