"""Summarize and tag each article with Claude. MILESTONES 3 and 4.

Milestone 3: send one article to SUMMARY_MODEL and print a 2-sentence summary. """

import os
from dotenv import load_dotenv

load_dotenv()  # read .env once, when this file is first imported

#Module-level constants.
MODEL = os.environ["SUMMARY_MODEL"]
SYSTEM = """You are an expert summarizer. Summarize the article the user sends in 2 sentences."""

def summarize_article(client, title: str, content_md: str) -> str:
    """Summarize the article with Claude and return the summary text"""
    
    user_message = f"Title: {title}\n\nContent:\n{content_md}"

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM,
        messages=[{"role": "user",  "content": user_message}]
    )

    for block in response.content:
        if block.type == "text":
            return block.text
        
    #Failing loudly beats failing silently.
    raise ValueError("No text block found in Claude's response")

"""
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
