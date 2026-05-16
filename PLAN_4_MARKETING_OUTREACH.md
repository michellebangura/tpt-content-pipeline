# PLAN 4: MARKETING, OUTREACH & AUTOMATED ENGAGEMENT
## Where teachers are, how to reach them, and how to automate it
## For: Planner + Marketing conversations / Claude API agentic build

---

## THE CORE STRATEGIC REALITY

Teachers don't browse EdTech product sites looking for tools. They search for specific content when they need it, in the middle of lesson planning. The marketing strategy must meet them there, not wait for them to come here.

The two moments that matter:
1. **The TPT moment** — a teacher is on TPT right now, looking for a lesson, about to spend $8.99. The Chrome extension intercepts this moment. This is the highest-conversion touch.
2. **The planning moment** — a teacher is searching Google for "photosynthesis lesson grade 4." Bright Standard content must appear in those results. This requires SEO-optimized public lesson pages.

Everything else — social, Reddit, email, communities — builds the brand that makes moment 1 and 2 convert faster.

---

## WHERE TEACHERS ACTUALLY ARE

### Reddit (highest engagement, lowest barrier)
- r/Teachers (1.2M members) — general teaching discussion
- r/Education (900K members) — broader but active
- r/TeachersInTransition — career changes, burnout, looking for better systems
- r/science_education — science teachers specifically
- r/MathTeachers — math teachers
- r/ELATeachers — English/Language Arts
- r/ElementaryTeachers — K-5 focused
- r/MiddleSchoolTeachers — 6-8 focused

**The rules:** No self-promotion in r/Teachers or r/Education without value-first. The playbook is: post a genuinely useful resource, mention Bright Standard as the source, answer questions. Do not post "check out my site." Post the lesson itself.

**What works on Reddit:**
- "I made a free fractions lesson that connects to Egyptian mathematics and it actually works — here's the breakdown"
- "My school has zero budget. Here's how I built a photosynthesis lab for $0 per student"
- "I scored 200 TPT lessons against 5 quality criteria. Here's what I found."
- "TIL fractions lessons in the US almost never acknowledge that the a/b notation is Hindu-Arabic in origin. I fixed that."

**What doesn't work:** Anything that reads like marketing. Any link in the first post without value before it.

### Facebook Groups (second highest reach)
- "Teachers Pay Teachers Teachers" group (ironic name, 200K+ members)
- "Elementary Teachers" (500K+ members)
- "Science Teachers Network" (150K+)
- Subject-specific grade band groups
- State-specific teacher groups (California Teachers, Texas Teachers, etc.)

**The approach:** Join, contribute for 2 weeks before posting anything with a link. Then: share a lesson (not the site), ask for feedback, mention where it came from.

### Teachers Pay Teachers Itself
- TPT has a seller community and buyer review system
- Posting certified $1 lessons directly competes and drives traffic
- Every TPT listing for a Bright Standard lesson includes: "This lesson is Five Checks certified at thebrightstandard.com where you can find 200+ certified lessons for free"

### X/Twitter (declining but teacher presence remains)
- #TeacherTwitter (historically strong, declining post-2023)
- @teachers handles, #edchat, #education hashtags
- Lower ROI than Reddit or Facebook currently

### Pinterest (underrated for teachers)
- Teachers use Pinterest for lesson discovery constantly
- SEO-optimized pins can drive long-term organic traffic
- Pin: lesson title + Five Checks scores + "Free at Bright Standard"
- Link to lesson detail page

### Email newsletters
- Many education writers/curators have newsletters
- Cult of Pedagogy (Jennifer Gonzalez) — 300K+ subscribers
- The Tempered Radical (Bill Ferriter)
- Angela Watson's Truth for Teachers
- EdSurge — EdTech focused
- Getting Smart

**The pitch:** "We built an objective quality standard for lesson plans that any teacher can use to evaluate content before buying it on TPT. We'd love to share the framework and our free certified content with your readers."

### Teacher professional development
- Edcamp (unconferences) — teachers organize, low barrier to present
- ISTE (International Society for Technology in Education)
- Subject-specific conferences (NSTA for science, NCTM for math)
- District PD days — districts are actively looking for session leaders

---

## AUTOMATED OUTREACH SYSTEM

### Architecture
An agentic system built on the Claude API that:
1. Monitors target channels for relevant discussions
2. Drafts contextually appropriate responses
3. Posts content that leads back to Bright Standard
4. Never repeats the same message or posts too frequently
5. Reports what it posted and the engagement it got

### The agents

**Agent 1: Reddit Content Agent**
- Monitors: r/Teachers, r/Education, r/science_education, r/MathTeachers, r/ELATeachers
- Trigger conditions: threads about lesson planning, TPT complaints, materials quality, budget constraints, differentiation, ADHD/ELL accommodations
- Action: drafts a response that addresses the specific thread with relevant content from Bright Standard
- Constraint: never posts the same lesson twice in the same subreddit within 30 days. Never posts more than 3 times per day total. Always provides genuine value before any link.

**Agent 2: TPT Creator Outreach Agent**
- Input: `tpt_creator_outreach_list.json` (generated by scraper)
- Action: for each creator, drafts Email 1 (the offer) and schedules Email 2 (30 days later if no response)
- Uses the email templates in `HAIKU_PROMPT.md` Phase 4
- Tracks: sent, opened (if tracking available), responded, certified, rejected

**Agent 3: Content SEO Agent**
- For each new certified lesson added to Bright Standard, generates:
  - Pinterest pin description (150 chars, includes grade/subject/Five Checks claim)
  - Google-optimized meta description
  - Twitter/X post
  - Facebook post (slightly longer, more personal)
- Does NOT post — generates drafts for human approval or batch approval

**Agent 4: Community Monitoring Agent**
- Monitors Reddit + Facebook + Twitter for mentions of: "TPT", "Teachers Pay Teachers", "lesson quality", "lesson plans grade [3-8]", "differentiated instruction", "ADHD classroom"
- Flags threads where Bright Standard content is directly relevant
- Drafts response for human review before posting

### Technical implementation

**Stack:**
- Claude API (claude-haiku for drafts, claude-sonnet for complex responses)
- Supabase for state tracking (what was posted, when, engagement)
- Edge Function as the scheduler/runner
- Email: Resend (simple API, reasonable pricing, warm reputation)
- Reddit: r/Teachers has no official API access without account; posting requires authenticated account + manual rate limiting

**Database tables needed:**
```sql
outreach_queue (
  id UUID,
  channel TEXT, -- 'reddit' | 'email' | 'facebook' | 'pinterest'
  target TEXT, -- subreddit name, creator email, etc.
  content_type TEXT, -- 'response' | 'outreach_email' | 'pin' | 'post'
  draft_content TEXT, -- what the agent wrote
  lesson_id UUID, -- which lesson it's promoting
  status TEXT, -- 'draft' | 'approved' | 'sent' | 'failed'
  scheduled_at TIMESTAMPTZ,
  sent_at TIMESTAMPTZ,
  approved_by UUID,
  notes TEXT
);

outreach_results (
  id UUID,
  queue_id UUID REFERENCES outreach_queue,
  engagement_score INT, -- clicks, upvotes, replies, opens
  conversion BOOLEAN, -- did it result in a signup?
  recorded_at TIMESTAMPTZ
);
```

**Edge Function: `draft-outreach-content`**
- Input: `{channel, target, lesson_id, context}` where context is the thread/post being responded to
- Process: fetch lesson from DB → construct prompt → call Claude API → store draft in outreach_queue
- Output: `{draft_id, draft_content}` — human reviews in the Bright Standard admin panel

**The human-in-the-loop design:**
No automated posting without approval — yet. The first phase is: agent drafts, human approves in under 30 seconds (just click approve), agent posts. Once the patterns are trusted, certain categories (Pinterest pins, SEO descriptions) can be auto-posted without approval.

---

## GO-TO-MARKET SEQUENCE

### Phase 0 — Before anything (right now)
Requirements before any outreach:
- [ ] At least 50 certified lessons (currently 0 — content factory needed)
- [ ] Landing page (unauthenticated) showing the product
- [ ] Five Checks scores visible on lesson cards
- [ ] At least one lesson in each of: Math, ELA, Science, Social Studies
- [ ] Subscribe button that actually works ($99/year)

Do NOT start marketing before these exist. Every teacher who arrives at a site with 31 lessons and no certified content will leave and not return.

### Phase 1 — Soft launch (50-100 lessons, 20+ certified)
**Target:** 500 teacher accounts in 30 days
**Channels:** Reddit only. r/Teachers and r/science_education.
**Content:** The teacher who built the fractions lesson that surfaces Egyptian mathematics. The photosynthesis lab that costs $0. The Reconstruction lesson that shows three families' experiences.
**Not yet:** email campaigns, social media, press outreach

**Reddit posting cadence:**
- 1 post per subreddit per week maximum
- Each post: a specific lesson with a specific angle
- Always in "value-first" format — the lesson is the content, Bright Standard is the source
- Always respond to every comment on the post

### Phase 2 — Structured outreach (100+ certified lessons)
**Target:** 2,000 teacher accounts, first 50 district conversations
**Channels:** Reddit + Facebook groups + TPT creator outreach email
**TPT creator outreach:** Email 1 to top 200 creators by review count
**Content:** The "I scored 200 TPT lessons" research post (based on actual data from scraper)
**District:** Contact 5-10 curriculum directors in high-priority districts (Title I, active HQIM adoption processes)

### Phase 3 — Press and partnership (500+ certified lessons)
**Target:** First paying district contract. 10,000 teacher accounts.
**Channels:** Education press (EdSurge, EdWeek Market Brief), podcast appearances, conference presence
**The story:** "A teacher-built quality standard for lesson plans is changing how teachers evaluate content — and competing with TPT for $1"
**The data:** Comparison of Five Checks scores between TPT bestsellers and Bright Standard certified lessons

---

## THE CONTENT MARKETING STRATEGY

Every piece of content is a lesson or a lesson-related insight. Never generic EdTech content.

**Content types that work:**

1. **The lesson itself** — post a certified lesson directly. Grade, subject, Five Checks scores visible. Free to use.

2. **The improvement case study** — "I took this TPT bestseller and improved it against the Five Checks framework. Here's what I added and why it matters."

3. **The subject deep-dive** — "How a fractions lesson can score 5/5 on Perspectives: the Egyptian notation connection, the imperial/metric divide, and who gets to decide what math looks like."

4. **The data post** — "We scored 200 science lessons on TPT. Here's the distribution. Here's what 64% of them are missing."

5. **The teacher story** — "A Title I teacher in CCSD uses zero-cost versions of every lesson. Here's how the budget alternative system works and why it matters."

**Content that doesn't work:**
- Product features (no one cares)
- "Excited to announce" (no one cares)
- Generic education takes (no differentiation)
- Anything that sounds like a company

---

## DISTRICT SALES STRATEGY

### Who to contact
- District curriculum directors (not superintendents first)
- Curriculum coordinators in subject areas (Science Coordinator, Math Coordinator)
- Title I coordinators (equity angle — budget alternatives)
- Special Education directors (Kombra Care integration, accessibility)

### The pitch (30 seconds)
"We've built an objective quality framework for instructional materials that your teachers are already using on TPT. We can score your entire supplemental materials library against our five criteria in 48 hours, give you a priority improvement list, and provide the improvements at [per-student price]/year. The first audit is free."

### The data they need for their board
- EdReports only covers full curriculum programs — not the supplemental materials teachers actually use
- 64% of most-used TPT content scores below 3 on at least one of five quality dimensions
- Bright Standard is the only system that scores individual lessons at scale against criteria that include cultural responsiveness, budget accessibility, and cognitive rigor
- The improvement service costs [X] per teacher per year vs $895 average teacher out-of-pocket spending

### Reference data for the equity argument
- 97% of teachers report their school supply budget doesn't cover what their students need
- Teachers at schools serving majority students of color spend more out-of-pocket per year
- Budget alternatives embedded in every lesson means $0/student options for every lesson in the district library
- English Language Learners acquire knowledge faster using grade-level content with supports (established research)

---

## AUTOMATED OUTREACH: CLAUDE API AGENT SPEC

For the planner/tech build conversations to implement:

### Agent 1: Reddit Value Poster

**How it works:**
1. Cron job (daily) calls the agent
2. Agent queries Supabase for: lessons added in the last 7 days that aren't yet posted to Reddit
3. For each lesson, agent calls Claude API:

```
System: You are a teacher on Reddit sharing a lesson you're genuinely excited about.
You never sound like marketing. You lead with the specific thing that makes this lesson 
interesting — the fractions insight, the $0 materials approach, the cultural angle.
You mention Bright Standard casually as where you found it.
Write a Reddit post for r/[TARGET_SUBREDDIT] about this lesson.
Max 200 words. Personal voice. Specific claim in the first sentence.
Do not use: "excited to share", "check out", "we built", any marketing language.
```

4. Draft stored in `outreach_queue` with status 'draft'
5. Email/notification sent to Michelle for 30-second approval
6. On approval: post via Reddit API (requires Reddit account + OAuth)

**Rate limits enforced in code:**
- Max 1 post per subreddit per 7 days
- Max 3 total posts per day across all channels
- Min 48 hours between any two posts to the same target

### Agent 2: Creator Email Drip

**Phase 1 (30 days after scraper data is loaded):**
```
Input: tpt_creator_outreach_list.json (sorted by outreach_priority: high/medium/low)
For each creator with outreach_priority='high':
  1. Generate personalized Email 1 using their worst-scoring product as context
  2. Store in outreach_queue
  3. Send via Resend API after Michelle approval
  4. Record sent_at
```

**Phase 2 (30 days after Email 1):**
```
For each creator who received Email 1 but has not created a creator_profile:
  1. Generate Email 2 (competitive notice)
  2. Reference any Bright Standard certified alternative we've published for their topic
  3. Send via Resend API
  4. Record sent_at
```

### What Claude API is used for (cost estimate)
- Reddit draft: 1 call per lesson per subreddit = $0.001 (Haiku)
- Creator email: 1 call per creator = $0.001 (Haiku)  
- Community monitoring analysis: 10 calls/day = $0.01/day
- Total estimated: under $5/month at current scale

---

## SEO STRATEGY

Every lesson detail page at `/lesson/:id` should be:
- Publicly accessible (no auth required to read)
- SEO-optimized with: title, grade, subject, Five Checks scores in meta
- Schema.org markup for educational content
- Indexed by Google

**Target keywords:**
- "[subject] lesson plan grade [N]" — high volume, direct intent
- "[subject] lesson plan free" — budget-motivated
- "[topic] lesson plan Five Checks certified" — owns the brand term
- "TPT alternative [subject]" — competitive capture

**The SEO advantage:** 200+ lesson pages each targeting a specific subject+grade+topic combination. Every page is a landing opportunity from search. TPT lessons are behind auth. Bright Standard lessons are public.

**Implementation needed:**
- `src/pages/PublicLessonDetail.tsx` — unauthenticated version of LessonDetail
- React Helmet or similar for meta tags per lesson
- Sitemap.xml generation (script that reads all public lessons)
- robots.txt (allow all)

---

## METRICS THAT MATTER

**Week 1-4 (soft launch):**
- Unique teacher accounts created
- Lessons viewed (without signup)
- Lessons downloaded/saved
- Upload flow completion rate
- Chrome extension installs

**Month 2-3:**
- Teacher subscription conversions (goal: 100 in month 2)
- District conversations started
- TPT creators who created accounts
- Lesson rating average across the library
- Certified lesson count (goal: 50+ by month 2)

**Month 4-6:**
- Monthly recurring revenue (MRR)
- Net promoter score (teacher survey)
- Content volume: certified lessons across all subjects
- First district contract signed

**What NOT to measure early:**
- Total page views (vanity)
- Social followers (vanity)
- Press mentions (vanity)
- Anything that doesn't directly correlate to a teacher finding a lesson they actually use
