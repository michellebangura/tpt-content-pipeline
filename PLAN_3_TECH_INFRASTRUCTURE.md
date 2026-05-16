# PLAN 3: TECHNICAL INFRASTRUCTURE
## Every component, prerequisite, dependency, function, and test
## For: Tech Build conversation

---

## SYSTEM OVERVIEW

**Live URL:** https://thebrightstandard.com
**Stack:** React 18 + Vite + TypeScript / Supabase (Postgres + Edge Functions) / Netlify
**Repo:** michellebangura/brightstandard (main branch)
**Deploy:** GitHub Actions → Netlify (auto-deploys on push to main)
**Supabase project:** gexxdsiowglhrxkkvsrv

---

## WHAT IS BUILT AND WORKING

### Frontend pages (all deployed)
| Route | File | Status |
|---|---|---|
| `/` | Landing.tsx | MISSING — redirects to /hub (unauthenticated landing page needed) |
| `/login` | Login.tsx | Working |
| `/hub` | LearningHub.tsx | Working — Five Checks filter, Bloom's, Teach Today, real DB queries |
| `/lesson/:id` | LessonDetail.tsx | Working — 2-column layout, sequence rail, real DB queries |
| `/upload` | Upload.tsx | Working — AI file parsing, Step 3.5 budget alternatives |
| `/creators` | CreatorPortal.tsx | Working — score any TPT URL, improvement suggestions |
| `/creators/improve` | CreatorPortal.tsx | Working — deep-link from Chrome extension |
| `/debrief` | VoiceDebrief.tsx | Working — full-screen dark, teacher end-of-day |
| `/students` | StudentPulse.tsx | Surface level — deprioritized |
| `/wellbeing` | Wellbeing.tsx | Surface level — deprioritized |
| `/tasks` | TaskDecomp.tsx | Surface level — deprioritized |
| `/profile` | Profile.tsx | Working |
| `/settings` | Settings.tsx (inline) | Working |

### Edge Functions (all ACTIVE in Supabase)
| Function | Version | Purpose | Status |
|---|---|---|---|
| `batch-score-lessons` | v2 | Score all unscored lessons in DB | Working — extractJSON() fix applied |
| `bright-standard-score` | v5 | Score a single submitted lesson | Working |
| `parse-lesson-upload` | v1 | PDF/DOCX → structured lesson JSON | Working |
| `score-content` | v1 | TPT URL/description → Five Checks | Working |
| `enrich-lesson-materials` | v1 | Materials list → budget alternatives | Working |
| `generate-parent-email` | v2 | Lesson → parent communication email | Working |
| `bulk-standards-ingest` | v1 | Batch standards population | Working |

### Database tables (all in Supabase public schema)
| Table | Rows | Status |
|---|---|---|
| lessons | 31 | Live — all scored, 0 certified |
| reviews | 17 | Live |
| teacher_profiles | 1 | Live |
| tpt_scans | 10 | Live — seed data only |
| creator_profiles | 0 | Schema exists, no UI |
| content_factory_queue | 0 | Schema exists, no pipeline |
| favorites | 0 | Schema exists, no UI |
| voice_entries | 0 | Schema exists, VoiceDebrief deprioritized |
| student_pulse | 0 | Deprioritized |
| curriculum_plan_items | 0 | Schema exists, HIGH PRIORITY UI needed |
| educator_profiles | 0 | Schema exists, no /educator/:id route |

### Chrome Extension (separate repo)
- **Repo:** michellebangura/bright-standard-extension
- **Status:** Ready to load unpacked in Chrome developer mode
- **Blocking:** Missing `icons/icon16.png`, `icon48.png`, `icon128.png` for Chrome Web Store
- **Function:** Scrapes TPT product pages, calls `score-content`, renders Five Checks panel

---

## WHAT IS NOT BUILT (priority order)

### P0 — Blocks the core product promise

**1. Landing page (unauthenticated)**
- Route: `/` when not logged in
- Currently: redirects to `/hub` but hub requires auth → redirects to `/login`
- Teachers arriving from Google/social need to see the product before signing up
- Required: File `src/pages/Landing.tsx` + conditional routing in App.tsx

**2. Five Checks scores visible on LessonCard**
- Currently: LessonCard shows title, subject, grade, rating, duration, cost
- Missing: the Five Checks circles with actual scores
- This is THE product differentiator — invisible until you click into a lesson
- Required: update `src/components/LessonCard.tsx` to render GovernanceCircles at xs size

**3. Certified lesson visual treatment**
- Currently: certified and non-certified lessons look identical in the hub
- Missing: gold border, certified badge, visual hierarchy
- Required: CSS + LessonCard conditional styling based on `quality_scores.bright_standard_certified`

**4. Content volume (not a code problem)**
- 31 lessons, 0 subjects fully covered
- Need 200+ lessons for the product to be usable
- Solution: run the content factory (HAIKU_PROMPT.md) to generate certified lessons at scale

### P1 — Core flows incomplete

**5. Curriculum Sequence Visualizer**
- `curriculum_plan_items` table exists with schema
- No frontend for teachers to build or view sequences
- This is identified as highest value feature alongside lesson quality
- Required: `src/pages/CurriculumPlan.tsx` + `src/components/SequenceVisualizer.tsx`
- Route: `/plan/:id` or `/curriculum`

**6. MakeItYours — fork does not score**
- MakeItYours.tsx forks the lesson to a new record
- Missing: calls `bright-standard-score` on the fork, updates `quality_scores` on the new lesson
- Required: add scoring call after successful fork insert in `MakeItYours.tsx`

**7. Average rating trigger**
- Reviews insert but `lessons.average_rating` doesn't update
- Trigger is created but may not be firing
- Required: verify trigger `on_review_change` exists and fires on INSERT

**8. Subscription + payment**
- No Stripe integration
- Creator Portal shows "$9/mo" button → goes nowhere
- Teacher subscription "$99/year" doesn't exist
- Required: Stripe checkout, webhook handler, subscription status on user profile

**9. Educator profile pages**
- `educator_profiles` table built
- No `/educator/:id` route
- Required: `src/pages/EducatorProfile.tsx` + route in App.tsx

**10. District portal**
- No distinct UI for district curriculum directors
- Districts need: bulk upload endpoint, scoring dashboard, improvement priority list, per-student billing
- Required: `src/pages/DistrictPortal.tsx` + new Supabase tables for district accounts

### P2 — Strategic features

**11. Chrome Extension icons**
- manifest.json references `icons/icon16.png` etc.
- Files don't exist → extension can't submit to Chrome Web Store
- Required: generate PNG icons (BS checkmark on dark background, 3 sizes)

**12. Content factory Edge Function**
- `content_factory_queue` table has rows marked 'queued'
- No function that takes a queued item, generates a lesson, scores it, publishes or rejects
- Required: `generate-certified-lesson` Edge Function

**13. Teach Today flag on lessons**
- Filter exists in SearchBar UI
- DB column `teach_today` referenced but not computed
- Required: DB trigger that sets `teach_today = true` when `prep_time_minutes = 0 AND requires_materials = false`

**14. Automated outreach system**
- See PLAN_4_MARKETING_OUTREACH.md for full spec
- Required: outreach_queue table + send-outreach Edge Function + scheduling

---

## COMPLETE DEPENDENCY MAP

```
Landing Page
  └── App.tsx conditional routing (built — needs Landing.tsx)
  └── Landing.tsx (NOT BUILT)

LessonCard with scores
  └── GovernanceCircles.tsx (BUILT — needs to be added to LessonCard)
  └── LessonCard.tsx (update needed)
  └── LearningHub.tsx (passes quality_scores to card — update needed)

Curriculum Sequence Visualizer
  └── curriculum_plan_items table (schema exists)
  └── SequenceVisualizer.tsx (NOT BUILT)
  └── CurriculumPlan.tsx (NOT BUILT)
  └── Route /plan (NOT BUILT)

Subscription + Payment
  └── Stripe account (NEEDS SETUP — Stripe MCP available)
  └── Stripe product/price creation
  └── Stripe checkout session Edge Function (NOT BUILT)
  └── Stripe webhook handler Edge Function (NOT BUILT)
  └── User subscription status in DB (column needed on profiles table)
  └── Subscription gate on Creator Portal "get suggestions" (NOT BUILT)

District Portal
  └── district_accounts table (NOT CREATED)
  └── district_lessons table (NOT CREATED — links districts to lesson access)
  └── DistrictPortal.tsx (NOT BUILT)
  └── Route /district (NOT BUILT)

Content Factory
  └── content_factory_queue table (EXISTS)
  └── generate-certified-lesson Edge Function (NOT BUILT)
  └── Scheduling mechanism (cron job or queue worker)

Automated Outreach
  └── outreach_queue table (NOT CREATED)
  └── send-outreach Edge Function (NOT BUILT)
  └── Email service (Resend or Postmark — not configured)
  └── Reddit/social posting agent (NOT BUILT — see PLAN_4)
```

---

## BUILD SEQUENCE (strict order — each depends on the previous)

### Sprint 1: Fix the trust gap (what teachers see in 3 seconds)
1. Add Five Checks circles to LessonCard (GovernanceCircles at xs size)
2. Add certified visual treatment to LessonCard (gold border when certified)
3. Build unauthenticated Landing.tsx with live lesson components
4. Add Teach Today DB trigger (computed column)
5. Test: load /hub, verify scores visible on cards, verify certified styling

### Sprint 2: The improvement pipeline (the actual product)
6. MakeItYours scoring call after fork
7. Curriculum Sequence Visualizer (SequenceVisualizer.tsx + CurriculumPlan.tsx)
8. Content factory Edge Function (generate-certified-lesson)
9. Run content factory for 50 lessons across 5 subjects
10. Test: upload a PDF, get improvement suggestions, see score improve

### Sprint 3: Revenue infrastructure
11. Stripe setup (product, prices, checkout session function)
12. Stripe webhook handler (update user subscription status)
13. Subscription gate on Creator Portal
14. District portal (3-screen UI: upload, score dashboard, priority list)
15. Test: complete purchase flow end to end in Stripe test mode

### Sprint 4: Scale and distribution
16. Chrome Extension icons → Chrome Web Store submission
17. Automated outreach Edge Function
18. Reddit posting agent (Claude API agentic)
19. Educator profile pages
20. Test: full journey from TPT page → extension score → BS certified alternative

---

## TEST SCRIPTS FOR EACH CRITICAL PATH

### Test 1: Five Checks scoring pipeline
```bash
# Score a single lesson
curl -X POST https://gexxdsiowglhrxkkvsrv.supabase.co/functions/v1/score-content \
  -H "Content-Type: application/json" \
  -d '{"title":"Photosynthesis Lab","description":"Students use chromatography to separate leaf pigments","grade":"4","subject":"Science","scan_source":"extension","store_result":false}'

# Expected: JSON with scores.rigor, scores.inclusivity, scores.perspective, scores.empathy, scores.thinking
# All integers 0-5. certified: true if all >= 4.
```

### Test 2: Batch scoring all lessons
```bash
curl -X POST https://gexxdsiowglhrxkkvsrv.supabase.co/functions/v1/batch-score-lessons \
  -H "Content-Type: application/json" \
  -d '{}'
# Expected: {"total":N,"certified":N,"needs_improvement":N,"errored":0,"results":[...]}
# errored should be 0. If not, check ANTHROPIC_API_KEY in Supabase secrets.
```

### Test 3: Material enrichment
```bash
curl -X POST https://gexxdsiowglhrxkkvsrv.supabase.co/functions/v1/enrich-lesson-materials \
  -H "Content-Type: application/json" \
  -d '{"materials_raw":"Spinach leaves, 4 per student, $0.30\nRubbing alcohol, 2tsp, $0.08","lesson_title":"Photosynthesis Lab","subject":"Science"}'
# Expected: enriched_materials array with zero_cost, low_cost, digital for each item
```

### Test 4: File upload parsing
```bash
# In browser: navigate to /upload, drop a PDF lesson plan
# Expected: form pre-fills with extracted title, description, grade, objectives
# If empty fields: check parse-lesson-upload function logs in Supabase dashboard
```

### Test 5: DB query for Hub
```sql
-- In Supabase SQL editor:
SELECT id, title, subject, grade_levels,
  quality_scores->>'rigor' as rigor,
  quality_scores->>'bright_standard_certified' as certified
FROM lessons 
WHERE status = 'published' AND is_public = true
ORDER BY (quality_scores->>'rigor')::int DESC NULLS LAST
LIMIT 10;
-- Expected: 10 rows with scores. certified = 'true' for 0 rows currently.
```

### Test 6: Teach Today filter
```sql
-- After trigger is created:
SELECT COUNT(*) FROM lessons WHERE teach_today = true;
-- Expected: lessons with prep_time_minutes = 0 AND requires_materials = false
```

---

## ENVIRONMENT VARIABLES (all set)

| Variable | Where set | Value |
|---|---|---|
| ANTHROPIC_API_KEY | Supabase Edge Function secrets | Set (digest d126ae5e1h) |
| SUPABASE_URL | Supabase (auto) | gexxdsiowglhrxkkvsrv.supabase.co |
| SUPABASE_SERVICE_ROLE_KEY | Supabase (auto) | Set |
| VITE_SUPABASE_URL | Netlify env vars | Set |
| VITE_SUPABASE_ANON_KEY | Netlify env vars | Set |
| NETLIFY_AUTH_TOKEN | GitHub repo secrets (brightstandard) | Set |
| NETLIFY_SITE_ID | GitHub Actions workflow | ff7ac3d6-8680-4dfb-bc37-4b831526a3a0 |

---

## THE CURRICULUM SEQUENCE VISUALIZER — DETAILED SPEC

This is the highest-value feature not yet built. Full specification:

### What it is
A visual tool that shows how lessons connect in a subject progression. Teachers can:
1. Browse the auto-generated sequence (from DB — same subject, adjacent grades)
2. Build their own sequence (drag-and-drop lessons into an ordered plan)
3. See the Bloom's level progression across the sequence
4. Share the sequence as a URL with other teachers

### Data model (table already exists)
```sql
curriculum_plan_items:
  id UUID
  plan_id UUID -- groups items into one sequence
  lesson_id UUID -- references lessons
  position INT -- order in the sequence
  grade_focus INT -- which grade in the lesson's range this plan targets
  notes TEXT -- teacher annotation
  created_by UUID
  created_at TIMESTAMPTZ
```

### UI: SequenceVisualizer.tsx
**Renders as:**
- Horizontal timeline for desktop
- Vertical list for mobile
- Each node: LessonCard (compact) at its Bloom's elevation
- Connecting arrows between nodes
- Bloom's level visual: Remember at bottom, Create at top — each lesson card positioned vertically based on its highest Bloom's level
- Five Checks mini-display on each card

**Interactions:**
- Click a lesson: expand to show learning objectives + output artifact
- Add a lesson: search modal → drag to position
- Remove: × button on each card
- Reorder: drag-and-drop (react-beautiful-dnd)
- Share: copy URL with plan_id

### Auto-generated sequences
When a teacher views a lesson detail page, the sequence rail shows auto-generated before/after based on:
1. Same subject
2. Adjacent grade level (current ± 1)
3. Related canonical themes
4. This is already implemented as a DB query in LessonDetail.tsx

### Teacher-built sequences
The full Curriculum Plan page (`/curriculum`) allows teachers to:
1. Create a new plan
2. Search and add lessons
3. Reorder
4. Save to their profile
5. Share as a URL

This needs: `src/pages/CurriculumPlan.tsx` + `src/components/SequenceVisualizer.tsx` + `src/components/LessonSearch.tsx`

---

## STRIPE INTEGRATION SPEC

### Products to create
1. **Teacher Pro** — $99/year
   - Access to improvement suggestions on uploaded content
   - Unlimited uploads
   - Early access to certified content

2. **District License** — per-student/year (TBD: $3-5/student)
   - All teacher features for all teachers in district
   - District portal: bulk upload, scoring dashboard, priority list
   - Dedicated account manager (manual for now)

### Implementation
1. Create products in Stripe dashboard (or via Stripe MCP)
2. Create `create-checkout-session` Edge Function:
   - Accepts: user_id, price_id
   - Creates Stripe checkout session
   - Returns: checkout URL
3. Create `stripe-webhook` Edge Function:
   - Handles: checkout.session.completed, customer.subscription.deleted
   - Updates: profiles.subscription_tier, profiles.subscription_expires_at
4. Add columns to profiles table: `subscription_tier`, `subscription_expires_at`, `stripe_customer_id`
5. Gate in Creator Portal: check `subscription_tier = 'pro'` before showing detailed suggestions

### Stripe MCP is connected
Use `Stripe:create_product`, `Stripe:create_price`, `Stripe:create_payment_link` tools directly.

---

## WHAT TECH BUILD HANDLES VS WHAT GOES TO OTHER CONVERSATIONS

**Tech Build owns:**
- All React component updates
- All Edge Function deployments
- All DB migrations
- Stripe integration
- Chrome Extension icons
- Content factory pipeline
- Automated outreach Edge Functions

**Researcher/Data conversation owns:**
- Running the TPT scraper
- Scoring the scraped products
- Identifying priority targets
- Generating the outreach contact list

**Design conversation (Gemini) owns:**
- Visual component library HTML/CSS
- Landing page visual design
- Marketing assets

**Planner conversation owns:**
- Coordinating the above
- Tracking which sprint items are complete
- Sequencing handoffs
