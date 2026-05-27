"""
app.py — Flask web application for Study Notes Manager
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import database as db
import ai_engine as ai
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "study-notes-secret-key")


def _run_ai(title: str, content: str) -> dict:
    generated_title = title.strip() if title.strip() else ai.generate_title(content)
    summary  = ai.generate_summary(content, num_sentences=3)
    keywords = ai.extract_keywords(content, max_keywords=8)
    quiz     = ai.generate_quiz(content, num_questions=5)
    return {'title': generated_title, 'summary': summary, 'keywords': keywords, 'quiz': quiz}


@app.route('/')
def index():
    notes = db.get_all_notes()
    return render_template('index.html', notes=notes)


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    results = db.search_notes(query) if query else []
    return render_template('search.html', results=results, query=query)


@app.route('/note/<int:note_id>')
def view_note(note_id):
    note = db.get_note(note_id)
    if not note:
        flash('Note not found.', 'error')
        return redirect(url_for('index'))
    return render_template('note.html', note=note)


@app.route('/new', methods=['GET', 'POST'])
def new_note():
    if request.method == 'POST':
        title   = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        tags    = request.form.get('tags', '').strip()
        if not content:
            flash('Note content cannot be empty.', 'error')
            return render_template('editor.html', note=None, title=title, content=content, tags=tags)
        ai_result = _run_ai(title, content)
        note_id = db.create_note(
            title=ai_result['title'], content=content, summary=ai_result['summary'],
            keywords=ai_result['keywords'], tags=tags, quiz=ai_result['quiz'],
        )
        flash('Note created successfully!', 'success')
        return redirect(url_for('view_note', note_id=note_id))
    return render_template('editor.html', note=None, title='', content='', tags='')


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = db.get_note(note_id)
    if not note:
        flash('Note not found.', 'error')
        return redirect(url_for('index'))
    if request.method == 'POST':
        title   = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        tags    = request.form.get('tags', '').strip()
        if not content:
            flash('Note content cannot be empty.', 'error')
            return render_template('editor.html', note=note, title=title, content=content, tags=tags)
        ai_result = _run_ai(title, content)
        db.update_note(
            note_id=note_id, title=ai_result['title'], content=content,
            summary=ai_result['summary'], keywords=ai_result['keywords'],
            tags=tags, quiz=ai_result['quiz'],
        )
        flash('Note updated successfully!', 'success')
        return redirect(url_for('view_note', note_id=note_id))
    return render_template('editor.html', note=note, title=note['title'], content=note['content'], tags=note['tags'])


@app.route('/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    db.delete_note(note_id)
    flash('Note deleted.', 'info')
    return redirect(url_for('index'))


@app.route('/api/preview-ai', methods=['POST'])
def preview_ai():
    data    = request.get_json()
    content = (data.get('content') or '').strip()
    title   = (data.get('title')   or '').strip()
    if not content:
        return jsonify({'error': 'No content provided'}), 400
    return jsonify(_run_ai(title, content))


if __name__ == '__main__':
    db.init_db()
    print("\n🎓 Study Notes Manager running at http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)