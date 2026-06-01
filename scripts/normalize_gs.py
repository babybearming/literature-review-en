#!/usr/bin/env python3
"""Normalize Google Scholar scrape results into the standard papers JSON format.

Input: GS scrape JSON (from evaluate_script results)
Output: Standardized papers JSON compatible with generate_html.py
"""

import json, sys, re

sys.stdout.reconfigure(encoding="utf-8")


def parse_journal_year(jy_str):
    """Parse 'Journal, Year' or 'Journal, Year - Publisher' string."""
    venue = ""
    year = ""
    if not jy_str:
        return venue, year
    # Find year first
    m = re.search(r"\b(19|20)\d{2}\b", jy_str)
    if m:
        year = int(m.group())
    # Venue is everything before the year
    parts = jy_str.split(",")
    for p in parts:
        pm = re.search(r"\b(19|20)\d{2}\b", p)
        if pm:
            venue = ",".join(parts[:parts.index(p)]).strip()
            break
    if not venue and parts:
        venue = parts[0].strip()
    return venue, year


def parse_authors_to_list(authors_str):
    """Parse GS author string. GS format varies:
    - 'A Smith, B Jones, C Lee' (initial + last)
    - 'John Smith, Bob Jones' (first + last)
    - 'Smith A, Jones B' (last + initial)
    Strategy: split by ', ' and treat each as a full name.
    """
    if not authors_str:
        return []
    # Split by comma-space, each chunk is one author name
    parts = [a.strip() for a in authors_str.split(", ") if a.strip()]
    return parts


def format_apa_authors(authors):
    if not authors:
        return ""
    if len(authors) == 1:
        return authors[0]
    elif len(authors) == 2:
        return authors[0] + ", & " + authors[1]
    elif len(authors) <= 20:
        return ", ".join(authors[:-1]) + ", & " + authors[-1]
    else:
        return ", ".join(authors[:19]) + ", ... " + authors[-1]


def in_text_cite(authors, year):
    if not authors:
        return f"({year})"
    last = lambda a: a.split()[-1]
    if len(authors) == 1:
        return f"({last(authors[0])}, {year})"
    elif len(authors) == 2:
        return f"({last(authors[0])} & {last(authors[1])}, {year})"
    else:
        return f"({last(authors[0])} et al., {year})"


def normalize(gs_results, category=""):
    """Convert GS scrape results array to standard paper dicts."""
    papers = []
    for r in gs_results:
        title = r.get("title", "")
        authors_str = r.get("authors", "")
        authors_list = parse_authors_to_list(authors_str)
        author_display = ", ".join(authors_list[:4])
        if len(authors_list) > 4:
            author_display += " et al."

        venue, year = parse_journal_year(r.get("journalYear", ""))
        if not year:
            year = ""

        cited_by = int(r.get("citedBy", "0") or "0")
        snippet = r.get("snippet", "")
        doi = ""
        href = r.get("href", "")
        if "doi.org/" in href:
            doi = href

        # APA reference
        apa = format_apa_authors(authors_list) + f" ({year}). {title}. {venue}."
        if doi:
            apa += f" https://doi.org/{doi.replace('https://doi.org/', '')}"

        papers.append({
            "title_en": title,
            "authors": author_display,
            "all_authors": authors_list,
            "year": year,
            "venue": venue,
            "cited_by": cited_by,
            "abstract": snippet,
            "doi": doi,
            "apa_ref": apa,
            "in_text_cite": in_text_cite(authors_list, year),
            "category": category,
            "data_cid": r.get("dataCid", ""),
            "full_text_url": r.get("fullTextUrl", ""),
        })
    return papers


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="GS scrape results JSON")
    parser.add_argument("--output", required=True, help="Normalized output JSON")
    parser.add_argument("--category", default="", help="Category label")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, dict) and "results" in raw:
        results = raw["results"]
    elif isinstance(raw, list):
        results = raw
    else:
        results = [raw]

    papers = normalize(results, args.category)

    existing = []
    if args.output and len(papers) > 0:
        try:
            with open(args.output, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except FileNotFoundError:
            pass

    seen = {p["title_en"].lower().strip() for p in existing}
    for p in papers:
        key = p["title_en"].lower().strip()
        if key not in seen:
            existing.append(p)
            seen.add(key)

    existing.sort(key=lambda x: x["cited_by"], reverse=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"Normalized {len(papers)} new papers, total {len(existing)} in {args.output}")


if __name__ == "__main__":
    main()