# BRIGHT STANDARD — MASTER PLAN DOCUMENTS
# For handoff to Planner, Researcher, and Tech Build conversations
# Current date: May 2026

This repo contains the complete strategic plan across four domains.
Each document is self-contained for handoff to a dedicated conversation.

## Documents

1. **PLAN_1_SCRAPING.md** — TPT data acquisition: what failed, why, and the correct architecture
2. **PLAN_2_UX_DESIGN.md** — User experience, component library brief, visual architecture
3. **PLAN_3_TECH_INFRASTRUCTURE.md** — Complete technical spec: every component, dependency, test
4. **PLAN_4_MARKETING_OUTREACH.md** — Go-to-market, channel strategy, automated outreach system

## Live State (as of May 2026)

- **Site:** https://thebrightstandard.com (Netlify, deploy 6a086e6e)
- **Repo:** michellebangura/brightstandard (main)
- **Database:** Supabase project gexxdsiowglhrxkkvsrv
- **Lessons:** 31 published, 0 certified (all score below 4 on at least one dimension)
- **Subject coverage:** Science (14), Math (9), ELA (2), Social Studies (2), other (4)
- **Edge Functions:** batch-score-lessons (v2), parse-lesson-upload, score-content, enrich-lesson-materials, bright-standard-score, generate-parent-email
- **Chrome Extension:** michellebangura/bright-standard-extension (ready to load unpacked)
- **TPT Pipeline:** michellebangura/tpt-content-pipeline (scraper + Haiku prompt)

## Critical Unblocked Item

ANTHROPIC_API_KEY is set in Supabase Edge Function secrets. All AI functions are live.
The batch scoring bug (Haiku trailing text after JSON) has been fixed with extractJSON() regex.
31 lessons are scored. None certified. The two closest need Inclusivity improved from 3 to 4.
