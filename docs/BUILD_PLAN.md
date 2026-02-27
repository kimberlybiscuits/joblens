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

| Source | Method | Status | Notes |
|--------|--------|--------|-------|
| RemoteOK | JSON API | ✅ Live | Free, no auth needed |
| HN Who's Hiring | HN API | ✅ Live | Mostly tech noise, limited value for content/comms roles |
| EuroBrussels | HTML scrape | ✅ Live | Key for EU roles |
| eu-careers.europa.eu | RSS/HTML | ✅ Live | Official EU job portal |
| EU Remote Jobs | HTML scrape | ✅ Live | 40 jobs per fetch |
| ImpactPool | HTML scrape | ✅ Live | 400 jobs per fetch (10 pages × 40) |
| Working in Content | HTML scrape | ⏸️ Blocked | Cloudflare + reCAPTCHA — best fit for field, worth revisiting with Playwright |
| Working Nomads | HTML scrape | ⏸️ Blocked | Cloudflare + reCAPTCHA — revisit with Playwright |
| Remote Rocketship | HTML scrape | ⏸️ Blocked | 403 on all requests — investigate alternative approach |
| LinkedIn | — | ❌ Avoid | Aggressive bot detection, ToS/legal risk |

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

### Step 10: Ollama Integration (Shelved)
- Phi-3 mini installed on Mac Mini via Homebrew, SSH tunnel to Ubuntu on port 11434
- `app/ollama_client.py` and `app/routes/cover_letter.py` built but shelved
- Cover letter generation produced hallucinated results — small model not suited to open-ended writing
- **Decision:** AI angle abandoned. Focus shifted to better job surfacing and matching.
- **Learning checkpoint:** Local LLM API integration, prompt engineering, knowing when not to use AI

### Step 11: Job Surfacing & Filtering ✅ Complete
- **Title chip filtering** — predefined job title chips stored in profile.preferred_titles, active by default, toggleable, with Clear button
- **Location + Remote filters** — text input for location, toggle chip for remote only
- **Recency filter** — only shows jobs from last 90 days (date_posted if available, falls back to created_at)
- **New badge** — green pill on jobs posted in last 48 hours
- **Saved jobs / My Jobs page** — Save button on cards, /saved page with status cycling (Saved → Applied → Heard back) and Remove button
- **Nav updated** — Jobs, My Jobs, Profile links

### Step 12: New Sources (Next)
- Add ProBlogger (RSS), EU Remote Jobs (HTML), ImpactPool (HTML)
- Investigate Playwright for Cloudflare-protected sites (Working in Content, Working Nomads)
- Consider disabling or downweighting HN (mostly tech noise)

### Step 12: Non-Job-Board Sources
- Slack community job channels
- Newsletter/RSS feeds (Working Nomads, Otta, etc.)
- Bluesky/Mastodon job posts

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
- [x] Step 7: More Scrapers (EuroBrussels, HN Who's Hiring, EU Careers done ✓ — Impactpool + EURemoteJobs deferred)
- [x] Step 8: Scheduled Fetching
- [x] Step 9: Profile Wizard
- [x] Step 10: Ollama — Shelved (Phi-3 too weak, hallucinated results)
- [x] Step 11: Job Surfacing & Filtering (title chips, recency, saved jobs, My Jobs page)
- [x] Step 12: New Sources (EU Remote Jobs ✅, ImpactPool ✅ — blocked sources deferred to Playwright batch)
- [ ] Step 13: EU Tender/RFP Intelligence Module

---

## Deferred Tasks

| Task | Reason deferred | Step |
|------|----------------|-------|
| EuroBrussels full listing | JS-rendered, ~100+ jobs hidden behind dynamic filters | 7 |
| Playwright scraper batch | Do all JS-rendered scrapers together — includes EuroBrussels full listing (100+ jobs, currently capped at ~35) | 7 |
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
