import html
import json
import re
import sys
import time
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "2310.12986_reference_metadata.json"
OUT_MD = ROOT / "2310.12986_references_paper_table.md"
OUT_HTML = ROOT / "2310.12986_references_paper_table.html"
BADGE_DIR = ROOT / "assets" / "reference_badges"
REF_TEXT = ROOT / "2310.12986_nolayout.txt"


REFERENCES = [
    (1, "Optimization Algorithms on Matrix Manifolds", "Princeton University Press", 2007, ["Theory", "Optimization"], "Training_Free"),
    (2, "Momentum improves optimization on riemannian manifolds", "AISTATS", 2021, ["Optimization", "Riemannian"], "Training_Free"),
    (3, "Hyperbolic busemann learning with ideal prototypes", "NeurIPS", 2021, ["Image", "Classification", "Hyperbolic"], "Retrain"),
    (4, "Ensemble deep manifold similarity learning using hard proxies", "CVPR", 2019, ["Retrieval", "Metric_Learning"], "Retrain"),
    (5, "Ensemble diffusion for retrieval", "ICCV", 2017, ["Retrieval", "Diffusion"], "Training_Free"),
    (6, "Manifold topology divergence: a framework for comparing data manifolds", "NeurIPS", 2021, ["Generative", "Topology"], "Training_Free"),
    (7, "Riemannian adaptive optimization methods", "ICLR", 2019, ["Optimization", "Riemannian"], "Training_Free"),
    (8, "Matching normalizing flows and probability paths on manifolds", "ICML", 2022, ["3D", "Generative", "Normalizing_Flow"], "Retrain"),
    (9, "A grassmann manifold handbook: Basic geometry and computational aspects", "arXiv", 2020, ["Theory", "Grassmann"], "Training_Free"),
    (10, "Mvc-net: A convolutional neural network architecture for manifold-valued images with applications", "arXiv", 2020, ["Video", "Manifold_NN"], "Retrain"),
    (11, "Geometric deep learning: Going beyond euclidean data", "IEEE Signal Processing Magazine", 2017, ["Survey", "Geometric_DL"], "Training_Free"),
    (12, "Gaussians on riemannian manifolds: Applications for robot learning and adaptive control", "IEEE Robotics & Automation Magazine", 2020, ["Theory", "Robotics"], "Training_Free"),
    (13, "Algorithms for manifold learning", "CoRR", 2005, ["Survey", "Dim_Reduction"], "Training_Free"),
    (14, "Manifoldnorm: Extending normalizations on riemannian manifolds", "arXiv", 2020, ["Manifold_NN", "Normalization"], "Retrain"),
    (15, "Manifoldnet: A deep neural network for manifold-valued data with applications", "IEEE TPAMI", 2022, ["Manifold_NN", "Image"], "Retrain"),
    (16, "Projective manifold gradient layer for deep rotation regression", "CVPR", 2022, ["3D", "Rotation"], "Retrain"),
    (17, "Deep learning for instance retrieval: A survey", "IEEE TPAMI", 2022, ["Survey", "Retrieval"], "Training_Free"),
    (18, "Riemannian approach to batch normalization", "NeurIPS", 2017, ["Manifold_NN", "Normalization"], "Retrain"),
    (19, "Improving diffusion models for inverse problems using manifold constraints", "arXiv", 2022, ["Diffusion", "Inverse_Problem"], "Training_Free"),
    (20, "Diffusion models in vision: A survey", "arXiv", 2022, ["Survey", "Diffusion"], "Training_Free"),
    (21, "Adaptive feature interpolation for low-shot image generation", "ECCV", 2022, ["Image", "GAN", "Low_Shot"], "Retrain"),
    (22, "Diffusion processes for retrieval revisited", "CVPR", 2013, ["Retrieval", "Diffusion"], "Training_Free"),
    (23, "Manifold optimization over the set of doubly stochastic matrices: A second-order geometry", "Technical report", 2018, ["Optimization", "Geometry"], "Training_Free"),
    (24, "A decade survey of content based image retrieval using deep learning", "IEEE Transactions on Circuits and Systems for Video Technology", 2022, ["Survey", "Retrieval"], "Training_Free"),
    (25, "A geometric approach for unsupervised similarity learning", "ICASSP", 2020, ["Retrieval", "Metric_Learning"], "Retrain"),
    (26, "Terse notes on riemannian geometry", "Technical report", 2010, ["Theory", "Riemannian"], "Training_Free"),
    (27, "KShapeNet: Riemannian network on kendall shape space for skeleton based action recognition", "CoRR", 2020, ["Video", "Action_Recognition"], "Retrain"),
    (28, "Parallel transport on kendall shape spaces", "GSI", 2021, ["Theory", "Shape_Space"], "Training_Free"),
    (29, "A geometric take on metric learning", "NeurIPS", 2012, ["Metric_Learning", "Geometry"], "Retrain"),
    (30, "Mining on manifolds: Metric learning without labels", "CVPR", 2018, ["Retrieval", "Metric_Learning"], "Retrain"),
    (31, "Riemannian adaptive stochastic gradient algorithms on matrix manifolds", "ICML", 2019, ["Optimization", "Riemannian"], "Training_Free"),
    (32, "Shape and shape theory", "Book", 1999, ["Theory", "Shape_Space"], "Training_Free"),
    (33, "Intrinsic neural fields: Learning functions on manifolds", "ECCV", 2022, ["3D", "Neural_Field"], "Retrain"),
    (34, "Trivializations for gradient-based optimization on manifolds", "NeurIPS", 2019, ["Optimization", "Riemannian"], "Training_Free"),
    (35, "Efficient riemannian optimization on the stiefel manifold via the cayley transform", "AISTATS", 2021, ["Optimization", "Stiefel"], "Training_Free"),
    (36, "Differentiating through the frechet mean", "ICML", 2020, ["Manifold_NN", "Frechet_Mean"], "Retrain"),
    (37, "Progressive attentional manifold alignment for arbitrary style transfer", "ACCV", 2022, ["Image", "Style_Transfer"], "Retrain"),
    (38, "Geomstats: A python package for riemannian geometry in machine learning", "JMLR", 2022, ["Software", "Riemannian"], "Training_Free"),
    (39, "Introduction to Geometric Learning in Python with Geomstats", "SciPy", 2020, ["Software", "Riemannian"], "Training_Free"),
    (40, "Geometric data analysis based on manifold learning with applications for image understanding", "SIBGRAPI", 2017, ["Image", "Dim_Reduction"], "Training_Free"),
    (41, "Unsupervised geometric disentanglement for surfaces via cfan-vae", "ICLR Workshop", 2021, ["3D", "VAE"], "Retrain"),
    (42, "Everything is there in latent space: Attribute editing and attribute style manipulation by stylegan latent space exploration", "ACM MM", 2022, ["Image", "StyleGAN"], "Training_Free"),
    (43, "Theseus: A Library for Differentiable Nonlinear Optimization", "NeurIPS", 2022, ["Software", "Optimization"], "Training_Free"),
    (44, "Learning on manifolds", "SSSPR", 2010, ["Theory", "Manifold"], "Training_Free"),
    (45, "Rethinking conditional GAN training: An approach using geometrically structured latent manifolds", "NeurIPS", 2021, ["GAN", "Generative"], "Retrain"),
    (46, "Embedding propagation: Smoother manifold for few-shot classification", "ECCV", 2020, ["Image", "Few_Shot"], "Retrain"),
    (47, "Hierarchical nearest neighbor graph embedding for efficient dimensionality reduction", "CVPR", 2022, ["Dim_Reduction", "Graph"], "Training_Free"),
    (48, "Directed graph embeddings in pseudo-riemannian manifolds", "ICML", 2021, ["Graph", "Embedding"], "Retrain"),
    (49, "Introduction to differential and Riemannian geometry", "Elsevier", 2020, ["Theory", "Riemannian"], "Training_Free"),
    (50, "Learning spherical convolution for 360 recognition", "IEEE TPAMI", 2022, ["Image", "360_Vision"], "Retrain"),
    (51, "LIDL: Local intrinsic dimension estimation using approximate likelihood", "ICML", 2022, ["Dim_Reduction", "Intrinsic_Dimension"], "Training_Free"),
    (52, "Pymanopt: A python toolbox for optimization on manifolds using automatic differentiation", "JMLR", 2016, ["Software", "Optimization"], "Training_Free"),
    (53, "An introduction to manifolds", "Springer", 2007, ["Theory", "Manifold"], "Training_Free"),
    (54, "Mls3rduh: Deep unsupervised hashing via manifold based local semantic similarity structure reconstructing", "IJCAI", 2020, ["Retrieval", "Hashing"], "Retrain"),
    (55, "Manifold mixup: Better representations by interpolating hidden states", "ICML", 2019, ["Image", "Regularization"], "Retrain"),
    (56, "Improving metric dimensionality reduction with distributed topology", "arXiv", 2021, ["Dim_Reduction", "Topology"], "Training_Free"),
    (57, "Dreamnet: A deep riemannian manifold network for spd matrix learning", "ACCV", 2022, ["Video", "SPD"], "Retrain"),
    (58, "Understanding how dimension reduction tools work: An empirical approach to deciphering t-SNE, UMAP, TriMap, and PaCMAP for data visualization", "JMLR", 2022, ["Survey", "Dim_Reduction"], "Training_Free"),
    (59, "Generative adversarial networks in computer vision", "ACM Computing Surveys", 2021, ["Survey", "GAN"], "Training_Free"),
    (60, "Dilated convolutional neural networks for sequential manifold-valued data", "ICCV", 2019, ["Video", "Manifold_NN"], "Retrain"),
    (61, "SpaceMAP: Visualizing high-dimensional data by space expansion", "ICML", 2022, ["Dim_Reduction", "Visualization"], "Training_Free"),
]


COLORS = {
    "arXiv": "#d73a49",
    "PDF": "#007ec6",
    "Image": "#8a0f8f",
    "Video": "#8a0f8f",
    "3D": "#8a0f8f",
    "Theory": "#8a0f8f",
    "Software": "#8a0f8f",
    "Survey": "#6a737d",
    "Training_Free": "#b7950b",
    "Retrain": "#b7950b",
}


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def make_badge(label, color=None):
    BADGE_DIR.mkdir(parents=True, exist_ok=True)
    color = color or COLORS.get(label, "#6a737d")
    width = max(34, 8 * len(label) + 14)
    path = BADGE_DIR / f"{slug(label)}.svg"
    safe = html.escape(label)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="{safe}">
  <title>{safe}</title>
  <rect width="{width}" height="20" rx="3" fill="{color}"/>
  <text x="{width / 2:.1f}" y="14" text-anchor="middle" font-family="Verdana,Arial,sans-serif" font-size="10" font-weight="700" fill="#fff">{safe}</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    return path


def badge_md(label):
    color = COLORS.get(label, "#6a737d")
    safe = html.escape(str(label))
    return (
        f'<span style="display:inline-block;padding:1px 6px;margin:2px 2px 2px 0;'
        f'border-radius:3px;background:{color};color:#fff;font-size:10px;'
        f'font-weight:700;line-height:18px;white-space:nowrap;">{safe}</span>'
    )


def venue_badge(venue, year):
    label = venue
    if venue in {"arXiv", "CoRR"}:
        label = f"arXiv {year}"
    elif venue in {"Technical report", "Book", "Springer", "Elsevier", "Princeton University Press"}:
        label = venue
    else:
        label = f"{venue} {year}"
    return label


def search_semantic_scholar(title):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": title,
        "limit": 3,
        "fields": "title,authors,year,venue,publicationVenue,externalIds,url,abstract,publicationTypes",
    }
    try:
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 429:
            time.sleep(1)
            r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()
        data = r.json().get("data", [])
    except Exception as exc:
        return {"error": str(exc), "data": []}
    return {"data": data}


def search_openalex(title):
    url = "https://api.openalex.org/works"
    params = {
        "search": title,
        "per-page": 3,
        "select": "id,display_name,publication_year,authorships,primary_location",
    }
    try:
        r = requests.get(url, params=params, timeout=6)
        r.raise_for_status()
        return {"data": r.json().get("results", [])}
    except Exception as exc:
        return {"error": str(exc), "data": []}


def score_title(query, candidate):
    q = set(re.sub(r"[^a-z0-9 ]+", " ", query.lower()).split())
    c = set(re.sub(r"[^a-z0-9 ]+", " ", candidate.lower()).split())
    if not q or not c:
        return 0.0
    return len(q & c) / len(q | c)


def extract_openalex_institutions(openalex_item):
    institutions = []
    authors = []
    for authorship in openalex_item.get("authorships", []) or []:
        author = authorship.get("author") or {}
        if author.get("display_name"):
            authors.append(author["display_name"])
        for inst in authorship.get("institutions", []) or []:
            name = inst.get("display_name")
            if name and name not in institutions:
                institutions.append(name)
    return authors, institutions


def load_reference_texts():
    if not REF_TEXT.exists():
        return {}
    lines = REF_TEXT.read_text(encoding="utf-8", errors="ignore").splitlines()
    refs = {}
    current_id = None
    current = []
    for line in lines:
        m = re.match(r"^\[(\d+)\]\s*(.*)", line)
        if m:
            if current_id is not None:
                refs[current_id] = " ".join(current).strip()
            current_id = int(m.group(1))
            current = [m.group(2).strip()]
        elif current_id is not None:
            if line.strip():
                current.append(line.strip())
    if current_id is not None:
        refs[current_id] = " ".join(current).strip()
    return refs


def fallback_authors_from_reference(raw_ref, title):
    if not raw_ref:
        return ""
    normalized_ref = re.sub(r"\s+", " ", raw_ref)
    normalized_title = re.sub(r"\s+", " ", title)
    idx = normalized_ref.lower().find(normalized_title.lower()[: min(45, len(normalized_title))])
    if idx <= 0:
        # Fallback: most references use "Authors. Title. Venue".
        parts = normalized_ref.split(". ")
        return parts[0].strip() if parts else ""
    authors = normalized_ref[:idx].strip()
    return authors.rstrip(".").strip()


def markdown_text(text):
    return str(text).replace("|", "\\|")


def enrich():
    rows = []
    raw_refs = load_reference_texts()
    semantic_cache = {}
    openalex_cache = {}
    if OUT_JSON.exists():
        try:
            existing = json.loads(OUT_JSON.read_text(encoding="utf-8"))
            semantic_cache = existing.get("semantic_scholar_cache", {})
            openalex_cache = existing.get("openalex_cache", {})
        except Exception:
            semantic_cache = {}
            openalex_cache = {}

    for ref_id, title, fallback_venue, fallback_year, tags, usage in REFERENCES:
        if title not in semantic_cache:
            semantic_cache[title] = search_semantic_scholar(title)
            time.sleep(0.25)
        candidates = semantic_cache[title].get("data", [])
        best = None
        best_score = 0
        for item in candidates:
            s = score_title(title, item.get("title", ""))
            if s > best_score:
                best = item
                best_score = s

        if best and best_score >= 0.45:
            authors = ", ".join(a.get("name", "") for a in best.get("authors", [])[:8] if a.get("name"))
            if len(best.get("authors", [])) > 8:
                authors += " et al."
            venue = best.get("venue") or fallback_venue
            year = best.get("year") or fallback_year
            url = best.get("url") or ""
            external = best.get("externalIds") or {}
            if external.get("ArXiv"):
                url = f"https://arxiv.org/abs/{external['ArXiv']}"
            title_out = best.get("title") or title
            source = "Semantic Scholar"
        else:
            authors = fallback_authors_from_reference(raw_refs.get(ref_id, ""), title)
            venue = fallback_venue
            year = fallback_year
            url = ""
            title_out = title
            source = "Reference fallback"

        if title not in openalex_cache:
            openalex_cache[title] = search_openalex(title_out)
            time.sleep(0.15)
        openalex_candidates = openalex_cache[title].get("data", [])
        best_openalex = None
        best_openalex_score = 0
        for item in openalex_candidates:
            s = score_title(title_out, item.get("display_name", ""))
            if s > best_openalex_score:
                best_openalex = item
                best_openalex_score = s
        openalex_authors, institutions = ([], [])
        if best_openalex and best_openalex_score >= 0.45:
            openalex_authors, institutions = extract_openalex_institutions(best_openalex)
        if not authors and openalex_authors:
            authors = ", ".join(openalex_authors[:8])
            if len(openalex_authors) > 8:
                authors += " et al."
        institution_text = "; ".join(institutions[:6]) if institutions else "Institute unavailable"
        if len(institutions) > 6:
            institution_text += "; et al."

        rows.append(
            {
                "ref_id": ref_id,
                "title": title_out,
                "authors": authors,
                "venue": venue,
                "year": year,
                "url": url,
                "tags": tags,
                "usage": usage,
                "metadata_source": source,
                "institutions": institution_text,
                "openalex_match_score": round(best_openalex_score, 3),
                "fallback_venue": fallback_venue,
                "fallback_year": fallback_year,
                "match_score": round(best_score, 3),
            }
        )
        OUT_JSON.write_text(
            json.dumps(
                {
                    "rows": rows,
                    "semantic_scholar_cache": semantic_cache,
                    "openalex_cache": openalex_cache,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(
            f"[{ref_id:02d}/61] {title[:70]} -> {venue or fallback_venue} {year or fallback_year} ({source}; institute={institution_text[:60]})",
            flush=True,
        )

    OUT_JSON.write_text(
        json.dumps(
            {
                "rows": rows,
                "semantic_scholar_cache": semantic_cache,
                "openalex_cache": openalex_cache,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return rows


def infer_modality(tags):
    priority = ["Image", "Video", "3D", "Software", "Theory", "Survey"]
    mods = [tag for tag in priority if tag in tags]
    if not mods:
        if "Retrieval" in tags:
            mods.append("Image")
        elif "Dim_Reduction" in tags:
            mods.append("Theory")
        elif "Optimization" in tags or "Riemannian" in tags:
            mods.append("Theory")
        elif "GAN" in tags or "Diffusion" in tags or "Generative" in tags:
            mods.append("Image")
        else:
            mods.append("Theory")
    return mods[:3]


def build_markdown(rows):
    rows = sorted(rows, key=lambda r: (int(r["year"] or 0), -int(r["ref_id"])), reverse=True)
    lines = [
        "# Paper Table for References in arXiv:2310.12986",
        "",
        "Source survey: [A survey of manifold learning and its applications for multimedia](https://arxiv.org/abs/2310.12986)",
        "",
        "## Paper Table",
        "",
        "| **Title & Authors * Institute** | **Date** | **Links** | **Modality & Position** | **Tags** |",
        "| --- | --- | --- | --- | :---: |",
    ]
    for row in rows:
        venue = row["venue"] or row["fallback_venue"]
        year = row["year"] or row["fallback_year"]
        title = markdown_text(row["title"])
        link = row["url"] or f"https://www.semanticscholar.org/search?q={requests.utils.quote(row['title'])}&sort=relevance"
        author_text = markdown_text(row["authors"] or "Authors unavailable in metadata")
        institute_text = markdown_text(row.get("institutions") or "Institute unavailable")
        title_cell = (
            f"{badge_md(venue_badge(venue, year))}<br>[{title}]({link})"
            f" <br> {author_text}"
            f" <br> *Institute:* {institute_text}"
        )
        date_cell = str(year)
        links_cell = f"[Search]({link})" if not row["url"] else f"[Paper]({link})"
        mod_cell = " ".join(badge_md(m) for m in infer_modality(row["tags"]))
        tag_labels = [row["usage"]] + [t for t in row["tags"] if t not in infer_modality(row["tags"])]
        tag_cell = "<br> ".join(badge_md(t) for t in tag_labels[:5])
        lines.append(f"| {title_cell} | {date_cell} | {links_cell} | {mod_cell} | {tag_cell} |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Venue/year are searched through Semantic Scholar where available, with the original survey reference used as fallback.",
            "- Institute information is searched through OpenAlex where available; otherwise the table says `Institute unavailable`.",
            "- `Training_Free` is explicitly included for entries that do not require training a new model in the cited method; entries that train a neural network or representation model are marked `Retrain`.",
            "- Tags are method-level summaries for the manifold-learning survey context, not MLLM-token-compression positions.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def badge_span(label):
    color = COLORS.get(label, "#6a737d")
    return f'<span class="badge" style="background:{color}">{html.escape(label)}</span>'


def build_html(rows):
    rows = sorted(rows, key=lambda r: (int(r["year"] or 0), -int(r["ref_id"])), reverse=True)
    body_rows = []
    for row in rows:
        venue = row["venue"] or row["fallback_venue"]
        year = row["year"] or row["fallback_year"]
        venue_label = venue_badge(venue, year)
        link = row["url"] or f"https://www.semanticscholar.org/search?q={requests.utils.quote(row['title'])}&sort=relevance"
        mods = " ".join(badge_span(m) for m in infer_modality(row["tags"]))
        tag_labels = [row["usage"]] + [t for t in row["tags"] if t not in infer_modality(row["tags"])]
        tag_html = "<br>".join(badge_span(t) for t in tag_labels[:5])
        institutions = html.escape(row.get("institutions") or "Institute unavailable")
        body_rows.append(
            f"""
      <tr>
        <td>{badge_span(venue_label)}<br><a class="paper-title" href="{html.escape(link)}">{html.escape(row['title'])}</a><div class="authors">{html.escape(row['authors'] or 'Authors unavailable in metadata')}</div><div class="institutes"><strong>Institute:</strong> {institutions}</div></td>
        <td class="date-col">{html.escape(str(year))}</td>
        <td class="links-col"><a href="{html.escape(link)}">{'Paper' if row['url'] else 'Search'}</a></td>
        <td>{mods}</td>
        <td class="tags-col">{tag_html}</td>
      </tr>"""
        )

    html_text = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Paper Table - arXiv 2310.12986 References</title>
  <style>
    body {{ margin: 24px; font-family: Arial, Helvetica, sans-serif; color: #111; background: #fff; }}
    h2 {{ margin: 0 0 18px; font-size: 22px; }}
    table {{ width: 100%; max-width: 1240px; border-collapse: collapse; table-layout: fixed; font-size: 13px; line-height: 1.45; }}
    th, td {{ border: 1px solid #3f4650; padding: 8px 10px; vertical-align: middle; }}
    th {{ text-align: center; font-weight: 700; background: #fff; }}
    tbody tr:nth-child(even) {{ background: #e8edf3; }}
    .title-col {{ width: 48%; }}
    .date-col {{ width: 8%; text-align: center; }}
    .links-col {{ width: 9%; text-align: center; }}
    .mod-col {{ width: 15%; }}
    .tags-col {{ width: 20%; text-align: center; }}
    a {{ color: #0645ad; }}
    .badge {{ display: inline-block; padding: 1px 6px; margin: 2px 2px 2px 0; border-radius: 3px; color: #fff; font-size: 10px; font-weight: 700; line-height: 18px; white-space: nowrap; }}
    .paper-title {{ display: block; margin: 6px 0 2px; font-size: 14px; }}
    .authors {{ margin-top: 4px; }}
    .institutes {{ margin-top: 4px; color: #333; }}
  </style>
</head>
<body>
  <h2>Paper Table</h2>
  <table>
    <thead>
      <tr>
        <th class="title-col">Title &amp; Authors * Institute</th>
        <th class="date-col">Date</th>
        <th class="links-col">Links</th>
        <th class="mod-col">Modality &amp;<br>Position</th>
        <th class="tags-col">Tags</th>
      </tr>
    </thead>
    <tbody>
{''.join(body_rows)}
    </tbody>
  </table>
</body>
</html>
"""
    OUT_HTML.write_text(html_text, encoding="utf-8")


def main():
    rows = enrich()
    build_markdown(rows)
    build_html(rows)
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_HTML}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
