# PLAN 2: UX, DESIGN & COMPONENT LIBRARY
## Visual architecture, design brief, component specifications
## For: Design Conversation (Gemini visual component library build)

---

## WHAT GEMINI BUILT FOR PBP (REFERENCE STANDARD)

For the Purpose Built Press brand, Gemini received a comprehensive design brief and produced a visual component library that modernized the UX, established visual hierarchy, and created design consistency across all products. The Bright Standard equivalent needs the same treatment.

The key difference: PBP is a publishing brand (warm, editorial, print-like). Bright Standard is a teaching platform (warm but functional, signal-heavy, designed for 7-minute planning sessions).

---

## BRAND POSITIONING

**Tagline:** TPT but better and free
**Tone:** Peer-to-peer. A good teacher talking to another teacher. Direct, warm, specific, not corporate.
**The product feeling:** You found the right thing. It works for every kid in your room. You didn't have to make it.

**What it is NOT:**
- Not academic / institutional (that's EdReports)
- Not corporate EdTech (that's HMH, Amplify, Pearson)
- Not playful/childlike (that's TPT aesthetic — bright, busy, clip-art heavy)
- Not dark/minimal/developer (that's Linear, Vercel)

**What it IS:**
- Warm authority — like a trusted colleague who also happens to know more than you
- Earned trust — the Five Checks scores make every design decision auditable
- Human scale — built for a teacher at 6am with 7 minutes

---

## DESIGN SYSTEM FOUNDATIONS (from dkb research, already derived)

```
Background:   #F7F4EF  (warm cream — 67.6% reading comprehension vs 56.5% on white/blue)
Text primary: #1A1410  (warm near-black — eliminates clinical pure-black)
Text secondary: #5C4F42
Text tertiary: #9A8B7E
Accent:        C4622D  (warm amber — authority state, NOT blue which signals EdTech)
BG inverse:   #1A1410
BG elevated:  #FEFCF8
BG recessed:  #EDE9E1

Five Checks colors (research-derived, not decorative):
  Rigor:          #3B82F6  (blue  — cognitive demand)
  Inclusivity:    #22C55E  (green — access and equity)
  Perspectives:   #A855F7  (purple — multiple viewpoints)
  Empathy:        #F97316  (orange — emotional intelligence)
  Critical Thinking: #EC4899 (pink — reasoning and questioning)

Typography:
  Display: Fraunces (serif, warm editorial authority)
  Body:    DM Sans (clean, legible, teacher-friendly at small sizes)
  Mono:    IBM Plex Mono (data, scores, codes)
  Accent:  Caveat (handwritten — cognitive notes only, never UI)

Spacing scale: 4px base unit — 4, 8, 12, 16, 24, 32, 48, 64, 80, 96, 120
Border radius: 2px containers, 2px interactive, 18px pills (deliberate anti-template)
Shadow: none in default state (only on hover — depth means elevation here)
Animation: cubic-bezier(0.22, 1, 0.36, 1) 150ms for interactions
```

---

## CRITICAL UX PROBLEMS TO SOLVE

### Problem 1: The Five Checks scores are invisible at browse level
The most important thing about each lesson — whether it passes the quality standard — is buried inside the lesson detail page. A teacher browsing the Learning Hub cannot see scores without clicking into each lesson.

**Required fix:** Five colored circles with numeric scores visible on each LessonCard in the hub. Small but present. At a glance: 5-4-4-5-4. That's the entire product promise visible in two seconds.

### Problem 2: The hub looks like every other content platform
LearningHub currently: search bar + horizontal scroll rows of cards. This is exactly what TPT looks like, what Khan Academy looks like, what every content platform looks like. There is nothing visually that signals "this content has been evaluated."

**Required fix:** The certified badge must be the dominant visual language of the hub. A lesson that is certified looks different from one that is not. The hub should feel like a curated gallery, not a marketplace.

### Problem 3: The upload flow doesn't celebrate what it's doing
Step 3.5 (budget alternatives) is functionally correct but visually looks like a form. The experience should feel like: "Look what we just did to your lesson. In 10 seconds. For free."

**Required fix:** The budget alternatives review should be a reveal moment, not a confirmation form. Cards that flip. Before/after. The improvement is the product.

### Problem 4: No visual relationship between lessons
The sequence rail exists but is text-only cards. Teachers are visual thinkers. The "where this lesson fits" concept needs to be a visible learning path, not a list.

**Required fix:** Curriculum Sequence visualization — a horizontal timeline of lessons in the same subject progression, with the current lesson highlighted. Connected by lines. Bloom's level indicated by elevation or size.

---

## COMPONENT LIBRARY BRIEF (for Gemini visual build)

### COMPONENT 1: LessonCard
**States:** default, hover, loading/skeleton, favorited
**Must contain:**
- Lesson title (Fraunces, 16px, 2-line max with ellipsis)
- Subject tag (colored pill)
- Grade range (DM Sans, 12px)
- Duration (clock icon + minutes)
- Cost tier indicator (free / $0 tier / low cost)
- Five Checks score circles (5 × small colored circle with number, 0-5)
  - Circle fills proportionally to score (like a donut chart in miniature)
  - Color = dimension color (rigor=blue, etc.)
  - Number inside or below
- Certified badge (gold star / checkmark if all 5 scores ≥ 4)
- Output artifact name (italic, 12px, truncated)
- Average rating (if reviews exist)
- Bookmark/favorite button (top right corner)

**Visual direction:**
- Clean white card on the warm cream background
- Certified lessons: subtle gold left border or top stripe
- Non-certified: standard border
- On hover: 3px upward translate, shadow appears, border becomes accent color
- The Five Checks circles are the most distinctive element — make them legible at card size

### COMPONENT 2: Five Checks Score Display (3 sizes)
**xs (card):** 5 circles, 16px diameter, number inside 8px, tight cluster
**md (detail page hero):** 5 circles, 40px diameter, number inside, label below
**lg (governance review):** 5 circles, 64px, animated fill on mount, label + description

**Animation:** On mount, the circle fills from 0 to the score value (300ms, ease-out). This is the only animation in the system that is purely decorative — it earns it because it demonstrates what the score means visually.

**States:** empty (gray, no score), scoring (pulsing gray), scored (colored, filled), certified (gold outer ring added)

### COMPONENT 3: Curriculum Sequence Rail
A horizontal flow visualization showing the current lesson's position in a subject progression.

**Layout:**
```
[Before lesson]  →→→  [CURRENT — highlighted]  →→→  [After lesson]
 Grade 4 · 45min           Grade 4 · 50min            Grade 5 · 45min
 Science                   Science                     Science
```

**Visual spec:**
- Horizontal timeline with connecting arrows
- Current lesson: larger card, dark background (#1A1410), amber text
- Before/after: lighter cards, clickable links
- Bloom's level: subtle elevation difference (higher Bloom's = card sits higher on the timeline)
- Empty state: dashed border card with "Be the first to add one" + Upload link

### COMPONENT 4: Budget Tier Selector
**Three tiers:** Zero Cost / Low Cost / Standard
**Toggle behavior:** selecting a tier shows/hides materials by cost tier
**Visual direction:**
- Three segmented toggle buttons
- Active tier: filled dark background
- Each tier shows cost summary: "$0/student" or "≤$0.25/student"
- Below: materials table updates to show relevant items

### COMPONENT 5: Upload Step Indicator
**5 steps:** Files → Details → Materials → Budget → Review
**Current:** numbered dots with connecting lines
**Improvement needed:** 
- Current step should be more visually prominent
- Completed steps: checkmark + colored fill
- Add step description label below each dot
- Progress bar connecting them (filling as steps complete)
- Mobile: compress to progress bar only with "Step 3 of 5" label

### COMPONENT 6: Governance Review (final upload step)
The screen a teacher sees after submission showing their Five Checks scores.

**Layout:**
- Top: "Here's your score" with the lg Five Checks display
- Per dimension: score, label, the specific improvement suggestion if below 4
- Bottom: two CTAs — "Publish as-is" (secondary) and "See how to improve it" (primary)
- If certified: celebration state — confetti? Gold badge animation? "Your lesson is certified." full-width moment

**Emotional design requirement:** This screen is either a celebration or a coaching moment. It is NEVER a rejection. The language: "Here's what makes this great" (what's scored 4+) and "Here's what would make it even better" (what's below 4). Never "failed." Never "rejected."

### COMPONENT 7: Subject Tag
**Variants:** Science (blue-teal), Math (deep blue), ELA (rose), Social Studies (earth), Cross-Curricular (purple), Special Ed (gold), Life Skills (sage), SEL (peach), History (clay)
**Sizes:** xs (card), sm (filter), md (detail page)
**Shape:** pill, 2px radius

### COMPONENT 8: Certified Badge
**Sizes:** xs (12px icon on card), sm (card bottom), md (detail page hero), lg (share/embed)
**States:** certified (gold), not yet certified (gray), in review (amber pulsing)
**Text variants:** icon only / "Certified" / "Bright Standard Certified" / with score summary

### COMPONENT 9: SearchBar + Filter Row
**Current:** works functionally, visual polish needed
**Filter pills (active state):** colored background matching the filter type
  - Five Checks dimension filter: fills with that dimension's color when active
  - Teach Today toggle: iOS-style switch
  - Bloom's level: dropdown becomes filled when active
  - Budget: "$0 only" pill, active = green fill
**Active filter strip:** below the filter row, shows active filters as removable chips

### COMPONENT 10: LearningHub Layout
**Current:** search + horizontal scroll rows
**Required visual improvement:**
- Hero area: brief statement of what makes this different from TPT (1-2 lines, no jargon)
- Subject navigation: horizontal tabs or pills that filter the full view
- Certified section: visually distinct editorial section at top
- "Needs [X subject] in the next 7 minutes?" — zero-prep quickfind

---

## VISUAL DIFFERENTIATION FROM TPT

TPT visual language:
- Bright primary colors on white
- Clip art and illustrated icons everywhere
- "Cute" aesthetic — stars, hearts, rainbow gradients
- Flat hierarchy — everything looks equal
- Busy, cluttered product pages with long scrolling descriptions

Bright Standard must look completely different:
- Warm cream background (not white)
- Clean, sparse — white space is trust
- The Five Checks circles are the only colorful element and they're earned, not decorative
- Typography does the heavy lifting — no clip art, no illustrations
- Cards have clear hierarchy — title, then scores, then metadata
- The certified badge is recognizable at thumbnail size

---

## DESIGN BRIEF FOR GEMINI COMPONENT LIBRARY BUILD

**Give Gemini this prompt:**

```
You are building a React component library for Bright Standard (thebrightstandard.com) — a teacher-facing lesson quality platform. Every component uses CSS custom properties (already defined in the app). No Tailwind. No external component libraries. Pure React + CSS.

The design system is:
- Background: #F7F4EF (warm cream)
- Text: #1A1410 (warm near-black) 
- Accent: #C4622D (warm amber)
- Five Checks colors: Rigor #3B82F6, Inclusivity #22C55E, Perspectives #A855F7, Empathy #F97316, Thinking #EC4899
- Fonts: Fraunces (display), DM Sans (body), Caveat (handwritten accents only)
- Border radius: 2px on all containers, never round
- Shadow: only on hover, not default
- Animation: cubic-bezier(0.22, 1, 0.36, 1) 150ms

Build these components in sequence, each exported from its own file:
1. LessonCard (with Five Checks circles visible, certified badge, all states)
2. FiveChecksDisplay (xs/md/lg sizes, animated fill on mount)
3. CurriculumSequenceRail (horizontal timeline, Bloom's elevation)
4. BudgetTierSelector (3-tier toggle)
5. UploadStepIndicator (5-step with labels)
6. GovernanceReview (celebration + coaching states)
7. SubjectTag (all subjects, colored)
8. CertifiedBadge (all sizes, all states)
9. SearchFilterRow (active states, dimension color fills)
10. LessonHubLayout (full page composition)

For each component: props interface, default state, all variant states, hover/active/focus states, mobile responsive version. Export a Storybook-compatible story for each.

The visual bar: this must look completely different from Teachers Pay Teachers. TPT is clip-art bright colors on white. Bright Standard is warm, sparse, authoritative — the Five Checks circles are the only colorful elements and they're meaningful, not decorative.
```

---

## PAGES THAT NEED FULL VISUAL REDESIGN (priority order)

1. **Learning Hub** — the browse experience. Must show Five Checks scores on cards. Must have certified-first editorial hierarchy.
2. **Lesson Detail** — mostly built, needs visual polish: the Five Checks circles at hero size, the sequence rail as a timeline, the materials table with tier selector.
3. **Upload flow** — steps 3.5 (budget reveal) and 5 (governance review) need the emotional design treatment.
4. **Creator Portal** — the improvement service product page. This is what the $99/year proposition needs to land.
5. **Landing page** — currently doesn't exist as a separate page. Teachers arriving at thebrightstandard.com land on the Hub after auth. There should be an unauthenticated landing page that explains the product in one scroll.

---

## THE LANDING PAGE (does not exist yet)

**URL:** thebrightstandard.com (unauthenticated)
**One scroll. Five sections.**

**Section 1 — The hook (above fold):**
"Your lesson works for every student. You didn't have to modify it."
Show: a LessonCard with 5-4-5-4-4 Five Checks scores and Certified badge. Not a screenshot — the actual component rendered on the page.

**Section 2 — The proof:**
Three specific examples of what the Five Checks caught and fixed.
- A fractions lesson that got Perspectives 2 → here's the one that scores 5
- A science lesson that required $4/student → here's the zero-cost version
- An ELA lesson that had no ADHD scaffolds → here's what was added

**Section 3 — The comparison:**
Side by side. A TPT lesson (unbranded — just the content) vs the Bright Standard version. Same topic, different quality. The Five Checks scores make it objective.

**Section 4 — How it works:**
Upload your TPT purchases → we score them → we improve them → $99/year
Three steps, icons, one sentence each. No jargon.

**Section 5 — Browse free:**
Show 6 certified lessons. Click through to hub. No signup required to browse.

---

## WHAT TO HAND GEMINI VS WHAT TO HAND TECH BUILD

**Gemini:** HTML/CSS static component renders. The visual system. What things look like.

**Tech Build:** React implementation of those components. The Supabase queries behind them. The state management. The API calls.

The workflow: Gemini builds the visual reference → Tech Build implements it → QA against the visual spec.
