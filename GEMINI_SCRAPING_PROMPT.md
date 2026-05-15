# GEMINI SCRAPING PROMPT — TPT MARKET INTELLIGENCE
# Paste this into Google AI Studio (aistudio.google.com) with:
# - Model: Gemini 1.5 Pro or Gemini 2.0 Flash
# - Tools: Enable "Code Execution"
# - Grounding: Enable "Google Search" if available
# This is the scraping phase ONLY. Gemini outputs JSON files.
# Those files feed the Haiku Claude Code pipeline for scoring and generation.

=== PROMPT START ===

You are a market intelligence data agent. Your only job is to scrape
Teachers Pay Teachers (teacherspayteachers.com) and produce structured
JSON files. You do not evaluate content quality. You do not generate
lessons. You do not write emails. You collect data and structure it.

Use your code execution environment to write and run Python.
Output files to the current working directory.
After each script runs, print the first 5 rows of output as confirmation.

## WHAT YOU ARE BUILDING

A market intelligence database of TPT's highest-selling, most-reviewed,
highest-priced, and lowest-rated content — across every subject category
relevant to Bright Standard. This data will be used to:

1. Identify which content to compete against directly
2. Find creators to contact about quality improvement
3. Understand what teachers are actually buying and why

---

## SETUP

Run this first:

```python
import subprocess
subprocess.run(['pip', 'install', 'requests', 'beautifulsoup4',
                'pandas', 'lxml', 'html5lib'], capture_output=True)

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse, quote

# Rate-limiting headers — be polite
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

os.makedirs('data', exist_ok=True)

SCRAPE_DATE = datetime.now().strftime('%Y-%m-%d')
print(f"Setup complete. Scrape date: {SCRAPE_DATE}")
```

---

## TASK 1: SCRAPE SEARCH RESULT PAGES

Scrape product listings from these TPT search URLs.
Extract every product card visible on the page.
Paginate to get at least 3 pages per URL (page=1, page=2, page=3).

```python
SEARCH_TARGETS = [
    # Best sellers by subject
    {
        'category': 'Science',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=Science&order=Rating&page={page}',
            'https://www.teacherspayteachers.com/browse?subject[]=Science&order=Relevance&page={page}',
        ]
    },
    {
        'category': 'Math',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=Math&order=Rating&page={page}',
            'https://www.teacherspayteachers.com/browse?subject[]=Math&order=Relevance&page={page}',
        ]
    },
    {
        'category': 'ELA',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=English+Language+Arts&order=Rating&page={page}',
            'https://www.teacherspayteachers.com/browse?subject[]=English+Language+Arts&order=Relevance&page={page}',
        ]
    },
    {
        'category': 'Social Studies',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=Social+Studies+-+History&order=Rating&page={page}',
        ]
    },
    {
        'category': 'Special Education',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=Special+Education&order=Rating&page={page}',
            'https://www.teacherspayteachers.com/browse?subject[]=Special+Education&order=Relevance&page={page}',
        ]
    },
    {
        'category': 'Life Skills',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=Life+Skills&order=Rating&page={page}',
            'https://www.teacherspayteachers.com/browse?subject[]=Life+Skills&order=Relevance&page={page}',
        ]
    },
    {
        'category': 'Social Emotional Learning',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=Social+Emotional+Learning&order=Rating&page={page}',
        ]
    },
    {
        'category': 'Cross-Curricular',
        'urls': [
            'https://www.teacherspayteachers.com/browse?subject[]=Other+(Specialty)&order=Rating&page={page}',
        ]
    },
    # High price — these are the revenue targets
    {
        'category': '_high_price',
        'urls': [
            'https://www.teacherspayteachers.com/browse?price[]=paid&order=Price-High&page={page}',
        ]
    },
    # High review count — these are the market share targets
    {
        'category': '_high_reviews',
        'urls': [
            'https://www.teacherspayteachers.com/browse?price[]=paid&order=Most-Recent&page={page}',
            'https://www.teacherspayteachers.com/browse?order=Relevance&page={page}',
        ]
    },
    # Grade-specific targets for Grades 3-8 (Bright Standard sweet spot)
    {
        'category': '_grades_3_to_8',
        'urls': [
            'https://www.teacherspayteachers.com/browse?grade_levels[]=3&grade_levels[]=4&grade_levels[]=5&grade_levels[]=6&grade_levels[]=7&grade_levels[]=8&order=Rating&page={page}',
        ]
    },
]


def extract_products_from_page(html, category, source_url):
    """Extract product cards from a TPT search results page."""
    soup = BeautifulSoup(html, 'html.parser')
    products = []

    # TPT uses several possible card selectors depending on page variant
    card_selectors = [
        '[data-testid="product-card"]',
        '.ProductRowCard',
        '[class*="ProductCard"]',
        '[class*="product-card"]',
        'li[class*="Card"]',
        'div[class*="Card"] a[href*="/Product/"]',
    ]

    cards = []
    for sel in card_selectors:
        cards = soup.select(sel)
        if cards:
            break

    # Fallback: find all links to /Product/ pages
    if not cards:
        product_links = soup.find_all('a', href=re.compile(r'/Product/'))
        seen_hrefs = set()
        for link in product_links:
            href = link.get('href', '')
            if href not in seen_hrefs and '/Product/' in href:
                seen_hrefs.add(href)
                cards.append(link.find_parent('div') or link)

    for card in cards:
        try:
            # Title
            title_el = (card.select_one('[data-testid="product-title"]') or
                        card.select_one('[class*="title"]') or
                        card.select_one('h2') or
                        card.select_one('h3') or
                        card.find('a', href=re.compile(r'/Product/')))
            title = title_el.get_text(strip=True) if title_el else ''

            # URL
            link_el = card.find('a', href=re.compile(r'/Product/'))
            url = ''
            if link_el:
                href = link_el.get('href', '')
                url = href if href.startswith('http') else f'https://www.teacherspayteachers.com{href}'

            if not url or not title:
                continue

            # Price
            price_text = ''
            price_el = (card.select_one('[data-testid="price"]') or
                        card.select_one('[class*="price"]') or
                        card.select_one('[class*="Price"]'))
            if price_el:
                price_text = price_el.get_text(strip=True)
            price_match = re.search(r'\$?([\d.]+)', price_text)
            price = float(price_match.group(1)) if price_match else 0.0
            is_free = 'free' in price_text.lower() or price == 0.0

            # Rating
            rating = None
            rating_el = (card.select_one('[aria-label*="stars"]') or
                         card.select_one('[class*="rating"]') or
                         card.select_one('[class*="Rating"]') or
                         card.select_one('[class*="star"]'))
            if rating_el:
                aria = rating_el.get('aria-label', '')
                rating_match = re.search(r'([\d.]+)\s*(out of|star|/)', aria)
                if not rating_match:
                    rating_match = re.search(r'([\d.]+)', rating_el.get_text())
                if rating_match:
                    rating = float(rating_match.group(1))

            # Review count
            review_count = 0
            review_el = (card.select_one('[data-testid="review-count"]') or
                         card.select_one('[class*="review"]') or
                         card.select_one('[class*="Review"]'))
            if review_el:
                review_text = review_el.get_text(strip=True)
                review_match = re.search(r'([\d,]+)', review_text)
                if review_match:
                    review_count = int(review_match.group(1).replace(',', ''))

            # Grade levels
            grade_el = (card.select_one('[data-testid="grade-levels"]') or
                        card.select_one('[class*="grade"]') or
                        card.select_one('[class*="Grade"]'))
            grade_band = grade_el.get_text(strip=True) if grade_el else ''

            # Creator name
            creator_el = (card.select_one('[data-testid="author"]') or
                          card.select_one('[class*="author"]') or
                          card.select_one('[class*="Author"]') or
                          card.select_one('[class*="seller"]'))
            creator_name = creator_el.get_text(strip=True) if creator_el else ''

            # Description preview (first visible text block after title)
            desc_el = (card.select_one('[data-testid="description"]') or
                       card.select_one('[class*="description"]') or
                       card.select_one('p'))
            description_preview = desc_el.get_text(strip=True)[:300] if desc_el else ''

            # Resource type
            type_el = (card.select_one('[data-testid="resource-type"]') or
                       card.select_one('[class*="resource-type"]'))
            resource_type = type_el.get_text(strip=True) if type_el else ''

            # Compute priority score
            # Weights: review count (market size) + price (revenue opp) + inverse rating (quality gap)
            review_score   = min(review_count, 10000) * 0.4
            price_score    = min(price * 10, 100) * 0.3
            gap_score      = ((5.0 - (rating or 4.5)) * 20) * 0.3
            priority_score = round(review_score + price_score + gap_score, 2)

            products.append({
                'title':               title,
                'tpt_url':             url,
                'creator_name':        creator_name,
                'price':               price,
                'is_free':             is_free,
                'rating':              rating,
                'review_count':        review_count,
                'grade_band':          grade_band,
                'subject':             category,
                'resource_type':       resource_type,
                'description_preview': description_preview,
                'full_description':    None,  # filled in Task 2
                'what_is_included':    None,
                'learning_objectives': None,
                'standards':           None,
                'preview_bullets':     None,
                'page_image_urls':     [],
                'priority_score':      priority_score,
                'bright_standard_score': None,
                'certified':           False,
                'bs_lesson_id':        None,
                'scrape_date':         SCRAPE_DATE,
                'source_url':          source_url,
                'detail_scraped':      False,
            })

        except Exception as e:
            continue

    return products


all_products = []
seen_urls = set()

for target in SEARCH_TARGETS:
    category = target['category']
    print(f"\nScraping category: {category}")

    for url_template in target['urls']:
        for page in range(1, 4):  # Pages 1, 2, 3
            url = url_template.format(page=page)
            try:
                print(f"  GET {url[:80]}...")
                resp = SESSION.get(url, timeout=20)
                if resp.status_code == 429:
                    print("  Rate limited — sleeping 45s")
                    time.sleep(45)
                    resp = SESSION.get(url, timeout=20)
                if resp.status_code != 200:
                    print(f"  Skip: HTTP {resp.status_code}")
                    time.sleep(3)
                    continue

                products = extract_products_from_page(resp.text, category, url)
                new = 0
                for p in products:
                    if p['tpt_url'] and p['tpt_url'] not in seen_urls:
                        seen_urls.add(p['tpt_url'])
                        all_products.append(p)
                        new += 1

                print(f"  Found {len(products)} products, {new} new. Total: {len(all_products)}")
                time.sleep(2.5)

            except Exception as e:
                print(f"  Error: {e}")
                time.sleep(5)

print(f"\n=== TASK 1 COMPLETE: {len(all_products)} unique products scraped ===")

# Save checkpoint
with open('data/tpt_products_raw.json', 'w') as f:
    json.dump(all_products, f, indent=2)
print("Saved: data/tpt_products_raw.json")

# Show first 5
print("\nSample (first 5):")
for p in all_products[:5]:
    print(f"  [{p['subject']}] {p['title'][:50]} | ${p['price']} | ⭐{p['rating']} | {p['review_count']} reviews | priority:{p['priority_score']}")
```

---

## TASK 2: SCRAPE PRODUCT DETAIL PAGES

For the top 100 products by priority_score, click through to the
product detail page and extract the full content.

```python
# Load products (in case resuming)
with open('data/tpt_products_raw.json') as f:
    all_products = json.load(f)

# Sort by priority score, take top 100 that haven't been detail-scraped yet
sorted_products = sorted(all_products, key=lambda p: p['priority_score'], reverse=True)
to_detail = [p for p in sorted_products if not p.get('detail_scraped')][:100]

print(f"Detail scraping top {len(to_detail)} products...")


def scrape_product_detail(url):
    """Scrape a single TPT product detail page."""
    try:
        resp = SESSION.get(url, timeout=25)
        if resp.status_code == 429:
            time.sleep(60)
            resp = SESSION.get(url, timeout=25)
        if resp.status_code != 200:
            return {}

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Full description
        desc_selectors = [
            '[data-testid="product-description"]',
            '[class*="ProductDescription"]',
            '[class*="description-content"]',
            '.description',
            '#description',
        ]
        full_description = ''
        for sel in desc_selectors:
            el = soup.select_one(sel)
            if el:
                full_description = el.get_text(separator='\n', strip=True)[:3000]
                break

        # What's included
        included = ''
        for header in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b']):
            if re.search(r"what.*includ|includ.*what", header.get_text(), re.I):
                sibling = header.find_next_sibling()
                if sibling:
                    included = sibling.get_text(separator='\n', strip=True)[:1500]
                break

        # Learning objectives / what students will learn
        objectives = ''
        for header in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b']):
            if re.search(r"objective|student.*will|learn|outcome|standard", header.get_text(), re.I):
                sibling = header.find_next_sibling()
                if sibling:
                    objectives = sibling.get_text(separator='\n', strip=True)[:1000]
                break

        # Standards — look for CCSS, NGSS, TEKS, etc.
        standards = []
        std_pattern = re.compile(
            r'\b(CCSS|NGSS|TEKS|RL|RI|W|SL|L|RF|MP|NBT|OA|MD|G|NF|NS|EE|SP|F|'
            r'K-ESS|K-LS|K-PS|1-ESS|2-ESS|3-LS|4-ESS|4-PS|5-PS|5-LS|5-ESS|'
            r'MS-|HS-)[\w.-]+\b'
        )
        for match in std_pattern.finditer(soup.get_text()):
            if match.group() not in standards:
                standards.append(match.group())

        # All bullet points (learning indicators)
        bullets = []
        for li in soup.find_all('li')[:30]:
            text = li.get_text(strip=True)
            if 10 < len(text) < 200:
                bullets.append(text)

        # Creator store URL
        creator_link = (soup.select_one('[data-testid="author-link"]') or
                        soup.find('a', href=re.compile(r'/Store/')))
        creator_store_url = ''
        if creator_link:
            href = creator_link.get('href', '')
            creator_store_url = href if href.startswith('http') else f'https://www.teacherspayteachers.com{href}'

        # Preview image URLs
        img_urls = []
        for img in soup.select('[data-testid="preview-image"], [class*="preview"] img')[:5]:
            src = img.get('src') or img.get('data-src', '')
            if src and src.startswith('http'):
                img_urls.append(src)

        # Grade levels (more detailed from product page)
        grade_text = ''
        grade_el = (soup.select_one('[data-testid="grade-levels"]') or
                    soup.find(text=re.compile(r'Grade Levels?:', re.I)))
        if grade_el:
            if hasattr(grade_el, 'get_text'):
                grade_text = grade_el.get_text(strip=True)
            else:
                parent = grade_el.find_parent()
                if parent:
                    grade_text = parent.get_text(strip=True)[:100]

        # Page count / file type hints
        file_info = ''
        for text in soup.stripped_strings:
            if re.search(r'\d+\s*(page|slide|worksheet|activity|file)', text, re.I):
                file_info = text[:100]
                break

        return {
            'full_description':    full_description,
            'what_is_included':    included,
            'learning_objectives': objectives,
            'standards':           ', '.join(standards[:20]),
            'preview_bullets':     bullets[:10],
            'creator_store_url':   creator_store_url,
            'page_image_urls':     img_urls,
            'grade_band_detail':   grade_text,
            'file_info':           file_info,
            'detail_scraped':      True,
        }

    except Exception as e:
        print(f"    Detail error: {e}")
        return {'detail_scraped': True}


# Build URL index for fast lookup
url_index = {p['tpt_url']: i for i, p in enumerate(all_products)}

for i, product in enumerate(to_detail):
    print(f"  [{i+1}/{len(to_detail)}] {product['title'][:50]}")
    details = scrape_product_detail(product['tpt_url'])

    # Update in main list
    idx = url_index.get(product['tpt_url'])
    if idx is not None:
        all_products[idx].update(details)

    # Save checkpoint every 10 items
    if (i + 1) % 10 == 0:
        with open('data/tpt_products_raw.json', 'w') as f:
            json.dump(all_products, f, indent=2)
        print(f"    Checkpoint saved ({i+1} detail pages done)")

    time.sleep(3)

# Final save
with open('data/tpt_products_raw.json', 'w') as f:
    json.dump(all_products, f, indent=2)

print(f"\n=== TASK 2 COMPLETE ===")
detail_count = sum(1 for p in all_products if p.get('detail_scraped'))
print(f"Products with detail: {detail_count}")
```

---

## TASK 3: BUILD STRUCTURED OUTPUT FILES

Clean the data, deduplicate, compute all derived fields, and produce
the final output files the pipeline needs.

```python
with open('data/tpt_products_raw.json') as f:
    all_products = json.load(f)

# Deduplicate by URL
seen = set()
deduped = []
for p in all_products:
    url = p.get('tpt_url', '')
    if url and url not in seen:
        seen.add(url)
        deduped.append(p)

print(f"Deduplication: {len(all_products)} → {len(deduped)} products")


# ── Normalize subject labels ──────────────────────────────────────────────────
SUBJECT_MAP = {
    '_high_price': 'Mixed',
    '_high_reviews': 'Mixed',
    '_grades_3_to_8': 'Mixed',
}
for p in deduped:
    p['subject'] = SUBJECT_MAP.get(p['subject'], p['subject'])


# ── Recalculate priority score with full data ─────────────────────────────────
for p in deduped:
    rc     = min(p.get('review_count', 0), 10000)
    price  = min(p.get('price', 0) * 10, 100)
    gap    = (5.0 - (p.get('rating') or 4.5)) * 20
    p['priority_score'] = round(rc * 0.4 + price * 0.3 + gap * 0.3, 2)


# ── Identify Kombra Care content ──────────────────────────────────────────────
KOMBRA_CARE_KEYWORDS = [
    'autism', 'asd', 'autistic', 'sensory', 'low sensory', 'sensory-friendly',
    'adhd', 'add', 'attention deficit', 'iep', '504 plan', 'special needs',
    'learning disability', 'dyslexia', 'dyscalculia', 'dysgraphia',
    'social skills', 'emotional regulation', 'executive function',
    'daily living', 'life skills', 'independence skills', 'self-care',
    'nonverbal', 'aac', 'alternative communication', 'picture cards',
    'visual schedule', 'visual support', 'token board', 'behavior support',
    'trauma-informed', 'inclusive', 'differentiated', 'modifications',
    'accommodations', 'resource room', 'self-contained',
]

def is_kombra_care(product):
    text = ' '.join([
        product.get('title', ''),
        product.get('description_preview', ''),
        product.get('full_description', '') or '',
        product.get('subject', ''),
    ]).lower()
    matches = [kw for kw in KOMBRA_CARE_KEYWORDS if kw in text]
    return bool(matches), matches

for p in deduped:
    is_kc, kc_tags = is_kombra_care(p)
    p['is_kombra_care']    = is_kc
    p['kombra_care_tags']  = kc_tags
    p['kombra_care_priority'] = (
        round(p.get('price', 0) * 15 +
              min(p.get('review_count', 0), 5000) * 0.5 +
              (5.0 - (p.get('rating') or 4.5)) * 25, 2)
        if is_kc else 0
    )


# ── Sort ──────────────────────────────────────────────────────────────────────
sorted_by_priority   = sorted(deduped, key=lambda p: p['priority_score'], reverse=True)
sorted_by_reviews    = sorted(deduped, key=lambda p: p.get('review_count', 0), reverse=True)
sorted_by_price      = sorted(deduped, key=lambda p: p.get('price', 0), reverse=True)
kombra_care_targets  = sorted(
    [p for p in deduped if p['is_kombra_care']],
    key=lambda p: p['kombra_care_priority'], reverse=True
)


# ── Creator aggregation ───────────────────────────────────────────────────────
creator_map = {}
for p in deduped:
    cn = p.get('creator_name', '').strip()
    if not cn:
        continue
    if cn not in creator_map:
        creator_map[cn] = {
            'creator_name':          cn,
            'tpt_store_url':         p.get('creator_store_url', ''),
            'products':              [],
            'total_reviews':         0,
            'total_revenue_est':     0.0,
            'avg_rating':            0.0,
            'avg_priority_score':    0.0,
            'subjects':              set(),
            'has_kombra_care':       False,
        }
    creator_map[cn]['products'].append({
        'title':          p.get('title', ''),
        'tpt_url':        p.get('tpt_url', ''),
        'price':          p.get('price', 0),
        'rating':         p.get('rating'),
        'review_count':   p.get('review_count', 0),
        'priority_score': p.get('priority_score', 0),
    })
    creator_map[cn]['total_reviews']    += p.get('review_count', 0)
    creator_map[cn]['total_revenue_est'] += p.get('price', 0) * p.get('review_count', 0) * 0.3  # rough estimate
    if p.get('subject'):
        creator_map[cn]['subjects'].add(p['subject'])
    if p.get('is_kombra_care'):
        creator_map[cn]['has_kombra_care'] = True

for cn, creator in creator_map.items():
    prods   = creator['products']
    ratings = [p['rating'] for p in prods if p.get('rating')]
    scores  = [p['priority_score'] for p in prods]
    creator['avg_rating']          = round(sum(ratings) / len(ratings), 2) if ratings else None
    creator['avg_priority_score']  = round(sum(scores) / len(scores), 2)
    creator['product_count']       = len(prods)
    creator['total_revenue_est']   = round(creator['total_revenue_est'], 2)
    creator['subjects']            = list(creator['subjects'])
    creator['outreach_priority']   = (
        'high'   if creator['total_reviews'] > 2000 else
        'medium' if creator['total_reviews'] > 500  else
        'low'
    )
    # Worst product = lowest combined score
    creator['worst_product'] = min(prods, key=lambda p: (p.get('rating') or 5))

creators_sorted = sorted(
    creator_map.values(),
    key=lambda c: c['total_reviews'],
    reverse=True
)


# ── Subject analytics ─────────────────────────────────────────────────────────
subject_stats = {}
for p in deduped:
    subj = p.get('subject', 'Unknown')
    if subj not in subject_stats:
        subject_stats[subj] = {
            'subject':        subj,
            'product_count':  0,
            'avg_price':      0,
            'avg_rating':     0,
            'total_reviews':  0,
            'avg_priority':   0,
        }
    subject_stats[subj]['product_count']  += 1
    subject_stats[subj]['avg_price']      += p.get('price', 0)
    subject_stats[subj]['total_reviews']  += p.get('review_count', 0)
    if p.get('rating'):
        subject_stats[subj]['avg_rating'] += p['rating']
    subject_stats[subj]['avg_priority']   += p.get('priority_score', 0)

for subj, stats in subject_stats.items():
    n = stats['product_count']
    stats['avg_price']    = round(stats['avg_price'] / n, 2)
    stats['avg_rating']   = round(stats['avg_rating'] / n, 2)
    stats['avg_priority'] = round(stats['avg_priority'] / n, 2)


# ── Write output files ────────────────────────────────────────────────────────

# 1. All products sorted by priority
with open('data/tpt_products.json', 'w') as f:
    json.dump(sorted_by_priority, f, indent=2)
print(f"Saved: data/tpt_products.json ({len(sorted_by_priority)} products)")

# 2. Top 50 priority targets (non-free, most actionable)
priority_paid = [p for p in sorted_by_priority if not p.get('is_free', True)][:50]
with open('data/tpt_priority_targets.json', 'w') as f:
    json.dump(priority_paid, f, indent=2)
print(f"Saved: data/tpt_priority_targets.json ({len(priority_paid)} targets)")

# 3. Kombra Care targets
with open('data/tpt_kombra_care_targets.json', 'w') as f:
    json.dump(kombra_care_targets, f, indent=2)
print(f"Saved: data/tpt_kombra_care_targets.json ({len(kombra_care_targets)} products)")

# 4. Creator outreach list
with open('data/tpt_creator_outreach_list.json', 'w') as f:
    json.dump(creators_sorted, f, indent=2)
print(f"Saved: data/tpt_creator_outreach_list.json ({len(creators_sorted)} creators)")

# 5. Subject analytics
with open('data/tpt_subject_analytics.json', 'w') as f:
    json.dump(list(subject_stats.values()), f, indent=2)
print("Saved: data/tpt_subject_analytics.json")

# 6. Summary report
summary = {
    'scrape_date':            SCRAPE_DATE,
    'total_products':         len(deduped),
    'paid_products':          sum(1 for p in deduped if not p.get('is_free')),
    'free_products':          sum(1 for p in deduped if p.get('is_free')),
    'total_reviews_in_set':   sum(p.get('review_count', 0) for p in deduped),
    'avg_price':              round(sum(p.get('price',0) for p in deduped if not p.get('is_free')) / max(1, sum(1 for p in deduped if not p.get('is_free'))), 2),
    'avg_rating':             round(sum(p.get('rating',0) or 0 for p in deduped) / max(1, sum(1 for p in deduped if p.get('rating'))), 2),
    'kombra_care_products':   len(kombra_care_targets),
    'unique_creators':        len(creator_map),
    'high_priority_creators': sum(1 for c in creators_sorted if c['outreach_priority'] == 'high'),
    'subjects_covered':       list(subject_stats.keys()),
    'top_10_by_priority':     [
        {
            'title':        p.get('title','')[:60],
            'creator':      p.get('creator_name',''),
            'price':        p.get('price', 0),
            'rating':       p.get('rating'),
            'reviews':      p.get('review_count', 0),
            'priority':     p.get('priority_score', 0),
            'subject':      p.get('subject',''),
            'kombra_care':  p.get('is_kombra_care', False),
            'url':          p.get('tpt_url',''),
        }
        for p in sorted_by_priority[:10]
    ],
    'top_10_by_reviews':      [
        {
            'title':    p.get('title','')[:60],
            'creator':  p.get('creator_name',''),
            'reviews':  p.get('review_count', 0),
            'price':    p.get('price', 0),
            'rating':   p.get('rating'),
            'url':      p.get('tpt_url',''),
        }
        for p in sorted_by_reviews[:10]
    ],
    'top_10_by_price':        [
        {
            'title':   p.get('title','')[:60],
            'creator': p.get('creator_name',''),
            'price':   p.get('price', 0),
            'reviews': p.get('review_count', 0),
            'url':     p.get('tpt_url',''),
        }
        for p in sorted_by_price[:10]
    ],
    'kombra_care_top_5':      [
        {
            'title':    p.get('title','')[:60],
            'tags':     p.get('kombra_care_tags', [])[:5],
            'reviews':  p.get('review_count', 0),
            'price':    p.get('price', 0),
            'priority': p.get('kombra_care_priority', 0),
        }
        for p in kombra_care_targets[:5]
    ],
    'subject_breakdown':      subject_stats,
    'files_produced': [
        'data/tpt_products.json',
        'data/tpt_priority_targets.json',
        'data/tpt_kombra_care_targets.json',
        'data/tpt_creator_outreach_list.json',
        'data/tpt_subject_analytics.json',
        'data/tpt_market_summary.json',
    ],
}

with open('data/tpt_market_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("Saved: data/tpt_market_summary.json")
```

---

## TASK 4: PRINT FINAL REPORT

```python
import json

with open('data/tpt_market_summary.json') as f:
    s = json.load(f)

print("\n" + "="*60)
print("TPT MARKET INTELLIGENCE — GEMINI SCRAPE REPORT")
print("="*60)
print(f"\nDate:              {s['scrape_date']}")
print(f"Total products:    {s['total_products']}")
print(f"  Paid:            {s['paid_products']}")
print(f"  Free:            {s['free_products']}")
print(f"Total reviews:     {s['total_reviews_in_set']:,}")
print(f"Avg price (paid):  ${s['avg_price']}")
print(f"Avg rating:        {s['avg_rating']}/5")
print(f"Kombra Care items: {s['kombra_care_products']}")
print(f"Unique creators:   {s['unique_creators']}")
print(f"High-priority:     {s['high_priority_creators']} creators (2000+ reviews)")

print("\n── TOP 10 BY PRIORITY SCORE ──────────────────────────")
for i, p in enumerate(s['top_10_by_priority'], 1):
    kc = " [KOMBRA CARE]" if p.get('kombra_care') else ""
    print(f"{i:2}. {p['title'][:45]:<45} ${p['price']:5.2f} | ⭐{p['rating']} | {p['reviews']:,} reviews | score:{p['priority']}{kc}")

print("\n── TOP 10 BY REVIEW COUNT ────────────────────────────")
for i, p in enumerate(s['top_10_by_reviews'], 1):
    print(f"{i:2}. {p['title'][:45]:<45} {p['reviews']:,} reviews | ${p['price']:.2f} | ⭐{p['rating']}")

print("\n── TOP 5 KOMBRA CARE TARGETS ─────────────────────────")
for i, p in enumerate(s['kombra_care_top_5'], 1):
    print(f"{i}. {p['title'][:50]}")
    print(f"   Tags: {', '.join(p['tags'][:4])}")
    print(f"   {p['reviews']:,} reviews | ${p['price']:.2f} | priority: {p['priority']}")

print("\n── SUBJECT BREAKDOWN ─────────────────────────────────")
for subj, stats in sorted(s['subject_breakdown'].items(), key=lambda x: x[1]['total_reviews'], reverse=True):
    print(f"  {subj:<25} {stats['product_count']:4} products | avg ${stats['avg_price']:.2f} | avg ⭐{stats['avg_rating']} | {stats['total_reviews']:,} total reviews")

print("\n── FILES READY FOR HAIKU PIPELINE ───────────────────")
for f in s['files_produced']:
    print(f"  ✓ {f}")

print("\n── NEXT STEP ─────────────────────────────────────────")
print("Download all files from data/ directory.")
print("Pass them to the Haiku Claude Code pipeline:")
print("  - data/tpt_products.json           → Phase 2 scoring input")
print("  - data/tpt_priority_targets.json   → Phase 3 generation targets")
print("  - data/tpt_kombra_care_targets.json → Phase 5 Kombra Care targets")
print("  - data/tpt_creator_outreach_list.json → Phase 4 outreach targets")
print("="*60)
```

---

## IF TPT BLOCKS SCRAPING

If requests return 403 or CAPTCHAs consistently, use Gemini's Google Search
grounding instead. Run this fallback:

```python
# FALLBACK: Use Gemini's search grounding to find TPT products
# This works if you have Google Search grounding enabled in AI Studio

# Ask Gemini to search for:
# 1. "site:teacherspayteachers.com science worksheet grade 4 5 most popular"
# 2. "site:teacherspayteachers.com special education autism activity reviews"
# 3. "teacherspayteachers best selling science lessons elementary 2024 2025"
# 4. "teachers pay teachers highest reviewed math worksheets grades 3-8"
# 5. "tpt best sellers special education life skills 2025"

# For each search result, extract:
# - Product title from the page title
# - URL (must contain /Product/)
# - Price from snippet if visible
# - Rating from snippet if visible
# - Review count from snippet if visible

# This will produce fewer results but still useful data.
# Save in same format to data/tpt_products_search_grounded.json

print("If direct scraping fails, enable Google Search grounding in AI Studio")
print("and ask Gemini to search for TPT products using the queries above.")
print("The output format is the same — same JSON schema, fewer products.")
```

=== PROMPT END ===

---

## OUTPUT FILES GEMINI PRODUCES

Hand these to the Haiku Claude Code session as uploaded files or copy paths:

| File | Contents | Used in |
|---|---|---|
| `data/tpt_products.json` | All scraped products, sorted by priority | Phase 2: Scoring |
| `data/tpt_priority_targets.json` | Top 50 paid products to target | Phase 3: Generation |
| `data/tpt_kombra_care_targets.json` | Special needs content to improve | Phase 5: Kombra Care |
| `data/tpt_creator_outreach_list.json` | Creators ranked by outreach priority | Phase 4: Outreach |
| `data/tpt_subject_analytics.json` | Market stats by subject | Context |
| `data/tpt_market_summary.json` | Full summary report | Decision-making |

## HOW TO HAND OFF TO HAIKU

In the Haiku Claude Code session, add this at the top of the prompt:

```
Market intelligence data from Gemini scrape is in:
  ./data/tpt_products.json           — all products
  ./data/tpt_priority_targets.json   — top 50 targets
  ./data/tpt_kombra_care_targets.json — special needs targets
  ./data/tpt_creator_outreach_list.json — creator outreach list

Skip Phase 1 (scraping). Start with Phase 2 (scoring).
Load data from these files instead of scraping fresh.
```
