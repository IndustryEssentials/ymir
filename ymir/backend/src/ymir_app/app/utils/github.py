from typing import Dict, Iterator, List

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0"}


def parse_line(line: str) -> List[str]:
    return [t.strip() for t in line.split("|")[1:-1]]


def get_markdown_table(url: str, timeout: int) -> List[str]:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    tbl = []
    for line in resp.iter_lines():
        line = line.decode()
        if line.startswith("#") or not line:
            continue
        tbl.append(line)
    return tbl


def parse_markdown_table(tbl: List[str]) -> Iterator[Dict]:
    for n, line in enumerate(tbl):
        row = {}
        if n == 0:
            header = parse_line(line)
        if n > 1:
            values = parse_line(line)
            for col, value in zip(header, values):
                row[col] = value
            yield row


def get_github_table(url: str, timeout: int = 30) -> List[Dict]:
    tbl = get_markdown_table(url, timeout)
    return list(parse_markdown_table(tbl))
