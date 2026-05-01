import json
import re
from html import unescape
from pathlib import Path


ROOT = Path(r"E:\_WORK_\form-n-space\website")
CRAWL_ROOT = ROOT / "formnspaceimphal.com"
CATEGORY_FILE = CRAWL_ROOT / "category" / "projects" / "projects.html"
OUTPUT_FILE = ROOT / "app" / "src" / "data" / "portfolio-projects.json"


def clean_text(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def map_type(tags):
    tag_blob = " ".join(tags).lower()
    if "residence" in tag_blob:
        return "Residential"
    if any(token in tag_blob for token in ["hotel", "office", "restaurant", "school", "commercial", "hall"]):
        return "Commercial"
    if any(token in tag_blob for token in ["interior", "renovation", "kitchen"]):
        return "Interiors"
    if any(token in tag_blob for token in ["landscaping", "township", "layout", "urban", "planning"]):
        return "Planning"
    return "Residential"


def extract_listing(html: str):
    pattern = re.compile(
        r'<article class="(?P<class>[^"]*?)entry"[^>]*aria-label="(?P<label>[^"]+)"[^>]*>.*?'
        r'<a class="entry-title-link"[^>]*href="(?P<href>[^"]+)"[^>]*><span>(?P<title>.*?)</span></a>.*?'
        r'<img[^>]*src="(?P<img>[^"]+)"',
        re.S,
    )
    items = []
    for match in pattern.finditer(html):
        classes = match.group("class")
        tags = re.findall(r"\btag-([a-z0-9-]+)\b", classes)
        href = match.group("href")
        slug = href.strip("/").split("/")[-2] if href.endswith(".html") else href.strip("/").split("/")[-1]
        items.append(
            {
                "slug": slug,
                "title": clean_text(match.group("title")),
                "legacyLabel": clean_text(match.group("label")),
                "thumbnail": match.group("img").replace("../../", "https://formnspaceimphal.com/"),
                "tags": tags,
                "type": map_type(tags),
            }
        )
    return items


def extract_detail(slug: str):
    detail_file = CRAWL_ROOT / slug / f"{slug}.html"
    if not detail_file.exists():
        return None

    html = detail_file.read_text(encoding="utf-8", errors="ignore")

    title_match = re.search(r'<h1 class="entry-title">([^<]+)</h1>', html)
    location_match = re.search(r"<p>([^<]*Manipur[^<]*)</p>", html)
    area_match = re.search(r"<p>([^<]*sqft[^<]*)</p>", html, re.I)
    body_match = re.search(r"<p>([^<]{80,})</p>", html)
    og_desc_match = re.search(r'<meta name="description" content="([^"]+)"', html)

    image_urls = []
    for image_match in re.finditer(
        r'n2-ss-slide-background-image[^>]*>.*?<img[^>]*src="([^"]+)"',
        html,
        re.S,
    ):
        src = image_match.group(1).replace("../", "https://formnspaceimphal.com/")
        if src not in image_urls:
            image_urls.append(src)
    if not image_urls:
        for image_match in re.finditer(r'<img[^>]*src="([^"]+)"', html):
            src = image_match.group(1)
            if "wp-content/uploads" in src:
                full = src if src.startswith("http") else src.replace("../", "https://formnspaceimphal.com/")
                if full not in image_urls:
                    image_urls.append(full)

    description = clean_text(body_match.group(1)) if body_match else ""
    if not description and og_desc_match:
        description = clean_text(og_desc_match.group(1))

    location = clean_text(location_match.group(1)) if location_match else "North East India"
    area = clean_text(area_match.group(1)) if area_match else ""

    return {
        "title": clean_text(title_match.group(1)) if title_match else slug.replace("-", " ").title(),
        "location": location,
        "area": area,
        "description": description,
        "images": image_urls,
    }


def main():
    html = CATEGORY_FILE.read_text(encoding="utf-8", errors="ignore")
    listing = extract_listing(html)

    projects = []
    for item in listing:
        detail = extract_detail(item["slug"])
        if not detail:
            # Skip items with no detail source page.
            continue
        projects.append(
            {
                "slug": item["slug"],
                "title": detail["title"] or item["title"],
                "type": item["type"],
                "tags": item["tags"],
                "thumbnail": item["thumbnail"],
                "location": detail["location"],
                "area": detail["area"],
                "description": detail["description"],
                "images": detail["images"],
            }
        )

    OUTPUT_FILE.write_text(json.dumps(projects, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(projects)} projects to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
