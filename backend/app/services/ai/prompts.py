
EXTRACT_ATOMS_PROMPT = """
Analyze the following transcript and extract 20-30 separate content atoms.
Each atom should be a distinct insight, opinion, lesson, or quote.

Return the output as a JSON object with a key 'atoms' containing a list of objects.
Each object must have:
- 'type': one of ['insight', 'opinion', 'lesson', 'quote']
- 'text': the extracted content

Transcript:
{transcript_text}
"""

REWRITE_CONTENT_PROMPT = """
Rewrite the following content for {platform}.
Style guide: {style_guide}.

Content:
{text}

Return only the rewritten text.
"""
