# Website QA Engine

A deterministic website question-answering system that crawls a website, extracts its content, retrieves relevant information, ranks evidence, and generates answers **without using an LLM or AI API**.

The system is designed to answer questions using only the indexed content of the provided website and provides source citations for retrieved evidence.

## Overview

Website QA Engine allows a user to:

1. Enter a website URL.
2. Crawl and analyze the website.
3. Extract readable textual content from discovered pages.
4. Split content into searchable chunks.
5. Retrieve relevant content for a user question.
6. Rank the retrieved sentences by relevance.
7. Extract supporting evidence.
8. Generate a deterministic answer from the available website content.
9. Display the source pages used for the answer.

### Core principle

> **If the information is not available in the indexed website content, the system should not invent an answer.**

The project intentionally avoids external LLM APIs and uses traditional information-retrieval and NLP techniques.

---

## Architecture

```text
                        ┌─────────────────────┐
                        │      User           │
                        │                     │
                        │ Website URL +       │
                        │ Question            │
                        └──────────┬──────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │      Next.js Frontend    │
                    │                          │
                    │ URL Analysis UI          │
                    │ Question Interface       │
                    │ Results + Sources        │
                    └────────────┬─────────────┘
                                 │
                                 │ HTTP / JSON
                                 ▼
                    ┌──────────────────────────┐
                    │      FastAPI Backend     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      URL Validation      │
                    │                          │
                    │ HTTP/HTTPS validation    │
                    │ SSRF protection          │
                    │ DNS resolution           │
                    │ Internal IP rejection    │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       Web Crawler        │
                    │                          │
                    │ BFS crawling              │
                    │ robots.txt                │
                    │ Page discovery            │
                    │ Crawl limits              │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │     HTML Extraction      │
                    │                          │
                    │ BeautifulSoup             │
                    │ lxml parser               │
                    │ Text cleaning              │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │        Chunking           │
                    │                          │
                    │ Website text → chunks     │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Hybrid Retrieval      │
                    │                          │
                    │ TF-IDF                    │
                    │ lexical matching          │
                    │ relevance scoring         │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Sentence Ranking      │
                    │                          │
                    │ Candidate evidence        │
                    │ relevance ranking         │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │    Evidence Extraction   │
                    │                          │
                    │ Supporting sentences     │
                    │ Source page association   │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ Deterministic Answering  │
                    │                          │
                    │ Evidence-based response  │
                    │ No LLM / No AI API       │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       Source Citations   │
                    └──────────────────────────┘
```

---

# Features

## Website Analysis

* Accepts HTTP and HTTPS website URLs.
* Validates URLs before crawling.
* Resolves hostnames and checks resolved IP addresses.
* Blocks localhost and internal/private destinations.
* Supports multi-page crawling.
* Tracks successfully crawled and failed pages.
* Respects `robots.txt`.
* Extracts readable page content.
* Reports indexed character count.

## Retrieval

The system uses deterministic information retrieval instead of an LLM.

Current retrieval pipeline:

```text
Question
   ↓
Text preprocessing
   ↓
TF-IDF representation
   ↓
Candidate retrieval
   ↓
Hybrid relevance scoring
   ↓
Sentence ranking
   ↓
Evidence extraction
```

## Evidence-Based Answers

Answers are generated from retrieved website content.

For example:

```text
Question:
What services does this website provide?

Retrieved evidence:
"Software development, mentorship and technology innovation."

Answer:
The website provides software development, mentorship and
technology innovation.

Source:
https://example.com/services
```

## Source Citations

Every answer can expose the page from which the supporting evidence was retrieved.

This makes the result auditable rather than presenting an unsupported generated response.

## Session-Based QA

After a website is analyzed, the crawler result is associated with a session.

The question-answering endpoint uses the indexed session instead of crawling the website again for every question.

```text
Analyze Website
       ↓
Create Session
       ↓
Store Indexed Content
       ↓
Ask Questions
       ↓
Retrieve From Session
```

---

# No LLM / No AI API

This project intentionally does **not** use:

* OpenAI API
* Gemini API
* Claude API
* Hugging Face inference APIs
* Any external generative AI API

The intelligence comes from deterministic algorithms and information-retrieval techniques.

### Main techniques

* TF-IDF
* lexical relevance
* hybrid retrieval
* sentence ranking
* evidence extraction
* deterministic answer generation
* rule-based URL security
* BFS crawling

This makes the system:

* reproducible
* inspectable
* deterministic
* inexpensive to run
* independent of external AI APIs

---

# Tech Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

## Backend

* Python
* FastAPI
* Uvicorn
* HTTPX
* BeautifulSoup
* lxml

## Retrieval / NLP

* scikit-learn
* NumPy
* SciPy
* TF-IDF

## Deployment

* Frontend: Vercel
* Backend: Render

---

# Project Structure

```text
website-qa-engine/
│
├── backend/
│   │
│   ├── app/
│   │   ├── api/
│   │   │   ├── analyze.py
│   │   │   └── ask.py
│   │   │
│   │   ├── crawler/
│   │   │   ├── crawler.py
│   │   │   ├── robots.py
│   │   │   └── url_utils.py
│   │   │
│   │   ├── extraction/
│   │   │   └── parser.py
│   │   │
│   │   ├── retrieval/
│   │   │   └── ...
│   │   │
│   │   ├── ranking/
│   │   │   └── ...
│   │   │
│   │   ├── evidence/
│   │   │   └── ...
│   │   │
│   │   ├── answer/
│   │   │   └── ...
│   │   │
│   │   ├── session/
│   │   │   └── ...
│   │   │
│   │   └── main.py
│   │
│   ├── requirements.txt
│   ├── runtime.txt
│   └── ...
│
├── frontend/
│   │
│   ├── app/
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── ...
│
└── README.md
```

---

# Backend API

## Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "website-qa-engine"
}
```

## Analyze Website

```http
POST /api/analyze
```

Request:

```json
{
  "url": "https://example.com"
}
```

Example response:

```json
{
  "success": true,
  "session_id": "session-id",
  "url": "https://example.com/",
  "pages_crawled": 1,
  "pages_failed": 0,
  "total_characters": 127,
  "pages": [
    {
      "url": "https://example.com/",
      "title": "Example Domain",
      "text": "Example Domain...",
      "characters": 127,
      "depth": 0
    }
  ]
}
```

## Ask a Question

```http
POST /api/ask
```

The question is associated with an existing analysis session.

The backend retrieves relevant content from the indexed website and returns the generated deterministic answer together with supporting sources.

---

# Local Development

## Prerequisites

* Python 3.12+
* Node.js
* npm
* Git

---

## Backend Setup

Move into the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

# Frontend Setup

Move into the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create an environment file:

```text
.env.local
```

Configure the backend API URL:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# Production Architecture

The deployed application uses:

```text
                     User
                      │
                      ▼
              ┌───────────────┐
              │    Vercel     │
              │   Next.js UI  │
              └───────┬───────┘
                      │
                      │ HTTPS
                      ▼
              ┌───────────────┐
              │    Render     │
              │ FastAPI API   │
              └───────┬───────┘
                      │
                      ▼
               Target Website
```

Frontend:

```text
https://website-qa-engine.vercel.app/
```

Backend:

```text
https://website-qa-backend-dn72.onrender.com
```

---

# Security

The crawler performs URL validation before making outbound requests.

Security checks include:

* HTTP/HTTPS-only URLs
* credential rejection
* localhost blocking
* internal hostname blocking
* private IP blocking
* loopback IP blocking
* link-local IP blocking
* reserved IP blocking
* multicast IP blocking
* unspecified IP blocking
* DNS resolution validation

This is important because a public URL crawler can otherwise become an SSRF attack surface.

---

# Crawling

The crawler uses breadth-first traversal to discover pages within the target website.

Conceptually:

```text
Start URL
   │
   ├── Page A
   │    ├── Page B
   │    └── Page C
   │
   ├── Page D
   │    └── Page E
   │
   └── Page F
```

Each discovered URL is normalized before being added to the crawl queue.

Normalization handles:

* URL fragments
* tracking parameters
* trailing slash differences
* case normalization

Tracking parameters such as `utm_source`, `utm_campaign`, `fbclid`, and `gclid` are removed to reduce duplicate pages.

---

# robots.txt

Before crawling a website, the crawler checks its `robots.txt` rules.

The system uses Python's `RobotFileParser` and caches the parsed rules per origin.

If the crawler cannot determine the crawling policy because of an HTTP failure or network error, it fails closed and avoids crawling that origin.

---

# Retrieval Pipeline

The retrieval system is designed around a simple principle:

> Retrieve first. Verify evidence. Answer second.

```text
User Question
      │
      ▼
Question Representation
      │
      ▼
Candidate Retrieval
      │
      ▼
TF-IDF / Hybrid Scoring
      │
      ▼
Top Candidates
      │
      ▼
Sentence Ranking
      │
      ▼
Evidence Extraction
      │
      ▼
Deterministic Answer
      │
      ▼
Source Citation
```

---

# Answerability

A key requirement for a website QA system is knowing when the indexed content does not contain the requested information.

For example, if the website contains:

```text
We provide software development and mentorship.
```

and the user asks:

```text
What is the company's annual revenue?
```

The system should not treat the nearest piece of text as an answer.

The desired behavior is:

```text
I couldn't find information about the company's
revenue in the provided website.
```

This prevents irrelevant retrieved content from being presented as an answer.

---

# Testing

The backend contains unit tests covering the major pipeline components.

Run:

```bash
pytest
```

The project has previously been validated with:

```text
15/15 tests passed
```

Production smoke tests can be performed with:

```bash
curl.exe -i https://website-qa-backend-dn72.onrender.com/health
```

And:

```bash
python -c "import httpx; r=httpx.post('https://website-qa-backend-dn72.onrender.com/api/analyze', json={'url':'https://example.com'}, timeout=120); print(r.status_code); print(r.text)"
```

---

# Example

A real-world website can be analyzed and indexed.

Example result:

```text
Website indexed

Pages: 6
Characters: 7,082
Failed: 5
```

A question about content found on a portfolio page can then retrieve the relevant evidence:

```text
Question:
What projects are shown on the website?

Retrieved evidence:
EuroZiel Creative business website developed for
Education consultancy.

Source:
https://techgajana.org/portfolio
```

The answer is therefore traceable back to the source page.

---

# Current Limitations

The current system is intentionally lightweight and deterministic.

Known limitations include:

* JavaScript-heavy websites may expose limited content to the crawler.
* Some websites may block automated requests.
* Some pages may fail due to network restrictions or server configuration.
* TF-IDF-based retrieval is less semantically powerful than modern embedding models.
* Deterministic answer generation has less linguistic flexibility than an LLM.
* In-memory session storage is not suitable for large-scale distributed production deployments.
* The current crawler requires further optimization for large websites.

---

# Future Improvements

Potential future improvements include:

### Retrieval

* BM25 retrieval
* dense embeddings
* hybrid sparse + dense retrieval
* query expansion
* better relevance thresholds
* explicit answerability scoring

### Crawling

* concurrent crawling
* better duplicate detection
* sitemap support
* JavaScript rendering
* configurable crawl limits
* persistent crawl storage

### Storage

* Redis session storage
* PostgreSQL metadata storage
* vector database integration
* persistent document indexing

### Answering

* stronger deterministic answer synthesis
* confidence scoring
* contradiction detection
* evidence coverage scoring
* explicit "information not found" classification

### Production

* authentication
* rate limiting
* request quotas
* structured logging
* observability
* background crawling jobs
* queue-based architecture

---

# Design Philosophy

The project focuses on making the complete QA pipeline visible and understandable.

Instead of:

```text
Question → LLM → Answer
```

the system uses:

```text
Website
   ↓
Crawl
   ↓
Extract
   ↓
Chunk
   ↓
Retrieve
   ↓
Rank
   ↓
Verify Evidence
   ↓
Answer
   ↓
Cite Source
```

This makes it possible to inspect where an answer came from and why a particular piece of information was selected.

---

# Author

**Sakthi**

Email: [sakthig1729@gmail.com](mailto:sakthig1729@gmail.com)

Portfolio: https://uimagician.netlify.app/

---

# License

This project is currently intended as a personal engineering project and demonstration of deterministic information retrieval, web crawling, and question-answering system design.
