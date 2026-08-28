\# Frontier Intelligence Pipeline



An AI-powered data-ingestion pipeline that crawls web content, extracts structured organization information using an LLM, handles HTTP failures, resolves duplicate entities, stores data in SQLite, and tracks GitHub repository metrics.



\## Project Overview



This project was developed as an AI Engineer internship assessment prototype.



The pipeline demonstrates:



\- Web crawling

\- HTTP 429 rate-limit handling

\- Retry and exponential backoff

\- HTML text extraction

\- LLM-based structured extraction

\- Pydantic schema validation

\- HTTP 413 recovery through chunking

\- Entity resolution and duplicate detection

\- Duplicate URL handling

\- GitHub repository metrics collection

\- Historical metrics storage

\- SQLite persistence

\- Automated testing

\- Scalability architecture for 100,000+ records



\---



\## Architecture



```text

&#x20;                        Input URL

&#x20;                           |

&#x20;                           v

&#x20;                   +---------------+

&#x20;                   |    Crawler    |

&#x20;                   |    HTTPX      |

&#x20;                   +---------------+

&#x20;                           |

&#x20;                           v

&#x20;                   HTTP 429 Handling

&#x20;                   Retry + Backoff

&#x20;                           |

&#x20;                           v

&#x20;                      HTML Content

&#x20;                           |

&#x20;                           v

&#x20;                   +---------------+

&#x20;                   | BeautifulSoup |

&#x20;                   +---------------+

&#x20;                           |

&#x20;                           v

&#x20;                     Readable Text

&#x20;                           |

&#x20;                           v

&#x20;                +----------------------+

&#x20;                |   LLM Extraction     |

&#x20;                | OpenAI + Pydantic    |

&#x20;                +----------------------+

&#x20;                           |

&#x20;                    Request Too Large?

&#x20;                       /           \\

&#x20;                     No             Yes

&#x20;                     |               |

&#x20;                     |          +-----------+

&#x20;                     |          | Chunk Text |

&#x20;                     |          +-----------+

&#x20;                     |               |

&#x20;                     |          LLM per chunk

&#x20;                     |               |

&#x20;                     |         Merge results

&#x20;                     |               |

&#x20;                     +-------+-------+

&#x20;                             |

&#x20;                             v

&#x20;                    Entity Resolution

&#x20;                             |

&#x20;                             v

&#x20;                        SQLite DB

&#x20;                      /            \\

&#x20;                     v              v

&#x20;             Organizations      Documents



&#x20;                      GitHub Metrics

&#x20;                             |

&#x20;                             v

&#x20;                        SQLite DB

```



\---



\## Technology Stack



| Technology | Purpose |

|---|---|

| Python | Core implementation |

| HTTPX | HTTP requests and GitHub API |

| BeautifulSoup | HTML parsing and text extraction |

| OpenAI | Structured LLM extraction |

| Pydantic | Structured data validation |

| python-dotenv | Environment variable loading |

| SQLite | Prototype database |

| pytest | Automated testing |

| tenacity | Retry support / retry utilities |



\---



\## Project Structure



```text

frontier-intelligence-pipeline/

│

├── app/

│   ├── crawler/

│   │   └── fetcher.py

│   │

│   ├── database/

│   │   └── db.py

│   │

│   ├── entity\_resolution/

│   │   ├── resolver.py

│   │   └── database\_resolver.py

│   │

│   ├── extraction/

│   │   ├── chunker.py

│   │   ├── extractor.py

│   │   └── pipeline.py

│   │

│   ├── metrics/

│   │   └── github\_metrics.py

│   │

│   └── main.py

│

├── tests/

│   ├── test\_413\_recovery.py

│   ├── test\_429\_retry.py

│   ├── test\_duplicate\_urls.py

│   └── test\_malformed\_ai\_output.py

│

├── test\_chunker.py

├── test\_database\_resolver.py

├── test\_entity\_resolution.py

├── test\_github\_metrics.py

├── test\_llm.py

│

├── SCALING.md

├── README.md

├── pytest.ini

├── requirements.txt

└── .gitignore

```



\---



\# 1. Web Crawler



The crawler is implemented in:



```text

app/crawler/fetcher.py

```



It uses HTTPX with:



\- Redirect support

\- Request timeout

\- Custom User-Agent

\- HTTP error handling

\- Retry logic

\- Exponential backoff

\- Jitter

\- HTTP 429 handling



\### HTTP 429 Handling



When a server returns HTTP 429, the crawler checks the `Retry-After` header.



If the header is unavailable, exponential backoff is used.



```text

Request

&#x20;  |

&#x20;  v

429?

&#x20;/  \\

No   Yes

|      |

Return  Retry

&#x20;      |

&#x20;      v

&#x20;   Backoff

&#x20;      |

&#x20;      v

&#x20;   Retry request

```



The retry mechanism is bounded by a maximum number of attempts.



\---



\# 2. HTML Processing



After downloading a page, BeautifulSoup is used to extract readable text from HTML.



The pipeline extracts:



\- Page title

\- Visible/readable text

\- Original URL

\- Processing timestamps



This produces clean text that can be passed to the extraction layer.



\---



\# 3. LLM Structured Extraction



LLM extraction is implemented in:



```text

app/extraction/extractor.py

```



The pipeline uses OpenAI structured output with a Pydantic model.



The extracted organization schema is:



```text

Organization

├── name

├── description

├── website

├── founded\_year

└── category

```



Example:



```json

{

&#x20; "name": "Example AI",

&#x20; "description": "An artificial intelligence company.",

&#x20; "website": "https://example.com",

&#x20; "founded\_year": 2020,

&#x20; "category": "AI"

}

```



The LLM is instructed to use only information supported by the input text.



Unknown fields are represented as `null`.



Pydantic validates the resulting structured data.



\---



\# 4. HTTP 413 Recovery



Large requests can exceed an API's request-size limit.



The extraction pipeline handles HTTP 413 / oversized-request errors in:



```text

app/extraction/pipeline.py

```



Normal flow:



```text

Large document

&#x20;     |

&#x20;     v

Attempt normal extraction

&#x20;     |

&#x20;     v

413 / Too Large

&#x20;     |

&#x20;     v

Split into chunks

&#x20;     |

&#x20;     v

Extract each chunk

&#x20;     |

&#x20;     v

Merge results

```



The chunker uses overlapping chunks so that important information near chunk boundaries is less likely to be lost.



The current prototype uses a configurable maximum chunk size and overlap.



\---



\# 5. Chunking



Chunking is implemented in:



```text

app/extraction/chunker.py

```



Large documents are divided into smaller overlapping sections.



Example:



```text

26,000 characters

&#x20;       |

&#x20;       v

+----------------+

| Chunk 1 12,000 |

+----------------+

&#x20;       |

&#x20;       v

+----------------+

| Chunk 2 12,000 |

+----------------+

&#x20;       |

&#x20;       v

+----------------+

| Chunk 3  4,000 |

+----------------+

```



The extracted organization information from each chunk is merged into a single structured result.



\---



\# 6. Entity Resolution



Entity resolution is implemented in:



```text

app/entity\_resolution/resolver.py

```



The resolver normalizes organization names before comparing them.



Examples of potentially equivalent names:



```text

OpenAI Inc.

OpenAI, Inc.

OpenAI Corporation

```



Normalization and matching help prevent duplicate organizations from being stored.



Database-level resolution is implemented in:



```text

app/entity\_resolution/database\_resolver.py

```



The database resolver:



1\. Normalizes the organization name.

2\. Searches existing organizations.

3\. Determines whether a matching organization exists.

4\. Updates an existing record when appropriate.

5\. Inserts a new organization when no match exists.



\---



\# 7. Duplicate URL Handling



Documents are stored using their URL as the unique identifier.



When a URL is processed again, the existing document can be updated rather than creating another duplicate document record.



This makes repeated crawling safer and prevents unnecessary duplication.



\---



\# 8. Database



The prototype uses SQLite:



```text

data/intelligence.db

```



The database contains three primary tables.



\## Organizations



```text

id

name

description

website

founded\_year

category

created\_at

updated\_at

```



\## Documents



```text

id

url

title

raw\_text

source\_published\_at

discovered\_at

scraped\_at

processed\_at

```



\## Repository Metrics



```text

id

repository

stars

forks

observed\_at

```



SQLite was selected because it is lightweight and sufficient for this assessment prototype.



For a production deployment at larger scale, PostgreSQL would be preferred.



\---



\# 9. GitHub Repository Metrics



GitHub metrics are implemented in:



```text

app/metrics/github\_metrics.py

```



The GitHub API is used to retrieve:



\- Repository name

\- Star count

\- Fork count



The metrics are stored as historical snapshots.



Example:



```text

repository          stars    forks

\-----------------------------------

openai/example      100      20

openai/example      125      30

openai/example      150      35

```



Historical observations are preserved instead of overwriting previous measurements.



This makes it possible to analyze repository growth over time.



\---



\# 10. Automated Testing



The project uses pytest.



The test suite covers:



\- Chunking

\- Entity resolution

\- Database entity resolution

\- GitHub metrics

\- HTTP 413 recovery

\- HTTP 429 retry behavior

\- Duplicate URLs

\- Malformed AI output

\- Optional live LLM integration



The latest test result:



```text

16 tests collected



15 passed

1 skipped

0 failed

```



The skipped test is the live OpenAI test.



It is intentionally skipped unless:



```powershell

$env:RUN\_LLM\_TEST="1"

```



is configured.



\---



\# 11. OpenAI API Quota Limitation



The real OpenAI extraction implementation is present and uses:



```text

gpt-4o-mini

```



The live API test is currently skipped because the configured OpenAI project returned:



```text

429 insufficient\_quota

```



This indicates an API quota/credits limitation rather than a crawler rate-limit failure.



The implementation itself is present and the remaining extraction functionality is tested through mocked/unit tests.



The pipeline distinguishes between:



```text

HTTP 429

```



used for crawler rate limiting, and:



```text

insufficient\_quota

```



returned by the OpenAI API when usable API quota is unavailable.



\---



\# 12. Scalability



The current implementation is intentionally a prototype.



For production workloads containing 100,000+ records, the architecture can be scaled horizontally.



The proposed architecture is:



```text

&#x20;                   Input Queue

&#x20;                        |

&#x20;         +--------------+--------------+

&#x20;         |              |              |

&#x20;         v              v              v

&#x20;      Worker 1       Worker 2       Worker 3

&#x20;         |              |              |

&#x20;         +--------------+--------------+

&#x20;                        |

&#x20;                        v

&#x20;                Crawler / Extraction

&#x20;                        |

&#x20;                        v

&#x20;                Entity Resolution

&#x20;                        |

&#x20;                        v

&#x20;                   PostgreSQL

```



A production system could use:



\- Message queue

\- Multiple crawler workers

\- Multiple LLM workers

\- PostgreSQL

\- Redis/cache

\- Batch processing

\- Rate-limit coordination

\- Observability and monitoring



The detailed scalability architecture is documented in:



```text

SCALING.md

```



\---



\# 13. Setup



\## Clone the repository



```powershell

git clone https://github.com/lakshmipravallikapothula-glitch/frontier-intelligence-pipeline.git

cd frontier-intelligence-pipeline

```



\## Create a virtual environment



```powershell

python -m venv .venv

```



\## Activate the environment



Windows PowerShell:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



\## Install dependencies



```powershell

pip install -r requirements.txt

```



\## Configure the OpenAI API key



Create a local `.env` file:



```env

OPENAI\_API\_KEY=your\_api\_key\_here

```



Do not commit `.env` to GitHub.



The repository `.gitignore` excludes:



```text

.env

.venv/

\_\_pycache\_\_/

\*.pyc

data/

```



\---



\# 14. Running the Pipeline



The application entry point is:



```text

app/main.py

```



Run:



```powershell

python -m app.main

```



The pipeline performs:



```text

URL

&#x20;↓

Crawler

&#x20;↓

HTML parsing

&#x20;↓

Text extraction

&#x20;↓

LLM structured extraction

&#x20;↓

413 recovery if required

&#x20;↓

Entity resolution

&#x20;↓

SQLite persistence

```



\---



\# 15. Running Tests



Run the complete test suite:



```powershell

pytest

```



Expected current result:



```text

15 passed, 1 skipped

```



Run an individual test file:



```powershell

pytest tests/test\_429\_retry.py

```



For the live LLM test:



```powershell

$env:RUN\_LLM\_TEST="1"

pytest test\_llm.py

```



A valid OpenAI API project with available quota is required for the live LLM test.



\---



\# 16. Design Decisions



\### Why SQLite?



SQLite keeps the prototype simple, portable, and easy to run locally.



\### Why Pydantic?



Pydantic provides schema validation for structured LLM output.



\### Why chunking?



Chunking provides a recovery mechanism when a document exceeds the request-size limit.



\### Why overlapping chunks?



Overlap reduces the chance of losing context at chunk boundaries.



\### Why historical GitHub metrics?



Historical snapshots allow repository growth to be analyzed instead of only storing the latest value.



\### Why entity resolution?



Entity resolution prevents multiple records representing the same organization from being stored independently.



\---



\# 17. Limitations



This is an assessment prototype rather than a production system.



Current limitations include:



\- SQLite is not intended for high-concurrency production workloads.

\- The crawler processes URLs synchronously at the application level.

\- Production-scale queue infrastructure is not implemented.

\- GitHub API authentication/rate-limit management can be expanded.

\- The live OpenAI test requires available API quota.

\- Observability and distributed tracing are not implemented.

\- Large-scale worker orchestration is documented rather than deployed.



\---



\# 18. Future Improvements



Possible production improvements include:



1\. PostgreSQL migration

2\. Message queue integration

3\. Distributed crawler workers

4\. LLM worker pool

5\. Redis caching

6\. Better GitHub API rate-limit coordination

7\. Structured logging

8\. Metrics and monitoring

9\. Distributed tracing

10\. Dead-letter queues for failed jobs

11\. Batch processing

12\. Scheduled GitHub metrics collection



\---



\# 19. Assignment Requirements Covered



| Requirement | Status |

|---|---|

| Website crawling | Complete |

| HTTP 429 handling | Complete |

| Retry/backoff | Complete |

| LLM structured extraction | Complete |

| Pydantic validation | Complete |

| HTTP 413 recovery | Complete |

| Document chunking | Complete |

| Entity resolution | Complete |

| Duplicate URL handling | Complete |

| GitHub metrics | Complete |

| Historical metrics | Complete |

| SQLite persistence | Complete |

| Automated tests | Complete |

| 100,000+ record architecture | Documented |

| README documentation | Complete |



\---



\## Test Summary



```text

16 tests collected

15 passed

1 skipped

0 failed

```



The single skipped test is the optional live LLM test because the current OpenAI API project has insufficient quota.



\---



\## Repository



GitHub:



```text

https://github.com/lakshmipravallikapothula-glitch/frontier-intelligence-pipeline

```



\---



\## Author



AI Engineer Internship Assessment



Frontier Intelligence Pipeline

