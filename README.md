# 📖 Study Notes Manager with AI Assistance

A Flask web app for creating and managing study notes with **fully local AI features** — no paid APIs, no internet required after setup.

---

## Features

| Feature | Details |
|---|---|
| Create / Edit / Delete notes | Full CRUD via web UI |
| Tag notes | Comma-separated tags, filterable |
| **AI: Title generation** | Extractive: picks the most informative opening phrase |
| **AI: Summary** | TextRank-inspired TF-IDF sentence scoring |
| **AI: Keyword extraction** | RAKE algorithm (implemented from scratch) |
| **AI: Quiz generation** | Mixed MCQ + True/False, NLP-based from note content |
| Search | Full-text search across title, content, tags, and keywords |
| Interactive quiz | Take the quiz in-browser with live scoring |

---

## Project Structure

```
study_notes_manager/
├── app.py             ← Flask routes (web server entry point)
├── ai_engine.py       ← All local NLP/AI: title, summary, RAKE, quiz
├── database.py        ← SQLite CRUD layer
├── seed_demo.py       ← Optional: seed with 3 sample notes
├── requirements.txt   ← Only Flask needed!
├── notes.db           ← Created automatically on first run
└── templates/
    ├── base.html      ← Layout, sidebar, nav
    ├── index.html     ← Note list
    ├── note.html      ← Single note view (summary, keywords, quiz)
    ├── editor.html    ← Create / edit form with live AI preview
    └── search.html    ← Search results
```

### Database Schema

```sql
CREATE TABLE notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    content     TEXT    NOT NULL,
    summary     TEXT,               -- AI-generated summary (stored)
    keywords    TEXT,               -- JSON array: ["photosynthesis","cell"]
    tags        TEXT,               -- user tags: "biology,exam"
    quiz        TEXT,               -- JSON array of question dicts
    created_at  TEXT,               -- ISO-8601
    updated_at  TEXT
);
```

---

## Setup

### 1. Install dependencies

```bash
cd study_notes_manager
pip install -r requirements.txt
```

> Only **Flask** is required. All AI runs on Python's standard library.

### 2. Run the app

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

### 3. (Optional) Seed demo notes

```bash
python seed_demo.py
```

Loads 3 sample notes (Biology, Physics, History) so you can explore all features immediately.

---

## AI Implementation Details

### Title Generation (`ai_engine.py → generate_title`)
- Extracts the first meaningful sentence
- If shorter than 8 words: uses it directly
- Otherwise: takes the first ~8 words, walking back to avoid ending on a stop word
- Title-cases the result

### Summarization (`generate_summary`)
- Computes **term frequency (TF)** for all content words (stop words excluded)
- Scores each sentence: `sum(TF[word]) / sentence_length`
- Applies **positional bias**: first sentence ×1.5, last sentence ×1.2
- Selects top N sentences; restores original document order

### Keyword Extraction — RAKE (`extract_keywords`)
**Rapid Automatic Keyword Extraction** (Rose et al., 2010):
1. Split text into candidate phrases at stop-word and punctuation boundaries
2. Compute `word_frequency` and `word_degree` (length of phrases containing it)
3. Word score: `degree(w) / frequency(w)`
4. Phrase score: sum of member-word scores
5. Return top phrases (deduplicated, substring-filtered)

### Quiz Generation (`generate_quiz`)
Three strategies applied in priority order:
- **Strategy A – Definition patterns**: regex detects `"X is/are Y"` → MCQ with other definitions as distractors
- **Strategy B – Keyword MCQ**: blanks a RAKE keyword in its sentence → MCQ
- **Strategy C – True/False**: uses real sentences (True) or keyword-swapped mutations (False)

---

## Usage Guide

### Creating a note
1. Click **New Note** or **+ New Note**
2. Paste your study material into the text area
3. Optionally add a title (or leave blank for AI-generated) and comma-separated tags
4. Click **✨ Preview AI Features** to see the AI output before saving
5. Click **💾 Save Note**

### Taking a quiz
1. Open any note
2. The right panel shows the AI-generated quiz
3. Select an answer; instant feedback and a final score appear

### Searching
- Use the sidebar search box or `/search?q=...`
- Searches title, content, tags, and AI-extracted keywords simultaneously

---

## Requirements

- Python 3.10+
- Flask 3.x
- SQLite (built into Python — no install needed)
- No GPU, no transformers, no paid APIs

---

## Extending the App

| Idea | Where to change |
|---|---|
| Use transformers for better summaries | `ai_engine.py → generate_summary` |
| Add spaCy NER for entity extraction | `ai_engine.py → extract_keywords` |
| User accounts / multi-user | Add `user_id` column to `notes` table |
| Export notes as PDF | Add a `/export/<id>` route |
| Dark/Light theme toggle | CSS variable swap in `base.html` |
