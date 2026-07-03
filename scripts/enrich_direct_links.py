import json
import re
import time
from pathlib import Path
from urllib.parse import quote

import requests


ROOT = Path(__file__).resolve().parents[1]
META_JSON = ROOT / "data" / "2310.12986_reference_metadata.json"


def norm_title(text):
    return re.sub(r"[^a-z0-9 ]+", " ", (text or "").lower()).split()


def title_score(query, candidate):
    q = set(norm_title(query))
    c = set(norm_title(candidate))
    if not q or not c:
        return 0.0
    return len(q & c) / len(q | c)


def normalize_arxiv_url(value):
    if not value:
        return None
    value = str(value).strip()
    if "arxiv.org" in value:
        value = value.replace("/pdf/", "/abs/").removesuffix(".pdf")
        return value
    return f"https://arxiv.org/abs/{value}"


def semantic_search(title):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": title,
        "limit": 5,
        "fields": "title,authors,year,venue,externalIds,url,openAccessPdf",
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception:
        return []


def openalex_search(title):
    url = "https://api.openalex.org/works"
    params = {
        "search": title,
        "per-page": 5,
        "select": "id,display_name,doi,publication_year,primary_location,locations,open_access",
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json().get("results", [])
    except Exception:
        return []


def link_from_semantic(title, cache):
    if title not in cache:
        cache[title] = semantic_search(title)
        time.sleep(0.2)
    best = None
    best_score = 0.0
    for item in cache.get(title, []):
        score = title_score(title, item.get("title"))
        if score > best_score:
            best = item
            best_score = score
    if not best or best_score < 0.42:
        return None, "semantic_no_match", best_score
    external = best.get("externalIds") or {}
    if external.get("ArXiv"):
        return normalize_arxiv_url(external["ArXiv"]), "arxiv_semantic", best_score
    oa = best.get("openAccessPdf") or {}
    if oa.get("url") and "semanticscholar.org" not in oa["url"]:
        if "arxiv.org" in oa["url"]:
            return normalize_arxiv_url(oa["url"]), "arxiv_semantic_pdf", best_score
        return oa["url"], "open_pdf_semantic", best_score
    if external.get("DOI"):
        return f"https://doi.org/{external['DOI']}", "doi_semantic", best_score
    if best.get("url") and "/paper/" in best["url"]:
        return best["url"], "semantic_paper", best_score
    return None, "semantic_no_direct", best_score


def iter_openalex_locations(item):
    primary = item.get("primary_location")
    if primary:
        yield primary
    for loc in item.get("locations") or []:
        yield loc


def link_from_openalex(title, cache):
    if title not in cache:
        cache[title] = openalex_search(title)
        time.sleep(0.2)
    best = None
    best_score = 0.0
    for item in cache.get(title, []):
        score = title_score(title, item.get("display_name"))
        if score > best_score:
            best = item
            best_score = score
    if not best or best_score < 0.42:
        return None, "openalex_no_match", best_score
    for loc in iter_openalex_locations(best):
        if not loc:
            continue
        for key in ("landing_page_url", "pdf_url"):
            url = loc.get(key)
            if url and "arxiv.org" in url:
                return normalize_arxiv_url(url), "arxiv_openalex", best_score
    for loc in iter_openalex_locations(best):
        if not loc:
            continue
        url = loc.get("landing_page_url") or loc.get("pdf_url")
        if url and "openalex.org" not in url:
            return url, "landing_openalex", best_score
    if best.get("doi"):
        return best["doi"], "doi_openalex", best_score
    if best.get("id"):
        return best["id"], "openalex_work", best_score
    return None, "openalex_no_direct", best_score


def verify_url(url):
    if not url:
        return {"ok": False, "status": None, "final_url": None, "error": "missing"}
    try:
        r = requests.get(url, allow_redirects=True, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        return {
            "ok": 200 <= r.status_code < 400,
            "status": r.status_code,
            "final_url": r.url,
            "error": None,
        }
    except Exception as exc:
        return {"ok": False, "status": None, "final_url": None, "error": str(exc)[:160]}


def main():
    meta = json.loads(META_JSON.read_text(encoding="utf-8"))
    rows = meta["rows"]
    semantic_cache = meta.setdefault("direct_link_semantic_cache", {})
    openalex_cache = meta.setdefault("direct_link_openalex_cache", {})

    for row in rows:
        title = row["title"]
        semantic_link, semantic_source, semantic_score = link_from_semantic(title, semantic_cache)
        openalex_link, openalex_source, openalex_score = link_from_openalex(title, openalex_cache)

        # Prefer arXiv links whenever either source finds one.
        candidates = []
        for link, source, score in [
            (semantic_link, semantic_source, semantic_score),
            (openalex_link, openalex_source, openalex_score),
            (row.get("url"), "existing_url", 1.0 if row.get("url") else 0.0),
        ]:
            if not link:
                continue
            priority = 0
            if "arxiv.org/abs/" in link:
                priority = 100
            elif "doi.org/" in link:
                priority = 80
            elif "openreview.net" in link or "openaccess.thecvf.com" in link:
                priority = 75
            elif "/paper/" in link and "semanticscholar.org" in link:
                priority = 55
            elif "semanticscholar.org/search" in link:
                priority = 0
            else:
                priority = 65
            candidates.append((priority, score, link, source))
        candidates.sort(reverse=True)
        chosen = candidates[0] if candidates else (0, 0.0, None, "no_candidate")
        direct_url = chosen[2]
        verification = verify_url(direct_url) if direct_url else verify_url(None)
        if verification["ok"]:
            row["url"] = direct_url
            row["direct_url"] = direct_url
            row["direct_url_source"] = chosen[3]
        else:
            row["direct_url"] = direct_url
            row["direct_url_source"] = f"{chosen[3]}_unverified"
        row["direct_url_verified"] = verification
        print(
            f"[{row['ref_id']:02d}] {title[:64]} -> {row.get('direct_url_source')} "
            f"{verification.get('status')} {direct_url}",
            flush=True,
        )

    META_JSON.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
