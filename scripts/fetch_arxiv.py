import datetime as dt
import textwrap
import requests
import feedparser
from pathlib import Path

# --------- 설정 ---------
TOPIC_NAME = "Gaussian Splatting"
YEAR = 2026
MAX_RESULTS = 100

QUERY = 'ti:"gaussian splatting"' ## 검색할 명령어

ARXIV_API_URL = "http://export.arxiv.org/api/query"

# GitHub Actions의 리포 루트 절대 경로를 직접 지정
README_PATH = Path(
    "/home/runner/work/2026_Arxiv_gaussian-splatting-Paper_List/2026_Arxiv_gaussian-splatting-Paper_List/README.md"
)
# ------------------------


def fetch_entries():
    params = {
        "search_query": QUERY,
        "start": 0,
        "max_results": MAX_RESULTS,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    resp = requests.get(ARXIV_API_URL, params=params, timeout=20)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)

    entries = []
    for e in feed.entries:
        published = dt.datetime(*e.published_parsed[:6])
        if published.year != YEAR:
            continue

        title = " ".join(e.title.split())
        url = e.link
        authors = ", ".join(a.name for a in e.authors)
        ymd = published.strftime("%Y-%m-%d")

        entries.append(
            {"title": title, "url": url, "authors": authors, "date": ymd}
        )

    entries.sort(key=lambda x: x["date"], reverse=True)
    return entries


def make_markdown_table(entries):
    if not entries:
        return f"_No papers found yet for {YEAR}._"

    lines = []
   lines.append("| Id | Date | Title | Authors |")
    lines.append("|----|------|-------|---------|")
    for idx, e in enumerate(entries, start=1):
        title_md = f"[{e['title']}]({e['url']})"
        title_md = "<br>".join(textwrap.wrap(title_md, width=80))
        authors_md = e["authors"].replace("\n", " ")
        lines.append(f"| {idx} | {e['date']} | {title_md} | {authors_md} |")
    return "\n".join(lines)


def update_readme(table_md):
    text = README_PATH.read_text(encoding="utf-8")

    start_tag = "<!-- PAPERS-START -->"
    end_tag = "<!-- PAPERS-END -->"

    if start_tag not in text or end_tag not in text:
        raise RuntimeError("README.md에 TAG가 없습니다.")

    before, rest = text.split(start_tag, 1)
    _, after = rest.split(end_tag, 1)

    new_block = (
        start_tag
        + "\n\n"
        + table_md
        + "\n\n_Last updated: "
        + dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).strftime(
            "%Y-%m-%d %H:%M (KST)"
        )
        + "_\n"
        + end_tag
    )

    new_text = before + new_block + after
    README_PATH.write_text(new_text, encoding="utf-8")


def main():
    import os
    print("CWD:", os.getcwd())
    print("README_PATH:", README_PATH)

    entries = fetch_entries()
    table_md = make_markdown_table(entries)
    update_readme(table_md)


if __name__ == "__main__":
    main()
