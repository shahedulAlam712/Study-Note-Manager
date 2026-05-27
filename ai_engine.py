"""
ai_engine.py — DeepSeek AI engine for Study Notes Manager
==========================================================
Uses DeepSeek API (OpenAI-compatible) for all AI features.
Set environment variable: DEEPSEEK_API_KEY
"""

import os
import json
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com"
)

MODEL = "deepseek-chat"


def _ask(prompt: str, max_tokens: int = 500) -> str:
    """Send a prompt to DeepSeek and return the text response."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[AI Error: {e}]"


# ---------------------------------------------------------------------------
# 1. Title Generation
# ---------------------------------------------------------------------------

def generate_title(content: str) -> str:
    """Generate a concise title for the note using DeepSeek."""
    prompt = (
        "Generate a short, descriptive title (maximum 8 words) for the following study note. "
        "Return ONLY the title text, no quotes, no markdown, no explanation.\n\n"
        f"{content[:1000]}"
    )
    title = _ask(prompt, max_tokens=30)
    return title.strip('"\'*#').strip()


# ---------------------------------------------------------------------------
# 2. Summarization
# ---------------------------------------------------------------------------

def generate_summary(content: str, num_sentences: int = 3) -> str:
    """
    Generate a summary using DeepSeek.
    Markdown and LaTeX are allowed — the UI renders them with marked.js + KaTeX.
    """
    prompt = (
        f"Summarize the following study note in {num_sentences} clear sentences. "
        "You may use Markdown formatting (bold, lists) and LaTeX math ($ for inline, $$ for block) if helpful. "
        "Return ONLY the summary, no intro phrase like 'This note...' or 'Here is a summary'.\n\n"
        f"{content[:3000]}"
    )
    return _ask(prompt, max_tokens=400)


# ---------------------------------------------------------------------------
# 3. Keyword Extraction
# ---------------------------------------------------------------------------

def extract_keywords(content: str, max_keywords: int = 8) -> list:
    """Extract key concepts/phrases using DeepSeek. Returns a list of strings."""
    prompt = (
        f"Extract the {max_keywords} most important key concepts or phrases from this study note. "
        "Return ONLY a JSON array of plain strings (no markdown, no LaTeX), "
        'for example: ["photosynthesis", "ATP", "chlorophyll"]. '
        "No explanation, no markdown code fences, just the JSON array.\n\n"
        f"{content[:3000]}"
    )
    raw = _ask(prompt, max_tokens=200)
    try:
        raw = re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()
        keywords = json.loads(raw)
        if isinstance(keywords, list):
            return [str(k) for k in keywords[:max_keywords]]
    except Exception:
        pass
    return [k.strip().strip('"\'') for k in raw.split(",")][:max_keywords]


# ---------------------------------------------------------------------------
# 4. Quiz Generation
# ---------------------------------------------------------------------------

def generate_quiz(content: str, num_questions: int = 5) -> list:
    """
    Generate a 5-question quiz (MCQ + True/False) using DeepSeek.
    Returns a list of question dicts compatible with the note.html UI.
    """
    prompt = (
        f"Create exactly {num_questions} quiz questions from this study note. "
        "Mix Multiple Choice (MCQ) and True/False questions. "
        "Return ONLY a valid JSON array. Each object must have these exact fields:\n"
        '  "type": "mcq" or "truefalse"\n'
        '  "question": the question text (plain text, no markdown)\n'
        '  "options": list of answer strings — 4 options for MCQ, ["True","False"] for T/F\n'
        '  "answer": the correct answer string (must exactly match one of the options)\n'
        '  "hint": one supporting sentence from the notes\n\n'
        "Return ONLY the JSON array, no markdown fences, no explanation.\n\n"
        f"{content[:3000]}"
    )
    raw = _ask(prompt, max_tokens=1500)
    try:
        raw = re.sub(r"```[a-z]*", "", raw).strip().strip("`").strip()
        quiz = json.loads(raw)
        if isinstance(quiz, list):
            valid = []
            for q in quiz:
                if all(k in q for k in ("type", "question", "options", "answer", "hint")):
                    valid.append(q)
            return valid[:num_questions]
    except Exception:
        pass
    return []