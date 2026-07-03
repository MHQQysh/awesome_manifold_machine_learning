import json
import re
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
META_JSON = ROOT / "2310.12986_reference_metadata.json"
OUT = ROOT / "README.md"


VENUE_SHORT = {
    "International Conference on Artificial Intelligence and Statistics": "AISTATS",
    "Neural Information Processing Systems": "NeurIPS",
    "European Conference on Computer Vision": "ECCV",
    "IEEE International Conference on Acoustics, Speech, and Signal Processing": "ICASSP",
    "IEEE Transactions on Pattern Analysis and Machine Intelligence": "TPAMI",
    "IEEE Transactions on Circuits and Systems for Video Technology": "TCSVT",
    "IEEE Signal Processing Magazine": "IEEE_SPM",
    "IEEE Robotics & Automation Magazine": "IEEE_RAM",
    "ACM Computing Surveys": "ACM_CSUR",
    "Princeton University Press": "Book",
    "Springer": "Book",
    "Elsevier": "Book",
    "Book": "Book",
    "Technical report": "Tech_Report",
    "Riemannian Geometric Statistics in Medical Image Analysis": "Book_Chapter",
}


COLOR = {
    "venue": "blue",
    "arxiv": "red",
    "modality": "purple",
    "usage": "yellowgreen",
    "method": "lightgrey",
    "software": "cyan",
    "theory": "cyan",
    "survey": "lightgrey",
}


def clean_text(text):
    if text is None:
        return ""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def badge(label, message=None, color="lightgrey"):
    label = str(label).strip()
    if message is None:
        # Empty left label creates a compact one-part badge on shields.io.
        return f"![{label}](https://img.shields.io/badge/-{quote(label, safe='')}-{color})"
    return f"![{label} {message}](https://img.shields.io/badge/{quote(label, safe='')}-{quote(str(message), safe='')}-{color})"


def short_venue(venue):
    venue = venue or "Unknown"
    if venue in VENUE_SHORT:
        return VENUE_SHORT[venue]
    # Keep common acronym-style venues compact; otherwise use first 28 chars.
    if re.fullmatch(r"[A-Z][A-Z0-9+&./ -]{2,24}", venue):
        return venue.replace(" ", "_")
    return venue.replace(" ", "_")[:28]


def venue_badge(row):
    venue = row.get("venue") or row.get("fallback_venue") or "Unknown"
    year = row.get("year") or row.get("fallback_year") or ""
    vshort = short_venue(venue)
    color = COLOR["arxiv"] if vshort.lower() == "arxiv" or venue == "CoRR" else COLOR["venue"]
    if venue == "CoRR":
        vshort = "arXiv"
    return badge(vshort, year, color)


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


def tag_badges(row):
    tags = row.get("tags") or []
    mods = infer_modality(tags)
    labels = [row.get("usage", "Training_Free")] + [t for t in tags if t not in mods]
    rendered = []
    for label in labels[:5]:
        color = COLOR["usage"] if label in {"Training_Free", "Retrain"} else COLOR["method"]
        rendered.append(badge(label, color=color))
    return "<br> ".join(rendered)


def modality_badges(row):
    tags = row.get("tags") or []
    rendered = []
    for label in infer_modality(tags):
        if label == "Software":
            color = COLOR["software"]
        elif label in {"Theory", "Survey"}:
            color = COLOR["theory"] if label == "Theory" else COLOR["survey"]
        else:
            color = COLOR["modality"]
        rendered.append(badge(label, color=color))
    return " ".join(rendered)


def row_year(row):
    try:
        return int(row.get("year") or row.get("fallback_year") or 0)
    except Exception:
        return 0


def build():
    meta = json.loads(META_JSON.read_text(encoding="utf-8"))
    rows = meta["rows"]
    rows = sorted(rows, key=lambda r: (row_year(r), -int(r.get("ref_id", 9999))), reverse=True)

    out = [
        "# Awesome Manifold Machine Learning",
        "",
        "A curated paper table for manifold learning and manifold-based machine learning methods, generated from the references of:",
        "",
        "- [A survey of manifold learning and its applications for multimedia](https://arxiv.org/abs/2310.12986)",
        "",
        "## Tag Description",
        "",
        "- ![Venue](https://img.shields.io/badge/Venue-blue) conference, journal, book, technical report, or arXiv source.",
        "- ![Modality](https://img.shields.io/badge/-Image-purple) modality or domain tag.",
        "- ![Training Free](https://img.shields.io/badge/-Training_Free-yellowgreen) method does not require training a new model in the cited use case.",
        "- ![Retrain](https://img.shields.io/badge/-Retrain-yellowgreen) method trains or retrains a model/representation.",
        "- ![Method](https://img.shields.io/badge/-Optimization-lightgrey) method or topic tag.",
        "",
        "## Paper Table",
        "",
        "| **Title & Authors * Institute** | **Date** | **Links** | **Modality & Position** | **Tags** |",
        "| --- | --- | --- | --- | :---: |",
    ]

    for row in rows:
        title = clean_text(row.get("title"))
        link = row.get("url") or f"https://www.semanticscholar.org/search?q={quote(title)}&sort=relevance"
        authors = clean_text(row.get("authors") or "Authors unavailable")
        institutes = clean_text(row.get("institutions") or "Institute unavailable")
        title_cell = (
            f"{venue_badge(row)}<br>"
            f"[{title}]({link})<br>"
            f"{authors}<br>"
            f"*Institute:* {institutes}"
        )
        date_cell = str(row_year(row)) if row_year(row) else "-"
        links_cell = f"[Paper]({link})" if row.get("url") else f"[Search]({link})"
        out.append(
            f"| {title_cell} | {date_cell} | {links_cell} | {modality_badges(row)} | {tag_badges(row)} |"
        )

    out.extend(
        [
            "",
            "## Notes",
            "",
            "- Papers are sorted by year in descending order, so the newest papers appear first.",
            "- Author institutions are searched via OpenAlex when available. `Institute unavailable` means no stable institution metadata was returned.",
            "- Venue/year metadata is searched via Semantic Scholar when available, with the source survey references used as fallback.",
        ]
    )
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    build()
