from django.conf import settings
from openai import OpenAI


def generate_from_source(source_text, output_type):

    if not source_text or not source_text.strip():
        return (
            "There is not enough accessible source content "
            "to generate this output."
        )

    prompts = {

        "summary": """
Create a concise but useful summary.

Include:

1. Main idea
2. Important points
3. Key facts
4. Important conclusions
5. One-minute version

Use ONLY the supplied source.
Do not add outside information.
If something is not stated in the source, do not invent it.
""",

        "notes": """
Turn the source into structured study notes.

Use:

- Clear headings
- Subheadings
- Bullet points
- Definitions
- Key concepts
- Important examples
- Key takeaways
- Important terminology
- Remember this

Use ONLY the supplied source.
Do not invent facts.
""",

        "quiz": """
Create a 10-question quiz based ONLY on the source.

For each question provide:

Question:
A.
B.
C.
D.

Correct answer:
Explanation:
Hint:

Do not introduce information that is not in the source.
""",

        "audio": """
Convert the source into a natural spoken narration.

Do not read navigation, menus,
advertisements or webpage clutter.

Make it sound natural when spoken aloud.

Use ONLY the supplied source.
""",

        "video": """
Create a complete educational video storyboard.

For each scene provide:

Scene number:
Visual:
Narration:
On-screen text:

Include an opening, logical teaching sequence,
key concepts and conclusion.

Use ONLY the supplied source.
""",
    }

    instruction = prompts.get(output_type)

    if not instruction:
        raise ValueError(
            "Unsupported output type."
        )

    api_key = getattr(
        settings,
        "OPENAI_API_KEY",
        ""
    )

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not configured in Django settings."
        )

    client = OpenAI(
        api_key=api_key
    )

    prompt = f"""
{instruction}

SOURCE CONTENT
--------------
{source_text}
--------------
END SOURCE CONTENT

IMPORTANT:
Your answer must be based strictly on SOURCE CONTENT.
Do not use outside knowledge.
Do not invent facts.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text