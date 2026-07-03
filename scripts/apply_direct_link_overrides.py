import json
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
META_JSON = ROOT / "data" / "2310.12986_reference_metadata.json"


OVERRIDES = {
    1: {
        "url": "https://press.princeton.edu/books/hardcover/9780691132983/optimization-algorithms-on-matrix-manifolds",
        "venue": "Princeton University Press",
        "year": 2008,
    },
    9: {
        "url": "https://arxiv.org/abs/2011.13699",
        "venue": "Advances in Computational Mathematics",
        "year": 2024,
    },
    13: {"url": "https://cseweb.ucsd.edu/~lcayton/resexam.pdf"},
    16: {"url": "https://arxiv.org/abs/2110.11657"},
    17: {"url": "https://arxiv.org/abs/2101.11282"},
    18: {"url": "https://arxiv.org/abs/1709.09603"},
    20: {
        "url": "https://arxiv.org/abs/2209.04747",
        "venue": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
        "year": 2023,
    },
    21: {"year": 2022},
    24: {"url": "https://arxiv.org/abs/2012.00641"},
    25: {"url": "https://ieeexplore.ieee.org/document/9053418/"},
    26: {"url": "https://www.sci.utah.edu/~fletcher/RiemannianGeometryNotes.pdf"},
    27: {"url": "https://arxiv.org/abs/2011.12004"},
    28: {"url": "https://arxiv.org/abs/2103.04611"},
    29: {
        "url": "https://proceedings.neurips.cc/paper/2012/hash/ec5aa0b7846082a2415f0902f0da88f2-Abstract.html"
    },
    32: {"url": "https://www.wiley.com/en-us/Shape+and+Shape+Theory-p-9780470317006"},
    34: {"url": "https://arxiv.org/abs/1909.09501"},
    35: {"url": "https://arxiv.org/abs/2002.01113"},
    36: {"url": "https://arxiv.org/abs/2003.00335"},
    37: {
        "url": "https://openaccess.thecvf.com/content/ACCV2022/html/Luo_Progressive_Attentional_Manifold_Alignment_for_Arbitrary_Style_Transfer_ACCV_2022_paper.html"
    },
    38: {
        "url": "https://arxiv.org/abs/2004.04667",
        "year": 2020,
    },
    39: {"url": "https://proceedings.scipy.org/articles/Majora-342d178e-007"},
    40: {"url": "https://ieeexplore.ieee.org/document/8250223/"},
    41: {"url": "https://arxiv.org/abs/2005.11622"},
    44: {
        "url": "https://link.springer.com/chapter/10.1007/978-3-642-14980-1_4",
        "direct_url_note": "Replaces an automatic false match to Metric Learning on Manifolds.",
    },
    45: {"url": "https://arxiv.org/abs/2011.13055"},
    46: {"url": "https://arxiv.org/abs/2003.04151"},
    47: {"url": "https://arxiv.org/abs/2203.12997"},
    48: {"url": "https://arxiv.org/abs/2106.08678"},
    50: {"url": "https://ieeexplore.ieee.org/document/9541093/"},
    51: {"url": "https://arxiv.org/abs/2206.14882"},
    52: {"url": "https://arxiv.org/abs/1603.03236"},
    53: {
        "url": "https://link.springer.com/book/10.1007/978-1-4419-7400-6",
        "year": 2011,
    },
    54: {"url": "https://www.ijcai.org/proceedings/2020/479"},
    55: {"url": "https://arxiv.org/abs/1806.05236"},
    56: {"url": "https://arxiv.org/abs/2106.07613"},
    57: {
        "url": "https://openaccess.thecvf.com/content/ACCV2022/html/Wang_DreamNet_A_Deep_Riemannian_Manifold_Network_for_SPD_Matrix_Learning_ACCV_2022_paper.html"
    },
    58: {
        "url": "https://arxiv.org/abs/2012.04456",
        "year": 2021,
    },
    59: {
        "url": "https://arxiv.org/abs/1906.01529",
        "title": "Generative Adversarial Networks in Computer Vision: A Survey and Taxonomy",
    },
    60: {"url": "https://arxiv.org/abs/1910.02206"},
    61: {"url": "https://proceedings.mlr.press/v162/zu22a.html"},
}


def normalize_url(url):
    if not url:
        return url
    url = url.strip()
    if url.startswith("http://arxiv.org/"):
        url = "https://" + url.removeprefix("http://")
    if "arxiv.org/pdf/" in url:
        url = url.replace("/pdf/", "/abs/").removesuffix(".pdf")
    return url


def verify_url(url):
    if not url:
        return {"ok": False, "status": None, "final_url": None, "error": "missing"}
    try:
        r = requests.get(
            url,
            allow_redirects=True,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
            stream=True,
        )
        result = {
            "ok": 200 <= r.status_code < 400,
            "status": r.status_code,
            "final_url": r.url,
            "error": None,
        }
        r.close()
        return result
    except Exception as exc:
        return {"ok": False, "status": None, "final_url": None, "error": str(exc)[:160]}


def main():
    meta = json.loads(META_JSON.read_text(encoding="utf-8"))
    rows = {int(row["ref_id"]): row for row in meta["rows"]}

    for row in rows.values():
        for key in ("url", "direct_url"):
            if row.get(key):
                row[key] = normalize_url(row[key])

    for ref_id, override in OVERRIDES.items():
        row = rows[ref_id]
        if "venue" in override:
            row["venue"] = override["venue"]
        if "year" in override:
            row["year"] = override["year"]
        if "title" in override:
            row["title"] = override["title"]
        if "url" in override:
            url = normalize_url(override["url"])
            row["url"] = url
            row["direct_url"] = url
            row["direct_url_source"] = "manual_verified"
            verification = verify_url(url)
            row["direct_url_verified"] = verification
            if "direct_url_note" in override:
                row["direct_url_note"] = override["direct_url_note"]
            print(
                f"[{ref_id:02d}] {verification['status']} ok={verification['ok']} {url}",
                flush=True,
            )

    META_JSON.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
