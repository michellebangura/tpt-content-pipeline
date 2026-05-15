import os
import re
import sys
import json
import time
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing dependencies...")
    os.system(sys.executable + " -m pip install requests beautifulsoup4 lxml --quiet")
    import requests
    from bs4 import BeautifulSoup

os.makedirs("data", exist_ok=True)
SCRAPE_DATE = datetime.now().strftime("%Y-%m-%d")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
    "Connection": "keep-alive",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

SEARCH_TARGETS = [
    {
        "category": "Science",
        "urls": [
            "https://www.teacherspayteachers.com/browse?subject[]=Science&order=Rating&page={page}",
            "https://www.teacherspayteachers.com/browse?subject[]=Science&order=Relevance&page={page}",
        ]
    },
    {
        "category": "Math",
        "urls": [
            "https://www.teacherspayteachers.com/browse?subject[]=Math&order=Rating&page={page}",
            "https://www.teacherspayteachers.com/browse?subject[]=Math&order=Relevance&page={page}",
        ]
    },
    {
        "category": "ELA",
        "urls": [
            "https://www.teacherspayteachers.com/browse?subject[]=English+Language+Arts&order=Rating&page={page}",
        ]
    },
    {
        "category": "Social Studies",
        "urls": [
            "https://www.teacherspayteachers.com/browse?subject[]=Social+Studies+-+History&order=Rating&page={page}",
        ]
    },
    {
        "category": "Special Education",
        "urls": [
            "https://www.teacherspayteachers.com/browse?subject[]=Special+Education&order=Rating&page={page}",
            "https://www.teacherspayteachers.com/browse?subject[]=Special+Education&order=Relevance&page={page}",
        ]
    },
    {
        "category": "Life Skills",
        "urls": [
            "https://www.teacherspayteachers.com/browse?subject[]=Life+Skills&order=Rating&page={page}",
        ]
    },
    {
        "category": "SEL",
        "urls": [
            "https://www.teacherspayteachers.com/browse?subject[]=Social+Emotional+Learning&order=Rating&page={page}",
        ]
    },
    {
        "category": "_high_price",
        "urls": [
            "https://www.teacherspayteachers.com/browse?price[]=paid&order=Price-High&page={page}",
        ]
    },
    {
        "category": "_grades_3_to_8",
        "urls": [
            "https://www.teacherspayteachers.com/browse?grade_levels[]=3&grade_levels[]=4&grade_levels[]=5&grade_levels[]=6&grade_levels[]=7&grade_levels[]=8&order=Rating&page={page}",
        ]
    },
]


def get_text_safe(el, sep=" "):
    if el is None:
        return ""
    return el.get_text(separator=sep, strip=True)


def parse_price(text):
    m = re.search(r"[\d.]+", text or "")
    return float(m.group()) if m else 0.0


def parse_reviews(text):
    m = re.search(r"[\d,]+", text or "")
    return int(m.group().replace(",", "")) if m else 0


def parse_rating(el):
    if el is None:
        return None
    aria = el.get("aria-label", "")
    m = re.search(r"([\d.]+)\s*(out of|star|/)", aria)
    if not m:
        m = re.search(r"([\d.]+)", get_text_safe(el))
    return float(m.group(1)) if m else None


def priority(review_count, price, rating):
    rc = min(review_count, 10000) * 0.4
    pr = min(price * 10, 100) * 0.3
    gp = (5.0 - (rating or 4.5)) * 20 * 0.3
    return round(rc + pr + gp, 2)


def extract_cards(html, category, source_url):
    soup = BeautifulSoup(html, "html.parser")
    products = []

    card_selectors = [
        '[data-testid="product-card"]',
        ".ProductRowCard",
        '[class*="ProductCard"]',
        '[class*="product-card"]',
        'li[class*="Card"]',
    ]

    cards = []
    for sel in card_selectors:
        cards = soup.select(sel)
        if cards:
            break

    if not cards:
        links = soup.find_all("a", href=re.compile(r"/Product/"))
        seen = set()
        for lnk in links:
            href = lnk.get("href", "")
            if href not in seen and "/Product/" in href:
                seen.add(href)
                parent = lnk.find_parent("div")
                cards.append(parent if parent else lnk)

    for card in cards:
        try:
            title_el = (
                card.select_one('[data-testid="product-title"]')
                or card.select_one("h2")
                or card.select_one("h3")
                or card.find("a", href=re.compile(r"/Product/"))
            )
            title = get_text_safe(title_el)
            if not title:
                continue

            link_el = card.find("a", href=re.compile(r"/Product/"))
            if not link_el:
                continue
            href = link_el.get("href", "")
            url = href if href.startswith("http") else "https://www.teacherspayteachers.com" + href
            if not url:
                continue

            price_el = (
                card.select_one('[data-testid="price"]')
                or card.select_one('[class*="price"]')
                or card.select_one('[class*="Price"]')
            )
            price_text = get_text_safe(price_el)
            price = parse_price(price_text)
            is_free = "free" in price_text.lower() or price == 0.0

            rating_el = (
                card.select_one('[aria-label*="stars"]')
                or card.select_one('[class*="rating"]')
                or card.select_one('[class*="Rating"]')
            )
            rating = parse_rating(rating_el)

            review_el = (
                card.select_one('[data-testid="review-count"]')
                or card.select_one('[class*="review"]')
            )
            review_count = parse_reviews(get_text_safe(review_el))

            grade_el = (
                card.select_one('[data-testid="grade-levels"]')
                or card.select_one('[class*="grade"]')
            )
            grade_band = get_text_safe(grade_el)

            creator_el = (
                card.select_one('[data-testid="author"]')
                or card.select_one('[class*="author"]')
                or card.select_one('[class*="seller"]')
            )
            creator_name = get_text_safe(creator_el)

            desc_el = card.select_one("p")
            description_preview = get_text_safe(desc_el)[:300]

            products.append({
                "title": title,
                "tpt_url": url,
                "creator_name": creator_name,
                "price": price,
                "is_free": is_free,
                "rating": rating,
                "review_count": review_count,
                "grade_band": grade_band,
                "subject": category,
                "description_preview": description_preview,
                "full_description": None,
                "what_is_included": None,
                "learning_objectives": None,
                "standards": None,
                "preview_bullets": [],
                "page_image_urls": [],
                "priority_score": priority(review_count, price, rating),
                "bright_standard_score": None,
                "certified": False,
                "bs_lesson_id": None,
                "scrape_date": SCRAPE_DATE,
                "source_url": source_url,
                "detail_scraped": False,
                "is_kombra_care": False,
                "kombra_care_tags": [],
                "kombra_care_priority": 0,
            })
        except Exception:
            continue

    return products


def scrape_detail(url):
    try:
        resp = SESSION.get(url, timeout=25)
        if resp.status_code == 429:
            time.sleep(60)
            resp = SESSION.get(url, timeout=25)
        if resp.status_code != 200:
            return {"detail_scraped": True}

        soup = BeautifulSoup(resp.text, "html.parser")

        full_desc = ""
        for sel in ['[data-testid="product-description"]', '[class*="ProductDescription"]', ".description"]:
            el = soup.select_one(sel)
            if el:
                full_desc = get_text_safe(el)[:3000]
                break

        included = ""
        for hdr in soup.find_all(["h2", "h3", "h4", "strong"]):
            if re.search(r"includ", get_text_safe(hdr), re.I):
                sib = hdr.find_next_sibling()
                if sib:
                    included = get_text_safe(sib)[:1500]
                break

        objectives = ""
        for hdr in soup.find_all(["h2", "h3", "h4", "strong"]):
            if re.search(r"objective|student.*will|learn", get_text_safe(hdr), re.I):
                sib = hdr.find_next_sibling()
                if sib:
                    objectives = get_text_safe(sib)[:1000]
                break

        std_pat = re.compile(r"\b(CCSS|NGSS|TEKS|CCSS\.ELA|CCSS\.MATH|MS-|HS-)[\w.\-]+\b")
        standards = list(set(std_pat.findall(soup.get_text())))[:20]

        bullets = []
        for li in soup.find_all("li")[:30]:
            txt = get_text_safe(li)
            if 10 < len(txt) < 200:
                bullets.append(txt)

        creator_link = soup.find("a", href=re.compile(r"/Store/"))
        creator_store_url = ""
        if creator_link:
            href = creator_link.get("href", "")
            creator_store_url = href if href.startswith("http") else "https://www.teacherspayteachers.com" + href

        return {
            "full_description": full_desc,
            "what_is_included": included,
            "learning_objectives": objectives,
            "standards": ", ".join(standards),
            "preview_bullets": bullets[:10],
            "creator_store_url": creator_store_url,
            "detail_scraped": True,
        }
    except Exception as e:
        print("    detail error: " + str(e))
        return {"detail_scraped": True}


KOMBRA_KEYWORDS = [
    "autism", "asd", "autistic", "sensory", "adhd", "iep", "504",
    "special needs", "learning disability", "dyslexia", "social skills",
    "emotional regulation", "executive function", "daily living",
    "life skills", "nonverbal", "aac", "visual schedule", "visual support",
    "token board", "behavior support", "trauma-informed", "differentiated",
    "accommodations", "resource room",
]


def flag_kombra(product):
    text = " ".join([
        product.get("title", ""),
        product.get("description_preview", ""),
        product.get("full_description", "") or "",
        product.get("subject", ""),
    ]).lower()
    tags = [kw for kw in KOMBRA_KEYWORDS if kw in text]
    kp = 0.0
    if tags:
        kp = round(
            product.get("price", 0) * 15
            + min(product.get("review_count", 0), 5000) * 0.5
            + (5.0 - (product.get("rating") or 4.5)) * 25,
            2
        )
    product["is_kombra_care"] = bool(tags)
    product["kombra_care_tags"] = tags
    product["kombra_care_priority"] = kp


# ── TASK 1: Search scrape ───────────────────────────────────────────

checkpoint = "data/tpt_products_raw.json"
if os.path.exists(checkpoint):
    print("Loading existing checkpoint: " + checkpoint)
    with open(checkpoint) as f:
        all_products = json.load(f)
    seen_urls = set(p["tpt_url"] for p in all_products)
else:
    all_products = []
    seen_urls = set()

print("Starting search scrape. Already have: " + str(len(all_products)) + " products")

for target in SEARCH_TARGETS:
    category = target["category"]
    print("")
    print("Category: " + category)
    for url_template in target["urls"]:
        for page in range(1, 4):
            url = url_template.format(page=page)
            try:
                print("  GET " + url[:80])
                resp = SESSION.get(url, timeout=20)
                if resp.status_code == 429:
                    print("  Rate limited - sleeping 45s")
                    time.sleep(45)
                    resp = SESSION.get(url, timeout=20)
                if resp.status_code != 200:
                    print("  Skip HTTP " + str(resp.status_code))
                    time.sleep(3)
                    continue
                cards = extract_cards(resp.text, category, url)
                new_count = 0
                for p in cards:
                    if p["tpt_url"] and p["tpt_url"] not in seen_urls:
                        seen_urls.add(p["tpt_url"])
                        all_products.append(p)
                        new_count += 1
                print("  found=" + str(len(cards)) + " new=" + str(new_count) + " total=" + str(len(all_products)))
                time.sleep(2.5)
            except Exception as e:
                print("  error: " + str(e))
                time.sleep(5)

with open(checkpoint, "w") as f:
    json.dump(all_products, f, indent=2)
print("")
print("TASK 1 DONE: " + str(len(all_products)) + " products")

# ── TASK 2: Detail scrape top 100 ─────────────────────────────────

sorted_all = sorted(all_products, key=lambda p: p["priority_score"], reverse=True)
to_detail = [p for p in sorted_all if not p.get("detail_scraped")][:100]
url_index = {p["tpt_url"]: i for i, p in enumerate(all_products)}

print("Detail scraping " + str(len(to_detail)) + " products...")

for i, product in enumerate(to_detail):
    print("  [" + str(i+1) + "/" + str(len(to_detail)) + "] " + product["title"][:50])
    details = scrape_detail(product["tpt_url"])
    idx = url_index.get(product["tpt_url"])
    if idx is not None:
        all_products[idx].update(details)
    if (i + 1) % 10 == 0:
        with open(checkpoint, "w") as f:
            json.dump(all_products, f, indent=2)
        print("  checkpoint saved")
    time.sleep(3)

with open(checkpoint, "w") as f:
    json.dump(all_products, f, indent=2)
print("TASK 2 DONE")

# ── TASK 3: Clean + output ─────────────────────────────────────────

seen = set()
deduped = []
for p in all_products:
    url = p.get("tpt_url", "")
    if url and url not in seen:
        seen.add(url)
        deduped.append(p)

SUBJECT_MAP = {"_high_price": "Mixed", "_high_reviews": "Mixed", "_grades_3_to_8": "Mixed"}
for p in deduped:
    p["subject"] = SUBJECT_MAP.get(p["subject"], p["subject"])
    p["priority_score"] = priority(p.get("review_count", 0), p.get("price", 0), p.get("rating"))
    flag_kombra(p)

sorted_priority = sorted(deduped, key=lambda p: p["priority_score"], reverse=True)
sorted_reviews = sorted(deduped, key=lambda p: p.get("review_count", 0), reverse=True)
kombra_targets = sorted([p for p in deduped if p["is_kombra_care"]], key=lambda p: p["kombra_care_priority"], reverse=True)
priority_paid = [p for p in sorted_priority if not p.get("is_free")][:50]

creator_map = {}
for p in deduped:
    cn = p.get("creator_name", "").strip()
    if not cn:
        continue
    if cn not in creator_map:
        creator_map[cn] = {
            "creator_name": cn,
            "tpt_store_url": p.get("creator_store_url", ""),
            "products": [],
            "total_reviews": 0,
            "subjects": [],
        }
    creator_map[cn]["products"].append({
        "title": p.get("title", ""),
        "tpt_url": p.get("tpt_url", ""),
        "price": p.get("price", 0),
        "rating": p.get("rating"),
        "review_count": p.get("review_count", 0),
        "priority_score": p.get("priority_score", 0),
    })
    creator_map[cn]["total_reviews"] += p.get("review_count", 0)
    subj = p.get("subject", "")
    if subj and subj not in creator_map[cn]["subjects"]:
        creator_map[cn]["subjects"].append(subj)

for cn, cr in creator_map.items():
    cr["product_count"] = len(cr["products"])
    cr["outreach_priority"] = "high" if cr["total_reviews"] > 2000 else "medium" if cr["total_reviews"] > 500 else "low"
    cr["worst_product"] = min(cr["products"], key=lambda p: p.get("rating") or 5)

creators_sorted = sorted(creator_map.values(), key=lambda c: c["total_reviews"], reverse=True)

subject_stats = {}
for p in deduped:
    s = p.get("subject", "Unknown")
    if s not in subject_stats:
        subject_stats[s] = {"subject": s, "product_count": 0, "total_reviews": 0, "prices": [], "ratings": []}
    subject_stats[s]["product_count"] += 1
    subject_stats[s]["total_reviews"] += p.get("review_count", 0)
    if p.get("price"):
        subject_stats[s]["prices"].append(p["price"])
    if p.get("rating"):
        subject_stats[s]["ratings"].append(p["rating"])

for s, st in subject_stats.items():
    st["avg_price"] = round(sum(st["prices"]) / len(st["prices"]), 2) if st["prices"] else 0
    st["avg_rating"] = round(sum(st["ratings"]) / len(st["ratings"]), 2) if st["ratings"] else 0
    del st["prices"]
    del st["ratings"]

with open("data/tpt_products.json", "w") as f:
    json.dump(sorted_priority, f, indent=2)
with open("data/tpt_priority_targets.json", "w") as f:
    json.dump(priority_paid, f, indent=2)
with open("data/tpt_kombra_care_targets.json", "w") as f:
    json.dump(kombra_targets, f, indent=2)
with open("data/tpt_creator_outreach_list.json", "w") as f:
    json.dump(creators_sorted, f, indent=2)
with open("data/tpt_subject_analytics.json", "w") as f:
    json.dump(list(subject_stats.values()), f, indent=2)

summary = {
    "scrape_date": SCRAPE_DATE,
    "total_products": len(deduped),
    "paid_products": sum(1 for p in deduped if not p.get("is_free")),
    "free_products": sum(1 for p in deduped if p.get("is_free")),
    "total_reviews": sum(p.get("review_count", 0) for p in deduped),
    "kombra_care_count": len(kombra_targets),
    "unique_creators": len(creator_map),
    "high_priority_creators": sum(1 for c in creators_sorted if c["outreach_priority"] == "high"),
    "top_10_priority": [{"title": p.get("title","")[:60], "price": p.get("price",0), "rating": p.get("rating"), "reviews": p.get("review_count",0), "priority": p.get("priority_score",0), "url": p.get("tpt_url","")} for p in sorted_priority[:10]],
    "top_10_reviews": [{"title": p.get("title","")[:60], "reviews": p.get("review_count",0), "price": p.get("price",0), "url": p.get("tpt_url","")} for p in sorted_reviews[:10]],
    "kombra_top_5": [{"title": p.get("title","")[:60], "tags": p.get("kombra_care_tags",[])[:4], "reviews": p.get("review_count",0), "price": p.get("price",0)} for p in kombra_targets[:5]],
    "subject_breakdown": subject_stats,
}

with open("data/tpt_market_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# ── TASK 4: Report ─────────────────────────────────────────────────

print("")
print("=" * 60)
print("TPT MARKET INTELLIGENCE REPORT")
print("=" * 60)
print("Date:            " + summary["scrape_date"])
print("Total products:  " + str(summary["total_products"]))
print("Paid:            " + str(summary["paid_products"]))
print("Free:            " + str(summary["free_products"]))
print("Total reviews:   " + str(summary["total_reviews"]))
print("Kombra Care:     " + str(summary["kombra_care_count"]))
print("Unique creators: " + str(summary["unique_creators"]))
print("High priority:   " + str(summary["high_priority_creators"]) + " creators (2000+ reviews)")
print("")
print("-- TOP 10 BY PRIORITY --")
for i, p in enumerate(summary["top_10_priority"], 1):
    print(str(i) + ". " + p["title"][:45] + " | $" + str(p["price"]) + " | " + str(p["rating"]) + " stars | " + str(p["reviews"]) + " reviews")
print("")
print("-- TOP 5 KOMBRA CARE --")
for i, p in enumerate(summary["kombra_top_5"], 1):
    print(str(i) + ". " + p["title"][:50])
    print("   tags: " + ", ".join(p["tags"][:4]))
    print("   " + str(p["reviews"]) + " reviews | $" + str(p["price"]))
print("")
print("-- SUBJECT BREAKDOWN --")
for s in sorted(subject_stats.values(), key=lambda x: x["total_reviews"], reverse=True):
    print("  " + s["subject"][:24].ljust(25) + " " + str(s["product_count"]) + " products | avg $" + str(s["avg_price"]) + " | avg " + str(s["avg_rating"]) + " stars | " + str(s["total_reviews"]) + " reviews")
print("")
print("-- OUTPUT FILES --")
for fname in ["data/tpt_products.json", "data/tpt_priority_targets.json", "data/tpt_kombra_care_targets.json", "data/tpt_creator_outreach_list.json", "data/tpt_subject_analytics.json", "data/tpt_market_summary.json"]:
    print("  " + fname)
print("=" * 60)
