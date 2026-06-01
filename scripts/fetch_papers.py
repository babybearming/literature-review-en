import json
import requests
import time
import sys

def search_openalex(keyword, top=15, year_from=2014):
    url = "https://api.openalex.org/works"
    params = {
        "search": keyword,
        "per-page": min(top, 50),
        "filter": f"from_publication_date:{year_from}-01-01",
        "sort": "cited_by_count:desc",
        "mailto": "research@example.com"
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            print(f"Error for keyword \'{keyword}\': {response.status_code}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Exception for keyword \'{keyword}\': {e}", file=sys.stderr)
        return []

def safe_get(d, *keys, default=""):
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return default
        if d is None:
            return default
    return d if d is not None else default

def main():
    keyword_groups = [
        ("sea level rise impact coastal cities urban areas", "海平面上升沿海城市影响"),
        ("sea level rise coastal flooding adaptation cities", "沿海城市洪水适应性"),
        ("coastal city vulnerability climate change", "沿海城市脆弱性"),
        ("sea level rise storm surge urban coastal", "海平面上升风暴潮"),
        ("coastal urban planning climate change adaptation", "沿海城市气候适应规划"),
        ("sea level rise inundation coastal megacities", "沿海特大城市淹没"),
        ("global mean sea level rise projections coastal", "海平面上升预测"),
        ("coastal erosion sea level rise urban areas", "海岸侵蚀城市影响"),
    ]
    
    all_papers = []
    seen_ids = set()
    
    for keyword, category in keyword_groups:
        print(f"Searching: {keyword}", file=sys.stderr)
        results = search_openalex(keyword, top=15, year_from=2014)
        for work in results:
            if work["id"] not in seen_ids:
                seen_ids.add(work["id"])
                authors = []
                for a in work.get("authorships", [])[:10]:
                    author_name = safe_get(a, "author", "display_name")
                    if author_name:
                        authors.append(author_name)
                
                venue = safe_get(work, "primary_location", "source", "display_name")
                
                paper = {
                    "id": work["id"],
                    "title_en": work.get("title", ""),
                    "authors": authors,
                    "venue": venue,
                    "year": work.get("publication_year", ""),
                    "cited_by": work.get("cited_by_count", 0),
                    "abstract": work.get("abstract", ""),
                    "doi": work.get("doi", ""),
                    "url": work.get("doi", ""),
                    "category": category,
                    "title_cn": "",
                    "summary": "",
                    "motivation": ""
                }
                all_papers.append(paper)
        time.sleep(1)
    
    print(f"Total papers collected: {len(all_papers)}", file=sys.stderr)
    
    output_file = "G:/1Projects/WisPaper/literature-review-html/papers_raw.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_papers, f, ensure_ascii=False, indent=2)
    
    print(f"Output: {output_file}", file=sys.stderr)

if __name__ == "__main__":
    main()
