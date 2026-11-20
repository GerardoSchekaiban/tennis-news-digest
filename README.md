# Tennis News Digest

A personal daily email with the day's tennis news (ATP, WTA, Grand Slams) as short headlines.
Built as a learning project: you write most of the code, milestone by milestone.

## Architecture

```
 sources (one module each)          pipeline                                   output
 ┌──────────────┐
 │ RSS + full   │──┐
 │ text (traf.) │  │   ┌────────┐   ┌───────────┐   ┌────────┐   ┌────────┐   ┌─────────┐   ┌───────┐
 ├──────────────┤  ├──▶│ Article│──▶│ Postgres  │──▶│ Claude │──▶│ dedup  │──▶│ rank vs │──▶│Claude │──▶ email
 │ YouTube      │  │   │ (common│   │ +pgvector │   │ Haiku: │   │ (embed-│   │ profile │   │Sonnet:│    (Resend)
 │ transcripts  │──┤   │ shape) │   └───────────┘   │ JSON   │   │ dings) │   └─────────┘   │compose│
 ├──────────────┤  │   └────────┘                   │ summary│   └────────┘                 └───────┘
 │ scrapers     │──┘                                └────────┘
 │ (later)      │
 └──────────────┘                         run daily by GitHub Actions
```

- **Sources** each return `list[Article]` (see `digest/models.py`), with content as Markdown.
- **Postgres + pgvector** stores articles, Claude's structured output and embeddings.
- **Claude Haiku** summarizes and tags each article as JSON (cheap, runs per article).
- **Embeddings** spot the same story told by different outlets.
- **Ranking** scores stories against `profile.yaml` (your players and interests).
- **Claude Sonnet** writes the final email from the top stories (runs once a day).

## Layout

```
digest/
  models.py           Article dataclass (done)
  sources/youtube.py  YouTube channels + transcripts (done, worked example)
  sources/rss.py      RSS + full text (milestone 1, skeleton)
  db.py               milestone 2
  summarize.py        milestones 3-4
  dedup.py            milestone 6
  rank.py             milestone 7
  compose.py          milestone 8
  send_email.py       milestone 8
  main.py             runs the pipeline
config/sources.yaml   feeds and channels
db/init.sql           schema (milestone 2)
profile.example.yaml  copy to profile.yaml
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in keys as you need them
cp profile.example.yaml profile.yaml
docker compose up -d            # Postgres + pgvector on localhost:5432
```

Run modules from the repo root, e.g. `python -m digest.sources.youtube`.

---

## Roadmap

Each milestone ends with something you can run and see. Hints point the way; the code is yours.

### 1. Fetch RSS
**Goal:** `python -m digest.sources.rss` prints today's tennis headlines with full text.
**Learn:** RSS/Atom, feedparser, extracting main text from HTML, why Markdown is a good format for LLMs.
**Hints:**
- Read `digest/sources/youtube.py` first. `rss.py` has the same shape.
- Find 3 to 5 feeds and put them in `config/sources.yaml`. Open each URL in the browser first.
- `trafilatura.extract(html, output_format="markdown")`. Some sites block scrapers: fall back to the feed's summary.
- Feeds disagree on dates. Print `entry.keys()` for one entry of each feed.

### 2. Store in Postgres
**Goal:** running the fetch twice leaves no duplicate rows.
**Learn:** Docker Compose, psycopg 3, schema design, idempotent inserts.
**Hints:** write the table in `db/init.sql`; `UNIQUE (url)` + `ON CONFLICT DO NOTHING`. Use `psql` or a GUI (DBeaver, TablePlus) to look at the data.

### 3. First Claude call
**Goal:** print a 2-sentence summary of one stored article.
**Learn:** the Anthropic SDK, system vs. user prompts, tokens and cost, model choice.
**Hints:** start in a scratch script or notebook. Check `response.usage` to see what each call costs.

### 4. Structured output
**Goal:** every article gets a validated JSON summary (headline, players, tour, tournament, topics, importance) saved in the DB.
**Learn:** structured outputs / tool use, pydantic validation, prompt iteration, handling failures.
**Hints:** see the docstring in `summarize.py`. Keep 10 real articles as a test set and compare prompts on them.

### 5. YouTube source
**Goal:** videos from your channels flow through the same pipeline as articles.
**Learn:** reading someone else's working module, channel feeds, transcripts, messy input text.
**Hints:** this module is already written. Your job: find real channel IDs, run it, read every line, then wire it into `main.py` and the DB. Check how Haiku copes with a 20-minute transcript compared with a news article. Try changing the code: skip videos shorter than N words, or add a second language.

### 6. Dedup with embeddings
**Goal:** the same match result from 4 outlets appears once.
**Learn:** embeddings, cosine distance, pgvector indexes, choosing thresholds from data.
**Hints:** see `dedup.py`. Print distances for pairs you know are duplicates and pairs you know are not before picking a threshold.

### 7. Profile ranking
**Goal:** your favorite players and topics come first.
**Learn:** scoring functions, then LLM-as-ranker, and how to compare the two.
**Hints:** start with a rule-based score you can explain. Only then try Claude.

### 8. Compose and email
**Goal:** a digest lands in your inbox.
**Learn:** prompting for a format, HTML email basics, the Resend API.
**Hints:** save the composed HTML to `output/` and open it in a browser before sending anything.

### 9. GitHub Actions
**Goal:** the digest arrives every morning without you.
**Learn:** cron workflows, repository secrets, hosted Postgres (Neon free tier).
**Hints:** `on: schedule: - cron: "0 6 * * *"` (UTC). Put keys in repo Secrets. YouTube often blocks transcript downloads from cloud IPs: if that happens in Actions, look into the proxy options in youtube-transcript-api's README, or fetch videos from home.
