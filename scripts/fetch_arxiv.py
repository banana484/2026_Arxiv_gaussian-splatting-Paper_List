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
        abstract = " ".join(e.summary.split())

        entries.append(
            {
                "title": title,
                "url": url,
                "authors": authors,
                "date": ymd,
                "abstract": abstract,
            }
        )

    entries.sort(key=lambda x: x["date"],reverse=True))
    return entries


def make_markdown_table(entries):
    if not entries:
        return f"_No papers found yet for {YEAR}._"

    lines = []
    # Id + Abstract 컬럼까지 포함
    lines.append("| Id | Date | Title | Authors | Abstract |")
    lines.append("|----|------|-------|---------|----------|")
    for idx, e in enumerate(entries, start=1):
        title_md = f"[{e['title']}]({e['url']})"
        title_md = "<br>".join(textwrap.wrap(title_md, width=80))
        authors_md = e["authors"].replace("\n", " ")
        # abstract는 너무 길어서 한두 줄로만 줄이거나, 앞부분만 자르기
        abstract_short = " ".join(e["abstract"].split()[:40]) + " ..."
        lines.append(
            f"| {idx} | {e['date']} | {title_md} | {authors_md} | {abstract_short} |"
        )
    return "\n".join(lines)




def update_readme(table_md, entries):
    text = README_PATH.read_text(encoding="utf-8")

    start_tag = "<!-- PAPERS-START -->"
    end_tag = "<!-- PAPERS-END -->"

    if start_tag not in text or end_tag not in text:
        raise RuntimeError("README.md에 TAG가 없습니다.")

    before, rest = text.split(start_tag, 1)
    _, after = rest.split(end_tag, 1)

    # abstract 섹션 생성
    abs_lines = []
    abs_lines.append("## Abstracts\n")
    for idx, e in enumerate(entries, start=1):
        abs_lines.append(f"### {idx}. {e['title']}")
        abs_lines.append("")
        abs_lines.append(e["abstract"])
        abs_lines.append("")
    abstracts_md = "\n".join(abs_lines)

    new_block = (
        start_tag
        + "\n\n"
        + table_md
        + "\n\n"
        + abstracts_md
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
    update_readme(table_md, entries)



if __name__ == "__main__":
    main()
