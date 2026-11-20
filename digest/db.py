"""Database access. MILESTONE 2.

TODO:
- connect(): open a psycopg connection from DATABASE_URL (python-dotenv loads .env)
- save_articles(conn, articles): insert, ignoring ones already stored
  (hint: INSERT ... ON CONFLICT DO NOTHING)
- unsummarized(conn): articles that don't have Claude's output yet (milestone 3/4)
- later: save_summary, save_embedding, recent_embeddings
"""
