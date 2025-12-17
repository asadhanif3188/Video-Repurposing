
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

REPURPOSE_METADATA_PROMPT = """
You are a creative content strategist and educator.
Analyze the following YouTube video metadata to infer the main topic and educational value of the video.
Generate 20-30 unique, non-repetitive content atoms (insights, opinions, lessons, quotes) based **solely** on the topic inferred from this metadata.

Guidelines:
- **Avoid Hallucination**: Do not make up specific facts, numbers, or events not present in the text.
- **Generalize**: If specific details are missing, create high-quality general insights or educational lessons about the topic.
- **Tone**: Professional, educational, and engaging.
- **Format**: Return the output as a strict JSON object with a key 'atoms'.

Metadata:
Title: {title}
Channel: {channel}
Description:
{description}

Output Schema:
{{
  "atoms": [
    {{ "type": "insight", "text": "..." }},
    {{ "type": "opinion", "text": "..." }},
    {{ "type": "lesson", "text": "..." }},
    {{ "type": "quote", "text": "..." }}
  ]
}}
"""
