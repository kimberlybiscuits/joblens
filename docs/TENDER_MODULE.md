# EU Tender/RFP Intelligence Module — Reference Spec

> Source: Gemini research notes + project planning. This is the detailed reference
> for BUILD_PLAN.md Step 11.

---

## Objective

Systematically crawl and categorize high-value Content Design and UX Strategy
opportunities within the EU's public and private procurement ecosystems.

---

## 1. Primary EU Data Sources

### TED (Tenders Electronic Daily)
- Mandatory portal for all public tenders above EU thresholds
- Crawl the Official Journal of the EU (OJ S)
- **Target CPV Codes:**
  - `72221000-0` — Strategic design and planning
  - `72413000-8` — WWW site design services
  - `79413000-2` — Marketing management consultancy (covers Content Strategy)
  - `92312211-3` — Writing agency services (UX Writing/Content Design)

### SEDIA (EU Funding & Tenders Portal)
- Direct procurement for European Commission agencies (DG COMM, DG DIGIT, etc.)

### National Repositories (below-threshold tenders)

| Country | Portal | URL |
|---------|--------|-----|
| France | PLACE (Plateforme des Achats de l'Etat) | place.marches-publics.gouv.fr |
| Germany | Bund.de / Vergabe24 | service.bund.de |
| Netherlands | TenderNed | tenderned.nl |
| Spain | Plataforma de Contratación del Sector Público | contrataciondelestado.es |

---

## 2. Framework Holder Tracking ("Gatekeeper" Strategy)

In the EU, content strategy is rarely a standalone RFP — it's usually a Work
Package within a massive Framework Agreement.

**Intelligence task:** Monitor Award Notices. When a large consortium wins a
multi-year Framework, they become the primary source for sub-contracting work.

### Target Entities (Major 2024-2026 Framework Holders)

| Entity | Notes |
|--------|-------|
| ICF Next | Lead on many DG COMM communication frameworks |
| GOPA Com | Major player in EU institutional communications |
| Serviceplan / House-of-Communication.EU | Multi-agency digital consortium |
| Ogilvy Social Lab | Frequent winner of EU digital social/content lots |
| Deloitte Digital / PwC / Wavestone | Holders of major "ABC IV" and Digital Transformation frameworks |
| AlmavivA / Tremend | Holders of the €290M MAIA Lot 6 for EU digital transformation |

---

## 3. Keyword & Semantic Heuristics

The crawler must look beyond "Content Strategy" — EU tenders use administrative
and technical jargon.

### Primary Keywords (EN)
- Information Architecture
- User Experience Writing
- Digital Governance
- CMS Migration Strategy

### Multilingual Triggers

| Language | Keywords |
|----------|----------|
| FR | Stratégie éditoriale, Audit de contenu, Accessibilité numérique |
| DE | Content-Strategie, Redaktionsplanung, Informationsarchitektur |
| ES | Estrategia de contenidos, Diseño de experiencia de usuario |

---

## 4. Hidden RFP Signal Detection

Flag any RFP mentioning the following — these require Content Design even if not
explicitly stated:

| Signal | Why it matters |
|--------|---------------|
| "Digital Maturity Assessment" | Almost always leads to a content audit |
| "Website Re-platforming" | Requires content migration strategy and IA |
| "Citizen Engagement Portal" | High demand for UX Writing and plain-language strategy |
| "DORA Compliance" (Digital Operational Resilience Act) | Triggers needs for technical content governance and documentation strategy |

---

## Implementation Notes

- TED has a searchable API at `search.ted.europa.eu` — prefer API over scraping
- National portals vary widely in structure; some have APIs, most require HTML scraping
- Framework holder data is semi-static — can be seeded manually and refreshed quarterly
- Multilingual keyword matching should be configurable (user adds their own terms)
- Tender deadlines are critical — need prominent display and optional notifications
