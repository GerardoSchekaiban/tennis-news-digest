"""Summarize and tag each article with Claude. MILESTONES 3 and 4.

Milestone 3: send one article to SUMMARY_MODEL and print a 2-sentence summary.
Milestone 4: make the answer structured. Define a pydantic model such as

    class ArticleSummary(BaseModel):
        headline: str        # short, punchy, < 90 chars
        summary: str         # 1-2 sentences
        tour: Literal["ATP", "WTA", "both", "other"]
        players: list[str]
        tournament: str | None
        topics: list[str]    # e.g. ["result", "injury", "ranking"]
        importance: int      # 1-5

and ask Claude to return exactly that shape. Look up "structured outputs" /
"tool use" in the Anthropic docs. Validate the reply with pydantic.

Hint: video transcripts are long and unpunctuated. Truncating content_md to a
few thousand words keeps cost down and rarely hurts the summary.
"""
