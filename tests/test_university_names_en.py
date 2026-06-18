from pipeline.university_names_en import to_english


def test_known_official_names():
    assert to_english("고려대학교") == "Korea University"
    assert to_english("서울시립대학교") == "University of Seoul"
    assert to_english("이화여자대학교") == "Ewha Womans University"


def test_campus_tags():
    assert to_english("한양대학교(ERICA)") == "Hanyang University (ERICA)"
    assert to_english("한양대학교(ERICA)_분교") == "Hanyang University (ERICA)"
    assert to_english("강원대학교 (제2캠퍼스)") == "Kangwon National University (2nd Campus)"
    assert to_english("중앙대학교_제2캠퍼스") == "Chung-Ang University (2nd Campus)"
    assert to_english("가야대학교(김해)") == "Kaya University (Gimhae)"
