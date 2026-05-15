# GEMINI CLI — TPT SCRAPING SESSION
# Paste these two lines into Gemini CLI. That's it.
# The script lives in GitHub. Gemini downloads it and runs it.
# No writing. No string corruption. No SyntaxError.

=== PASTE THIS INTO GEMINI CLI ===

Download and run the TPT scraper from GitHub, then report the results.

Run these shell commands in order:

1. curl -L https://raw.githubusercontent.com/michellebangura/tpt-content-pipeline/main/scrape_tpt.py -o scrape_tpt.py

2. python3 scrape_tpt.py

After it finishes, tell me:
- How many products were scraped
- The top 10 by priority score (title, price, rating, review count)
- The top 5 Kombra Care targets (title, tags, reviews)
- Which output files were created in the data/ directory

=== END ===

---

## IF GEMINI CLI BLOCKS CURL OR OUTBOUND REQUESTS

Some Gemini CLI environments restrict network access from shell commands.
If curl fails, try:

```
Download the file at this URL and save it as scrape_tpt.py, then run it with python3:
https://raw.githubusercontent.com/michellebangura/tpt-content-pipeline/main/scrape_tpt.py
```

## IF AI STUDIO (browser)

In AI Studio with Code Execution enabled, paste this:

```
Run this Python code to download and execute the TPT scraper:

import urllib.request
urllib.request.urlretrieve(
    "https://raw.githubusercontent.com/michellebangura/tpt-content-pipeline/main/scrape_tpt.py",
    "scrape_tpt.py"
)

exec(open("scrape_tpt.py").read())
```

## WHAT THE SCRIPT DOES

Four tasks in one file, runs straight through:

1. Scrapes 9 TPT search categories (Science, Math, ELA, Social Studies,
   Special Education, Life Skills, SEL, high-price, grades 3-8),
   3 pages each. Sleeps 2.5s between requests.

2. Detail-scrapes the top 100 products by priority score —
   full description, objectives, standards, creator store URL.

3. Cleans data, deduplicates, flags Kombra Care content,
   aggregates by creator, computes subject analytics.

4. Prints the full market intelligence report and saves 6 JSON files.

## OUTPUT FILES (pass these to Haiku)

data/tpt_products.json              — all products sorted by priority
data/tpt_priority_targets.json      — top 50 paid products to target
data/tpt_kombra_care_targets.json   — special needs content targets
data/tpt_creator_outreach_list.json — creators sorted by review count
data/tpt_subject_analytics.json     — market stats by subject
data/tpt_market_summary.json        — full summary report

## HAND OFF TO HAIKU

Prepend this to the HAIKU_PROMPT.md session:

  Gemini scrape data is in ./data/ — skip Phase 1, start at Phase 2.
  Load data/tpt_products.json instead of scraping.
