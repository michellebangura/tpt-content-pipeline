# HAIKU CLAUDE CODE SESSION — TPT CONTENT PIPELINE
# Copy from SESSION START to SESSION END and paste as your first message.
# This is a pure execution session. No judgment calls. No content decisions.
# Every decision is pre-made below. Execute in order. Report results after each phase.

=== SESSION START ===

You are executing the Bright Standard TPT Content Pipeline. This is a four-phase
execution session. You write Python scripts, run them, store results, and report
what you found after each phase. You do not make content quality judgments — the
Five Checks scoring API does that. You do not decide what topics to cover — the
scrape data and the priority matrix below do that.

## CREDENTIALS

Read from environment:
- ANTHROPIC_API_KEY — your Anthropic API key (already set)
- SUPABASE_URL — https://gexxdsiowglhrxkkvsrv.supabase.co
- SUPABASE_SERVICE_KEY — Supabase service role key (already set)

Scoring API endpoint (no auth required, already deployed):
  POST https://gexxdsiowglhrxkkvsrv.supabase.co/functions/v1/score-content

Supabase REST API base:
  https://gexxdsiowglhrxkkvsrv.supabase.co/rest/v1

Use the service role key as: `Authorization: Bearer {SUPABASE_SERVICE_KEY}` and
`apikey: {SUPABASE_SERVICE_KEY}` headers on all Supabase REST calls.

---

## PHASE 1: TPT MARKET SCRAPE
### Goal: Find the highest-selling, highest-reviewed, highest-priced, lowest-quality content on TPT.
### This is the target list for Bright Standard to compete against.

Write and run: `scrape_tpt.py`

### What to scrape

TPT search URLs to scrape (each returns a list of product cards):

1. Best sellers across all subjects:
   https://www.teacherspayteachers.com/browse?order=Relevance&grade_levels=3,4,5,6,7,8

2. By subject — scrape each:
   - Science: https://www.teacherspayteachers.com/browse?subject=science&order=Relevance
   - Math: https://www.teacherspayteachers.com/browse?subject=math&order=Relevance
   - ELA/Reading: https://www.teacherspayteachers.com/browse?subject=ela&order=Relevance
   - Social Studies/History: https://www.teacherspayteachers.com/browse?subject=social-studies&order=Relevance
   - Special Education: https://www.teacherspayteachers.com/browse?subject=special-education&order=Relevance
   - Life Skills: https://www.teacherspayteachers.com/browse?subject=life-skills&order=Relevance

3. By price — high-priced content to target:
   https://www.teacherspayteachers.com/browse?price=paid&order=Price-High

### How to scrape

Use `requests` and `BeautifulSoup`. Add headers:
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}
```

Sleep 2 seconds between requests. If rate limited (429), sleep 30 seconds and retry.

### What to extract from each product card

From the search results page, extract what is visible without clicking through:
- `title` — the product title text
- `tpt_url` — the full product URL
- `creator_name` — seller/author name
- `price` — price as float (0.0 if free)
- `rating` — star rating as float (e.g. 4.8)
- `review_count` — integer number of reviews
- `grade_band` — grade levels shown
- `subject` — subject category
- `description_preview` — first 300 chars of any visible description

For the top 20 products on each search URL, ALSO click through to the product
detail page and extract:
- `full_description` — the full product description text
- `what_is_included` — "What's Included" section text if present
- `standards` — any standards codes mentioned
- `learning_objectives` — any objectives listed
- `preview_content` — any visible preview text

### Priority scoring formula

After scraping, compute a `priority_score` for each product:
```
priority_score = (review_count * 0.4) + (price * 10 * 0.3) + ((5 - rating) * 20 * 0.3)
```

This weights high review count (market size), high price (revenue opportunity),
and low rating (easiest to beat). Higher priority_score = attack this first.

### Output

Save all scraped products to: `data/tpt_products.json`

Format:
```json
[
  {
    "title": "...",
    "tpt_url": "...",
    "creator_name": "...",
    "creator_email": null,
    "price": 4.99,
    "rating": 4.2,
    "review_count": 3847,
    "grade_band": "3-5",
    "subject": "Science",
    "description_preview": "...",
    "full_description": "...",
    "what_is_included": "...",
    "standards": "...",
    "learning_objectives": "...",
    "priority_score": 0.0,
    "bright_standard_score": null,
    "certified": false,
    "bs_lesson_id": null,
    "scrape_date": "2026-05-15"
  }
]
```

Also save `data/tpt_products_sorted.json` — same data sorted by `priority_score` descending.

Report: total products scraped, top 10 by priority_score with title/creator/price/rating/reviews.

---

## PHASE 2: FIVE CHECKS SCORING
### Goal: Score every scraped product against the Five Checks framework.
### This creates the evidence base for creator outreach and content targeting.

Write and run: `score_tpt_products.py`

### Process

Load `data/tpt_products.json`. For each product:

1. POST to the scoring API:
```python
import requests, os, time

SCORE_API = 'https://gexxdsiowglhrxkkvsrv.supabase.co/functions/v1/score-content'

payload = {
    'tpt_url': product['tpt_url'],
    'title': product['title'],
    'description': product.get('full_description') or product.get('description_preview', ''),
    'grade': product.get('grade_band', ''),
    'subject': product.get('subject', ''),
    'creator_name': product.get('creator_name', ''),
    'price': product.get('price', 0),
    'content_preview': '\n'.join(filter(None, [
        product.get('what_is_included', ''),
        product.get('learning_objectives', ''),
        product.get('standards', ''),
    ]))[:2000],
    'scan_source': 'pipeline',
    'store_result': True,
}

response = requests.post(SCORE_API, json=payload, timeout=30)
time.sleep(1)  # rate limiting
```

2. On success, update the product record:
```python
result = response.json()
product['bright_standard_score'] = result.get('overall')
product['bs_scores'] = result.get('scores', {})
product['certified'] = result.get('certified', False)
product['bs_headline'] = result.get('headline', '')
product['bs_biggest_gap'] = result.get('biggest_gap', '')
product['bs_what_works'] = result.get('what_works', '')
product['bs_suggestions'] = result.get('suggestions', {})
```

3. On error (non-200 or network error): set `bright_standard_score: null`, log
   the error, continue to next product. Do not crash.

4. Save progress every 10 products to `data/tpt_products_scored.json` so the
   run is resumable. Check if a product already has a score before calling the
   API — skip it if `bright_standard_score` is not null.

### Output

Save `data/tpt_products_scored.json` — all products with scores.

Save `data/targeting_report.json`:
```json
{
  "total_scored": 0,
  "certified": 0,
  "below_standard": 0,
  "avg_score": 0.0,
  "by_subject": {},
  "priority_targets": [],   // top 50 by priority_score where certified=false
  "certified_list": []       // any that passed
}
```

Save `data/creator_outreach_list.json` — unique creators with below-standard
content, sorted by total review count of their flagged products:
```json
[
  {
    "creator_name": "...",
    "tpt_store_url": "...",
    "product_count": 0,
    "total_reviews": 0,
    "avg_score": 0.0,
    "lowest_scoring_product": "...",
    "lowest_score": 0.0,
    "outreach_priority": "high"  // high if total_reviews > 1000, medium if > 500, low otherwise
  }
]
```

Report: score distribution, how many certified vs not, top 20 targets by priority,
subject breakdown.

---

## PHASE 3: CONTENT GENERATION
### Goal: Generate Bright Standard certified lesson alternatives for the top 50 priority targets.
### Only lessons that score 4+ on ALL FIVE checks get written to the database.

Write and run: `generate_content.py`

### Priority target selection

Load `data/targeting_report.json`, extract `priority_targets`. Take the first 50.

Group them by subject and grade band so generated content is distributed:
- Do not generate more than 5 lessons on the same subject+grade combination
- If a group has >5 targets, take the 5 with highest priority_score

### Generation prompt

For each target product, call the Anthropic API directly to generate a lesson.
This is NOT the scoring API — this is a direct Anthropic API call:

```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

def generate_lesson(target):
    prompt = f"""You are generating a Bright Standard certified lesson plan.

TARGET CONTENT TO IMPROVE UPON:
Title: {target['title']}
Subject: {target['subject']}
Grade: {target['grade_band']}
What it does (their description): {target.get('full_description', '')[:500]}
What it lacks (from Five Checks scoring): {target.get('bs_biggest_gap', '')}
Their score: {target.get('bright_standard_score', 'unknown')}/5

YOUR TASK: Generate a BETTER lesson on the same topic/standard area that scores
5/5 on EVERY Bright Standard dimension. This lesson will be listed on TPT for $1
as a direct alternative.

BRIGHT STANDARD FIVE CHECKS — your lesson MUST pass all five:
1. RIGOR: Students do real cognitive work. Analysis, synthesis, or creation —
   not worksheets. Students produce something that required thinking.
2. INCLUSIVITY: Works with $0 materials OR provides explicit alternatives for
   every cost. Works for ADHD, ELL, kinesthetic learners with named scaffolds.
3. PERSPECTIVES: Multiple viewpoints required. No single narrative presented as
   truth. Underrepresented voices centered at least once in the lesson.
4. EMPATHY: Students understand an experience different from their own.
   Emotional intelligence and social awareness are built, not just content knowledge.
5. CRITICAL THINKING: Students form their own conclusions from evidence.
   They question something. They distinguish opinion from fact.

REQUIRED OUTPUT FORMAT — return ONLY valid JSON, no markdown, no explanation:

{{
  "title": "Title that is specific and describes what students DO, not just the topic",
  "description": "2-3 sentences: what students do, what they produce, why it matters. Present tense. Teacher voice.",
  "subject": "{target['subject']}",
  "grade_levels": [grade numbers as integers, e.g. [4, 5]],
  "duration_minutes": 45,
  "output_artifact_name": "Your [Specific Thing] — name what students produce, first-person possessive",
  "learning_objectives": [
    "Students will [Bloom's verb] [specific content]",
    "Students will [Bloom's verb] [specific content]",
    "Students will [Bloom's verb] [specific content]"
  ],
  "bloom_levels": ["analyze", "evaluate", "create"],
  "canonical_themes": ["identity", "power", "purpose"],
  "materials_cost_per_student": 0.00,
  "requires_materials": false,
  "prep_time_minutes": 5,
  "student_needs": ["ADHD-friendly", "ELL-friendly"],
  "content": {{
    "activities": [
      {{
        "step": "Hook · 5 min",
        "title": "Activity title",
        "desc": "Detailed description of what the teacher does and what students do. Enough detail to actually teach it.",
        "cognitive_insight": "Why this activity works — the learning science behind it. 1-2 sentences in teacher voice.",
        "five_check_connection": "Rigor"
      }}
    ],
    "materials_list": [
      {{
        "item": "Item name",
        "qty": "1 per student",
        "cost": "$0.00",
        "substitute": "What works instead if unavailable"
      }}
    ]
  }},
  "standards_aligned": {{
    "federal": [],
    "state": [],
    "district": []
  }},
  "kombra_care_notes": null,
  "autism_accommodations": null,
  "low_sensory_version": null
}}

KOMBRA CARE INTEGRATION: If the subject is Life Skills, Special Education, or
the topic involves emotional regulation, social skills, or daily living skills,
ALSO populate:
- kombra_care_notes: specific guidance for caregivers using this lesson at home
- autism_accommodations: specific modifications for autistic students
- low_sensory_version: version of the lesson with all sensory stimulation minimized

TRANSLATION NOTE: Write all copy as if it will be translated into 10 languages.
No idioms. No culturally-specific references without explanation. Short sentences.
Active voice. Specific nouns, not pronouns where possible."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
```

### Scoring gate

After generating, send the generated lesson through the scoring API BEFORE
writing to the database. Only write to the database if EVERY dimension scores 4+.

```python
def score_generated_lesson(lesson_json):
    payload = {
        'title': lesson_json['title'],
        'description': lesson_json['description'],
        'grade': ','.join(str(g) for g in lesson_json.get('grade_levels', [])),
        'subject': lesson_json['subject'],
        'learning_objectives': lesson_json.get('learning_objectives', []),
        'content_preview': json.dumps(lesson_json.get('content', {}))[:2000],
        'scan_source': 'factory',
        'store_result': False,  # don't store failed attempts
    }
    res = requests.post(SCORE_API, json=payload, timeout=30)
    return res.json()
```

If a lesson fails the gate (any dimension < 4):
- Log which dimensions failed and the suggestions
- Regenerate with a revised prompt that explicitly addresses the failures
- Try up to 3 times
- If still failing after 3 attempts, log to `data/generation_failures.json` and skip

### Database insert (only for passing lessons)

Use Supabase REST API to insert:

```python
import requests, os

SUPA = os.environ['SUPABASE_URL']
KEY  = os.environ['SUPABASE_SERVICE_KEY']
HEADERS = {
    'Authorization': f'Bearer {KEY}',
    'apikey': KEY,
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

def insert_lesson(lesson, score_result, target_tpt_url):
    record = {
        'title':                    lesson['title'],
        'description':              lesson['description'],
        'subject':                  lesson['subject'],
        'grade_levels':             lesson.get('grade_levels', []),
        'duration_minutes':         lesson.get('duration_minutes', 45),
        'learning_objectives':      lesson.get('learning_objectives', []),
        'bloom_levels':             lesson.get('bloom_levels', []),
        'canonical_themes':         lesson.get('canonical_themes', []),
        'materials_cost_per_student': lesson.get('materials_cost_per_student', 0),
        'requires_materials':       lesson.get('requires_materials', False),
        'prep_time_minutes':        lesson.get('prep_time_minutes', 5),
        'student_needs':            lesson.get('student_needs', []),
        'output_artifact_name':     lesson.get('output_artifact_name', ''),
        'content':                  lesson.get('content', {}),
        'standards_aligned':        lesson.get('standards_aligned', {}),
        'is_public':                True,
        'is_ai_generated':          True,
        'status':                   'published',
        'learning_context':         'classroom',
        'country':                  'US',
        'governance_status':        'certified',
        'certification_authority':  'bright_standard_ai',
        'quality_scores': {
            'rigor':       score_result['scores']['rigor'],
            'inclusivity': score_result['scores']['inclusivity'],
            'perspective': score_result['scores']['perspective'],
            'empathy':     score_result['scores']['empathy'],
            'thinking':    score_result['scores']['thinking'],
            'bright_standard_certified': True,
        },
        'assessment_notes': f'Generated as alternative to TPT: {target_tpt_url}',
    }

    res = requests.post(
        f'{SUPA}/rest/v1/lessons',
        headers=HEADERS,
        json=record,
    )
    if res.status_code in (200, 201):
        return res.json()[0]['id']
    else:
        raise Exception(f'Insert failed: {res.status_code} {res.text}')
```

After successful insert, update `tpt_scans` to link this TPT product to the
generated lesson:

```python
requests.patch(
    f'{SUPA}/rest/v1/tpt_scans',
    headers={**HEADERS, 'Prefer': 'return=minimal'},
    params={'tpt_url': f'eq.{target_tpt_url}'},
    json={'bright_standard_lesson_id': lesson_id},
)
```

Also update the content_factory_queue:

```python
requests.post(
    f'{SUPA}/rest/v1/content_factory_queue',
    headers=HEADERS,
    json={
        'topic': lesson['title'],
        'subject': lesson['subject'],
        'grade_levels': lesson.get('grade_levels', []),
        'canonical_themes': lesson.get('canonical_themes', []),
        'status': 'listed',
        'generated_lesson_id': lesson_id,
        'five_checks_scores': score_result.get('scores'),
        'tpt_price_cents': 100,
    },
)
```

### Output

Save `data/generated_lessons.json`:
```json
[
  {
    "lesson_id": "uuid from database",
    "title": "...",
    "subject": "...",
    "grade_levels": [],
    "scores": {},
    "overall": 4.8,
    "target_tpt_url": "...",
    "target_tpt_title": "...",
    "bs_url": "https://thebrightstandard.com/lesson/{lesson_id}",
    "tpt_list_price_cents": 100,
    "kombra_care": false,
    "autism_accommodations": false,
    "low_sensory": false
  }
]
```

Save `data/generation_failures.json` — lessons that failed the gate 3 times.

Report: total generated, total passed gate, total failed, pass rate, subject
distribution, how many have Kombra Care integration.

---

## PHASE 4: CREATOR OUTREACH EMAILS
### Goal: Generate personalized outreach emails for every creator with below-standard content.
### Do not send. Write to files only. Michelle sends them.

Write and run: `generate_outreach.py`

### Load inputs

Load `data/creator_outreach_list.json` (from Phase 2).
Load `data/generated_lessons.json` (from Phase 3) to know which alternatives exist.
Load `data/tpt_products_scored.json` to get full product details per creator.

### For each creator, generate two emails

**EMAIL 1: The offer (send first)**

```python
def generate_offer_email(creator, their_products, alternatives):
    # Their worst product
    worst = min(their_products, key=lambda p: p.get('bright_standard_score', 5))
    # Alternative if it exists
    alt = next((a for a in alternatives
                if a['target_tpt_url'] == worst['tpt_url']), None)

    prompt = f"""Write a short, direct, professional email from Bright Standard to a TPT creator.

TONE: Peer-to-peer. Not corporate. Not condescending. This is one educator
talking to another. Acknowledge their work is being used. Be honest but kind
about the quality gap. Make a clear offer. Under 200 words.

FACTS TO USE:
- Creator name: {creator['creator_name']}
- Their product: "{worst['title']}"
- Review count: {worst['review_count']} reviews (teachers are using this)
- Their Five Checks score: {worst.get('bright_standard_score', 'unknown')}/5
- The specific gap: {worst.get('bs_biggest_gap', 'quality issues identified')}
- What the subscription offers: specific AI-powered suggestions + certified badge

THE OFFER:
- Free: See the score and top-line feedback at thebrightstandard.com/creators
- $9/month: Get specific, actionable improvement suggestions per dimension
  + the Bright Standard certified badge for TPT listings once you pass
- The badge signals to the 85% of US teachers who use TPT that this content
  has been independently verified

DO NOT:
- Say the word "mediocre"
- Say "your content is bad"
- Use corporate language like "leverage" or "synergize"
- Threaten them or mention competitive alternatives

DO:
- Be specific about what the score was and what dimension needs work
- Make the value of the badge concrete
- Make the $9 feel like nothing compared to what one good rating is worth

Return only the email text. No subject line. No greeting/closing boilerplate.
Subject line separately at the end after three dashes: ---"""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text
```

**EMAIL 2: The competitive notice (send only if they don't respond to Email 1 in 30 days)**

```python
def generate_competitive_email(creator, their_products, alternatives):
    worst = min(their_products, key=lambda p: p.get('bright_standard_score', 5))
    alt = next((a for a in alternatives
                if a['target_tpt_url'] == worst['tpt_url']), None)

    alt_info = ""
    if alt:
        alt_info = f"""
- Our alternative: "{alt['title']}"
- Our price: $1.00 (vs their ${worst['price']:.2f})
- Our Five Checks score: {alt['overall']:.1f}/5
- Our TPT listing: [to be added when listed]
- Our Bright Standard listing: {alt['bs_url']}"""

    prompt = f"""Write a short professional email. This is the second email to a TPT creator
who did not respond to our first outreach about improving their content quality.

CONTEXT:
- Creator: {creator['creator_name']}
- Their product: "{worst['title']}" — {worst['review_count']} reviews, ${worst['price']:.2f}
- Their Five Checks score: {worst.get('bright_standard_score', 'unknown')}/5
- We now have a certified alternative listed{alt_info if alt_info else ' (in progress)'}

TONE: Still respectful. Honest. Not threatening. We are not trying to destroy
their business — we are creating economic incentive for quality. The email
acknowledges we are now competing directly, explains why, and keeps the door
open for them to get certified instead.

KEY MESSAGE: We would rather have them certified and listed on Bright Standard
than compete with them. The offer is still open. But we are proceeding either way.

Under 150 words. Return only the email text, then --- then the subject line."""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text
```

### Output structure

Save to `data/outreach/`:

```
data/outreach/
  {creator_slug}_email1.txt   — offer email
  {creator_slug}_email2.txt   — competitive notice
  {creator_slug}_context.json — their products, scores, alternatives
```

Also save `data/outreach_summary.json`:
```json
{
  "total_creators": 0,
  "high_priority": 0,
  "medium_priority": 0,
  "low_priority": 0,
  "with_alternatives_ready": 0,
  "without_alternatives_yet": 0,
  "estimated_total_revenue_at_risk": 0.0,
  "creator_list": []
}
```

Report: total emails generated, how many have alternatives ready to reference,
top 10 creators by total review count.

---

## PHASE 5: KOMBRA CARE & SPECIAL NEEDS CONTENT IDENTIFICATION
### Goal: Identify the specific TPT categories where Kombra Care integration is highest value.

Write and run: `kombra_care_analysis.py`

### What to find

From the scraped products and scored results, identify:

1. All products tagged Special Education, Life Skills, Autism, or containing
   these terms in title/description:
   - "autism", "ASD", "autistic", "sensory", "low sensory", "ADHD",
   - "IEP", "504", "special needs", "learning disability",
   - "social skills", "emotional regulation", "executive function",
   - "daily living", "life skills", "independence skills",
   - "nonverbal", "AAC", "alternative communication"

2. For each matching product, check:
   - Price (high price in special ed = high parent/caregiver willingness to pay)
   - Review count (high reviews = high need)
   - Score (low score = high opportunity)

3. Compute a `kombra_care_priority` score:
   ```
   kombra_care_priority = (price * 15) + (review_count * 0.5) + ((5 - score) * 25)
   ```

### Output

Save `data/kombra_care_targets.json`:
```json
[
  {
    "title": "...",
    "tpt_url": "...",
    "price": 0.0,
    "review_count": 0,
    "bright_standard_score": 0.0,
    "kombra_care_priority": 0.0,
    "special_needs_tags": ["autism", "sensory"],
    "why_kombra_care": "one sentence explaining the Kombra Care angle for this content"
  }
]
```

Also output the top 10 as a table in the terminal.

### Auto-generate Kombra Care versions for top 10

For each of the top 10 by kombra_care_priority, add these fields to the
generation prompt in Phase 3:

```python
kombra_care_extension = """
KOMBRA CARE INTEGRATION REQUIRED for this lesson:

kombra_care_notes: Write 3-5 sentences specifically for a caregiver (parent,
grandparent, support worker) who wants to reinforce this learning at home.
Assume no teaching background. Use plain language. Include one specific
activity they can do at the dinner table or in the car.

autism_accommodations: List 5 specific modifications. Each must be concrete
and implementable without specialist training. Cover: sensory, communication,
routine/predictability, social participation, and output alternatives.

low_sensory_version: Rewrite the core activity with: no bright colors required,
no auditory signals, no unexpected sounds, no crowded spaces, no touching other
students, no sudden transitions. Same learning objectives, different environment.
"""
```

---

## COMPLETION REPORT

After all phases complete, produce a final summary:

```
=== TPT CONTENT PIPELINE — COMPLETION REPORT ===

PHASE 1 — SCRAPE
  Total products scraped: X
  Subjects covered: [list]
  Price range: $X.XX - $X.XX
  Review count range: X - X

PHASE 2 — SCORING
  Total scored: X
  Certified (4+ all dimensions): X (X%)
  Below standard: X (X%)
  Average Five Checks score: X.X/5
  By subject (avg score):
    Science:         X.X
    Math:            X.X
    ELA:             X.X
    Social Studies:  X.X
    Special Ed:      X.X
    Life Skills:     X.X
  Creators identified for outreach: X
  High priority creators: X

PHASE 3 — CONTENT GENERATION
  Lessons generated: X
  Passed scoring gate: X (X% pass rate)
  Failed after 3 attempts: X
  Written to Bright Standard database: X
  With Kombra Care integration: X
  With autism accommodations: X
  With low-sensory version: X

PHASE 4 — OUTREACH
  Email 1 (offer) written: X
  Email 2 (competitive notice) written: X
  Creators with alternatives already ready: X

PHASE 5 — KOMBRA CARE
  Special needs products identified: X
  Kombra Care targets: X
  Kombra Care lessons generated: X

FILES CREATED:
  data/tpt_products.json
  data/tpt_products_scored.json
  data/targeting_report.json
  data/creator_outreach_list.json
  data/generated_lessons.json
  data/generation_failures.json
  data/kombra_care_targets.json
  data/outreach/ (X email pairs)

NEXT STEPS FOR MICHELLE:
  1. Review data/outreach/ emails — edit if needed, then send Email 1 to all
  2. Review data/generated_lessons.json — spot-check 5-10 lessons for quality
  3. List generated lessons on TPT at $1 each (manual step — TPT requires human account)
  4. Set 30-day reminder to send Email 2 to non-responders
  5. Check thebrightstandard.com/hub — all generated lessons should appear there now
```

---

## EXECUTION NOTES

- Run all phases in order. Do not skip.
- If a phase errors, fix the error and continue from where it stopped.
  The JSON files are checkpoints — use them.
- If the scoring API returns errors consistently, check:
  - Is ANTHROPIC_API_KEY set in Supabase Edge Function secrets?
  - Dashboard: supabase.com/dashboard/project/gexxdsiowglhrxkkvsrv/settings/functions
  - The key is named ANTHROPIC_API_KEY
- Install dependencies at start: `pip install requests beautifulsoup4 anthropic`
- All data files go in `./data/` directory (create it if it doesn't exist)
- All outreach files go in `./data/outreach/` directory

Begin with Phase 1. Report completion before moving to Phase 2.

=== SESSION END ===
