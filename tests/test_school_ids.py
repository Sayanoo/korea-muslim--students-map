from pipeline.school_ids import parse_candidates, match_school_id

SAMPLE = '''
<a href="#" onclick="gnf_go_schl_detail('0000069','compt');" target="_self">고려대학교</a>
<a href="#" onclick="gnf_go_schl_detail('0001215','pubinfo');" target="_self">고려대학교(세종)</a>
<a href="#" onclick="gnf_go_schl_detail('0000010','compt');" target="_self">가천대학교</a>
'''


def test_parse_candidates_extracts_id_name_pairs():
    cands = parse_candidates(SAMPLE)
    assert ("0000069", "고려대학교") in cands
    assert ("0000010", "가천대학교") in cands


def test_match_prefers_exact_name():
    assert match_school_id(SAMPLE, "고려대학교") == "0000069"
    assert match_school_id(SAMPLE, "가천대학교") == "0000010"


def test_match_normalizes_branch_suffixes():
    # XLSX form "고려대학교(세종)_분교" should map to the (세종) entry
    assert match_school_id(SAMPLE, "고려대학교(세종)_분교") == "0001215"


def test_match_returns_none_when_absent():
    assert match_school_id(SAMPLE, "서울대학교") is None
