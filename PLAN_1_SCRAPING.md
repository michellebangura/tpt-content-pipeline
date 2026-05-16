# PLAN 1: TPT DATA ACQUISITION
## What failed, why, and the correct architecture going forward
## For: Researcher / Data Conversation

---

## WHAT HAPPENED AND WHY

### The Python script corruption problem
Both Gemini CLI and AI Studio failed to write and execute the scraping script because of a fundamental tooling bug: their `write_file` tool mishandles newlines inside Python string arguments. Specifically:
- `separator='\n'` inside `get_text()` calls becomes a literal newline in the file
- Triple-quoted strings break at the newline character
- The result is `SyntaxError: unterminated string literal` at exactly the line where a string contains `\n`

**This is NOT a Python problem. It is a tool problem.**

### The fix that works
The script lives in GitHub. The AI downloads it with `curl` and runs it. Nothing is written by the AI tool. No corruption possible.

```bash
curl -L https://raw.githubusercontent.com/michellebangura/tpt-content-pipeline/main/scrape_tpt.py -o scrape_tpt.py
python3 scrape_tpt.py
```

This is confirmed working. The script auto-installs its own dependencies.

### Why only Science data was returned
The scraper ran successfully for the first search URL (Science) then stopped — likely because the Gemini session ended or hit a time/token limit before the loop completed the other 8 categories. The script has checkpointing: if `data/tpt_products_raw.json` already exists it resumes from where it stopped. Running it again will pick up Math, ELA, Social Studies, Special Ed, Life Skills, SEL, high-price, and grades 3-8.

### Why review counts are all zero
TPT renders review counts via JavaScript after initial HTML load. Static HTML scraping with `requests` + `BeautifulSoup` cannot capture JavaScript-rendered content. The star rating averages ARE captured because they appear in `aria-label` attributes in the static HTML.

**This is a known limitation, not a bug.** The review count field will remain 0 unless the scraper is rebuilt with Selenium or Playwright (browser automation). For the current purpose — identifying content to compete with — price and rating are sufficient. Review count can be supplemented by manually checking the top 50 priority products.

---

## WHAT THE CURRENT DATA SHOWS (1,213 products, Science only)

- **Average price:** $22.23 | **Median price:** $6.75
- **Our $1 certified lesson:** extreme price competitor against the median
- **Top creator:** Krista Wallden — 113 products, average $15.68
- **170 products** have full descriptions (detail-scraped) — ready to score
- **Grade bands:** not captured in static HTML (same JS rendering issue as review counts)
- **Kombra Care content:** 23 products tagged with autism/sensory/ADHD/IEP keywords

---

## CORRECT SCRAPING ARCHITECTURE FOR FULL DATA

### Option A: Static scraping (current — fast, incomplete)
**Use for:** bulk discovery, price data, rating averages, creator identification, URL lists
**Cannot get:** review counts, grade levels, dynamic content
**Runtime:** ~45 minutes for all 9 categories
**Tool:** `scrape_tpt.py` in tpt-content-pipeline repo

**To run the remaining categories now:**
```bash
curl -L https://raw.githubusercontent.com/michellebangura/tpt-content-pipeline/main/scrape_tpt.py -o scrape_tpt.py
python3 scrape_tpt.py
# Script resumes from checkpoint, skips Science, runs Math/ELA/etc.
```

### Option B: Browser automation (Playwright — complete data)
**Use for:** review counts, grade level data, preview images, full dynamic content
**Gets everything:** all fields, all dynamic content
**Runtime:** 3-4 hours for full catalog
**Requires:** `pip install playwright && playwright install chromium`
**Note:** More likely to be blocked by TPT's bot detection. Need to add randomized delays (2-8s), rotate user agents, and potentially use residential proxies.

**Playwright script skeleton (not corrupted by write_file — no multi-line strings):**
```python
from playwright.sync_api import sync_playwright
import json, time, random

products = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.teacherspayteachers.com/browse?subject[]=Math&order=Rating")
    time.sleep(random.uniform(2, 5))
    # Extract cards after JS renders
    cards = page.query_selector_all('[data-testid="product-card"]')
    for card in cards:
        review_el = card.query_selector('[data-testid="review-count"]')
        review_count = int(review_el.inner_text().replace(",","")) if review_el else 0
        products.append({"review_count": review_count})
    browser.close()
```

### Option C: TPT API / Affiliate data
TPT has an affiliate program and may have a data API for partners. This is worth investigating — an API would give clean structured data with review counts. Check: teacherspayteachers.com/Affiliates

### Option D: Gemini with Google Search grounding (fallback)
When direct HTTP scraping fails due to bot detection, Gemini in AI Studio with Google Search grounding enabled can extract product data from search results. This gives: title, price, rating, review count (from Google snippets), URL. Less complete than direct scraping but works through bot protection.

**Gemini prompt for this fallback:**
```
Search for the top 50 most-reviewed TPT products in [SUBJECT] for grades 3-8.
For each result, extract: title, URL, price, star rating, review count, creator name.
Output as JSON array. Only include products on teacherspayteachers.com/Product/ URLs.
```

---

## THE 6 CATEGORIES STILL NEEDED

Run the existing scraper to get these. Priority order:

1. **Math** — second biggest category, highest Perspectives opportunity (fractions history, Egyptian notation, imperial vs metric)
2. **ELA** — science of reading movement creating district urgency right now
3. **Social Studies / History** — highest political contestation = highest differentiation value
4. **Special Education** — highest price points, worst quality gap, Kombra Care integration
5. **Life Skills** — strong overlap with Kombra Care, daily living, autism/AAC content
6. **SEL** — Social Emotional Learning; currently being defunded federally = district scramble for alternatives

---

## WHAT TO DO WITH THE DATA ONCE COLLECTED

### Phase 1: Score everything
POST each product to `score-content` Edge Function:
```
POST https://gexxdsiowglhrxkkvsrv.supabase.co/functions/v1/score-content
{
  "tpt_url": "...",
  "title": "...",
  "description": "...",
  "grade": "...",
  "subject": "...",
  "scan_source": "pipeline",
  "store_result": true
}
```
Results stored in `tpt_scans` table. No auth required.

### Phase 2: Build priority target list
Sort `tpt_scans` by: (high review count × price × inverse Five Checks score)
The top 50 = the content to generate certified alternatives for first.

### Phase 3: Generate alternatives
For each priority target, call Anthropic API directly (not the scoring API) with the generation prompt in `HAIKU_PROMPT.md`. Score the output. Only store if 4+ on all five dimensions.

### Phase 4: Creator outreach
Use `tpt_creator_outreach_list.json` (generated by scraper). Email 1 = the offer. Email 2 (30 days later) = the competitive notice. See `PLAN_4_MARKETING_OUTREACH.md` for the automated outreach system.

---

## FILES IN THE PIPELINE REPO

| File | Purpose |
|---|---|
| `scrape_tpt.py` | Main scraper — download from GitHub, run locally |
| `GEMINI_SCRAPING_PROMPT.md` | Instructions for Gemini CLI or AI Studio |
| `HAIKU_PROMPT.md` | Claude Code session for scoring + generation + outreach |
| `data/` | Output directory — all JSON files land here |

---

## DATABASE TABLES FOR TPT DATA

| Table | Purpose | Current rows |
|---|---|---|
| `tpt_scans` | Every TPT product scored | 10 (seed) |
| `creator_profiles` | TPT creators who have submitted for certification | 0 |
| `content_factory_queue` | Generated lesson pipeline queue | 0 |
| `lessons` | Bright Standard published lessons | 31 |

---

## IMMEDIATE NEXT ACTION FOR RESEARCHER

1. Run scraper for remaining 5 categories (Math, ELA, Social Studies, Special Ed, Life Skills)
2. Upload resulting `data/tpt_products.json` to the pipeline conversation
3. Run scoring: POST each product to score-content endpoint (Python loop, no AI needed)
4. Identify top 50 priority targets by score formula
5. Flag all Kombra Care products (autism/sensory/ADHD keywords) separately
6. Report back: subject distribution, score distribution, top targets, Kombra Care count
