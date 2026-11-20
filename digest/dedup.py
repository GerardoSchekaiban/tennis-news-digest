"""Drop near-duplicate stories using embeddings. MILESTONE 6.

Five sites will report the same final. Idea:
- embed headline + summary for each new article
- compare with articles from the last ~2 days using pgvector's cosine distance (<=>)
- if the closest one is under a threshold, mark it as a duplicate
TODO: pick a threshold by printing distances for a few known duplicates.
"""
