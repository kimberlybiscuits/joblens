# JobLens — Guided Build Plan

## Context

You're building JobLens yourself as a learning project. You have your own terminal open and are driving the implementation. I'm here as a guide — answering questions, explaining concepts, reviewing your code, and helping you debug when you get stuck.

The full project spec (tech stack, architecture, phases) is below, followed by the step-by-step walkthrough.

## How We Work

- **You type the commands and write the code** in your terminal
- **I guide you step-by-step** — explaining what to do next, why, and what each piece does
- **You ask me when stuck** — errors, design questions, "what should this look like?"
- **I review your code** when you share it or ask me to look at files

---

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| **Backend** | Python + FastAPI | Lightweight, modern, great for async scraping. Beginner-friendly. |
| **Frontend** | HTMX + Tailwind CSS | Minimal JS, server-driven UI. Lightweight and fast to build. |
| **Database** | SQLite | Zero setup, file-based, perfect for local/self-hosted. |
| **Scraping** | BeautifulSoup + httpx (+ Playwright for JS-heavy sites) | Handles both static and dynamic job boards. |
| **Local AI** | Ollama (Mistral 7B or Phi-3) | Runs on 8-16GB RAM without GPU. Free, private, local. |
| **Task scheduling** | APScheduler | For daily/periodic job fetches. Lightweight, in-process. |

## Architecture

```
┌─────────────────────────────────────────────┐
│                 Browser (HTMX)              │
├─────────────────────────────────────────────┤
│              FastAPI Backend                │
│  ┌──────────┐ ┌──────────┐ ┌─────────────┐ │
│  │ Search & │ │ Profile  │ │ CV/Cover    │ │
│  │ Results  │ │ Wizard   │ │ Letter Gen  │ │
│  └────┬─────┘ └────┬─────┘ └──────┬──────┘ │
│       │             │              │        │
│  ┌────▼─────────────▼──────────────▼──────┐ │
│  │           SQLite Database              │ │
│  │  jobs | profiles | searches | docs     │ │
│  └────────────────────────────────────────┘ │
│       │                            │        │
│  ┌────▼──────────┐  ┌─────────────▼──────┐ │
│  │  Job Scrapers │  │  Ollama (Local AI) │ │
│  │  (per-board)  │  │  Mistral 7B        │ │
│  └───────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Job Board Sources

| Source | Method | Priority | Notes |
|--------|--------|----------|-------|
| RemoteOK | JSON API | High | Free, no auth needed |
| HN Who's Hiring | HN API | High | Monthly threads, easy to parse |
| EuroBrussels | HTML scrape | High | Key for EU roles |
| Impactpool | HTML scrape | High | UN/intl org jobs |
| eu-careers.europa.eu | RSS/HTML | High | Official EU job portal |
| EURemoteJobs | Playwright | High | JS-rendered (WordPress/WP Job Manager) |
| UNJobs/UNTalent | HTML scrape | Medium | International org roles |
| RemoteRocketship | HTML scrape | Medium | Good remote tech roles |
| Working Nomads | RSS feed | Medium | Has RSS, easy integration |
| Wellfound | HTML scrape | Low | May require auth |
| Built In | HTML scrape | Low | Good content but may block |

---

## Walkthrough Steps

### Step 1: Project Setup
- Create `joblens/` directory, init git, create venv
- Write `pyproject.toml` with dependencies
- Create the folder structure (`app/`, `app/scrapers/`, `app/routes/`, `app/templates/`, `static/`)
- Create `.gitignore` and minimal `README.md`

### Step 2: Hello World with FastAPI + HTMX
- Write a minimal `app/main.py` with one route
- Create `app/templates/base.html` with Tailwind CDN
- Run it with `uvicorn app.main:app --reload` and see it in the browser
- **Learning checkpoint:** Understand how FastAPI serves HTML via Jinja2 templates

### Step 3: Database Layer
- Write `app/database.py` — SQLite connection, create tables (jobs, sources, search_queries)
- **Learning checkpoint:** Understand how SQLite works with Python, table schemas

### Step 4: First Scraper (RemoteOK)
- Write `app/scrapers/base.py` — abstract base class
- Write `app/scrapers/remoteok.py` — fetch JSON API, normalize to common schema
- Test it standalone: run the scraper, see jobs in the DB
- **Learning checkpoint:** async HTTP with httpx, data normalization, base class pattern

### Step 5: Display Jobs in the Browser
- Write `app/routes/jobs.py` — query DB, return HTML
- Write `app/templates/jobs.html` — list jobs with HTMX search
- **Learning checkpoint:** HTMX partial responses, server-driven UI

### Step 6: Search & Filtering
- Add multi-keyword search, filters (source, date, location)
- Saved search profiles
- **Learning checkpoint:** SQL full-text search or LIKE queries, HTMX form submission

### Step 7: More Scrapers
- EuroBrussels (HTML scraping with BeautifulSoup)
- Impactpool, HN Who's Hiring
- Deduplication logic
- **Learning checkpoint:** HTML parsing, handling different site structures

### Step 8: Scheduled Fetching
- APScheduler integration for periodic fetches
- Manual "fetch now" button
- **Learning checkpoint:** Background task scheduling in Python

### Step 9: Profile Wizard (Phase 2)
- Profile form with HTMX
- Store in SQLite profiles table
- **Learning checkpoint:** Multi-step forms, structured data storage

### Step 10: Ollama Integration + CV/Cover Letter Generation
- Connect to Ollama API
- Generate tailored CVs and cover letters from profile + job description
- Per-job chat wizard — Ollama reads job description + profile, asks targeted questions, drafts cover letter
- CV generation — profile as structured CV, tailored per job
- **Learning checkpoint:** Local LLM API integration, prompt engineering

#### Step 10: Infrastructure Setup
- **Model:** Phi-3 mini (~2.3GB, fits comfortably in Mac Mini's 8GB RAM)
- **Ollama runs on:** M2 Mac Mini (native, localhost only)
- **JobLens runs on:** Ubuntu laptop
- **Connection:** SSH tunnel from Ubuntu → Mac Mini on port 11434
  - Tunnel command: `ssh -L 11434:localhost:11434 <user>@<mac-mini-ip>`
  - JobLens connects to `localhost:11434` as if Ollama were local
- **To set up Mac Mini side:** install Homebrew if needed, then `brew install ollama && ollama pull phi3`
- **TODO:** confirm Homebrew is installed on Mac Mini before starting

### Step 11: EU Tender/RFP Intelligence Module
- New DB tables: `tenders`, `cpv_codes`, `framework_holders`
- **TED API integration** — crawl Tenders Electronic Daily using target CPV codes (72221000, 72413000, 79413000, 92312211)
- **National portal scrapers** — PLACE (FR), TenderNed (NL), Bund.de (DE), Contratación Pública (ES)
- **Framework holder tracking** — monitor Award Notices, track major consortium winners for sub-contracting leads
- **Multilingual keyword heuristics** — search in EN/FR/DE/ES using domain-specific terminology
- **Hidden RFP signal detection** — flag tenders mentioning digital maturity, re-platforming, citizen portals, DORA compliance
- UI: tender list view with CPV filtering, deadline tracking, framework holder directory
- **Learning checkpoint:** Working with structured government APIs, multilingual search, domain-specific data modelling
- **Full spec:** `docs/TENDER_MODULE.md`

---

## Verification

At each step, you should be able to:
- Run the app (`uvicorn app.main:app --reload`)
- See the result in your browser at `http://localhost:8000`
- Commit your progress with a descriptive message

## Current Progress

- [x] Step 1: Project Setup
- [x] Step 2: Hello World with FastAPI + HTMX
- [x] Step 3: Database Layer
- [x] Step 4: First Scraper (RemoteOK)
- [x] Step 5: Display Jobs in the Browser
- [x] Step 6: Search & Filtering
- [x] Step 7: More Scrapers (EuroBrussels, HN Who's Hiring, EU Careers done ✓ — Impactpool + EURemoteJobs deferred, need Playwright)
- [x] Step 8: Scheduled Fetching
- [ ] Step 9: Profile Wizard
- [ ] Step 10: Ollama + CV/Cover Letter Generation (Phi-3 mini on M2 Mac Mini via SSH tunnel)
- [ ] Step 11: EU Tender/RFP Intelligence Module

---

## Deferred Tasks

| Task | Reason deferred | Step |
|------|----------------|-------|
| Impactpool scraper | JS-rendered, needs Playwright | 7 |
| EURemoteJobs scraper | JS-rendered, needs Playwright | 7 |
| Playwright scraper batch | Do all JS-rendered scrapers together | 7 |
| HN job title parsing (company/role/location) | Inconsistent format — defer to Ollama | 10 |
| Auto-refresh job list after "Fetch Now" | Nice-to-have UI improvement | 8 |
| Raise LIMIT 100 on job list query | Needed as sources grow | 8 |
| Check robots.txt for each scraped site | Ethical/legal due diligence | 7 |
| Multi-user support | Replace LIMIT 1 profile logic with user_id-based lookups + auth | 9 |
| Profile data model redesign | Split into profiles, education, work_history, skills, profile_documents tables | 9 |
| Profile UI redesign | Structured entries per role/qualification, richer form | 9 |

---

## Open Source Considerations

If this project is made public, the following should be addressed first:

- **robots.txt compliance** — check and document each source's scraping policy
- **ToS review** — some sites prohibit scraping even public pages; document which sources are safe
- **Profile data** — consider not storing profile data at all, generating CV/cover letters on the fly without persistence, or making storage opt-in
- **Scraping etiquette** — add rate limiting and a configurable fetch interval so self-hosters don't hammer sites
- **README notice** — advise users to review each source's ToS before running
- **Scale** — the current approach is fine for personal use; simultaneous scraping by many users would need a shared cache or API-first sources
