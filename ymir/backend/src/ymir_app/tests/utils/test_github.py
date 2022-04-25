from app.utils import github as m

tbl = """\
# public_index.md

|docker_name|functions|contributor|organization|description|
|--|--|--|--|--|
|executor-det-yolov4-training:release-0.5.0|training|alfrat|-|yolov4 detection model training|
|executor-det-yolov4-mining:release-0.5.0|mining inference|alfrat|-|yolov4 detection model mining & inference|
"""


def test_parse_line():
    assert m.parse_line("|a|b|c|") == ["a", "b", "c"]


def test_get_markdown_table():
    rows = []
    for line in tbl.split("\n"):
        if line.startswith("#") or not line:
            continue
        rows.append(line)
    records = list(m.parse_markdown_table(rows))
    assert len(records) == 2
    assert "docker_name" in records[0].keys()
