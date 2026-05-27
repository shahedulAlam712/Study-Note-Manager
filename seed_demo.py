"""
seed_demo.py — Populate the database with example study notes
Run once: python seed_demo.py
"""

import database as db
import ai_engine as ai

SAMPLE_NOTES = [
    {
        "title": "",   # Let AI generate
        "content": """
Photosynthesis is the process by which green plants convert sunlight into food.
It occurs mainly in the chloroplasts, which are organelles found in plant cells.
Chlorophyll is the green pigment that absorbs light energy, primarily from the
red and blue parts of the visible spectrum.

The overall reaction can be summarized as:
6CO2 + 6H2O + light energy → C6H12O6 + 6O2

Photosynthesis has two main stages. The light-dependent reactions occur in the
thylakoid membranes and produce ATP and NADPH. The Calvin cycle, also known as
the light-independent reactions, occurs in the stroma and uses the ATP and NADPH
to fix carbon dioxide into glucose. Oxygen is released as a by-product of the
light-dependent reactions when water molecules are split.
        """.strip(),
        "tags": "biology, plants, cellular-biology",
    },
    {
        "title": "Newton's Laws of Motion",
        "content": """
Newton's First Law states that an object at rest stays at rest, and an object in
motion stays in motion at constant velocity, unless acted upon by a net external force.
This is also called the law of inertia.

Newton's Second Law defines force as the product of mass and acceleration:
F = ma. The acceleration of an object is directly proportional to the net force
acting on it and inversely proportional to its mass.

Newton's Third Law states that for every action there is an equal and opposite
reaction. When object A exerts a force on object B, object B simultaneously
exerts a force of equal magnitude and opposite direction back on object A.

These three laws form the foundation of classical mechanics and were published
by Isaac Newton in his landmark work Principia Mathematica in 1687. They apply
to everyday objects moving at speeds much less than the speed of light.
        """.strip(),
        "tags": "physics, mechanics, classical-physics",
    },
    {
        "title": "",
        "content": """
The French Revolution was a period of radical political and societal transformation
in France that began in 1789 and ended in the late 1790s. The Revolution was
triggered by a combination of factors including financial crisis, social inequality,
and Enlightenment ideas about liberty and democracy.

The Third Estate, which represented commoners, declared itself the National Assembly
after being locked out of the Estates-General. The storming of the Bastille on
July 14, 1789 is considered the symbolic start of the Revolution.

Key phases include: the Constitutional Monarchy phase (1789–1792), the radical
Republic and the Reign of Terror under Robespierre (1793–1794), and the more
moderate Thermidorian Reaction and Directory (1795–1799). Napoleon Bonaparte
ended the Revolution by seizing power in the coup of 18 Brumaire in 1799.

The Revolution produced lasting changes: the abolition of feudalism, the Declaration
of the Rights of Man and Citizen, and the spread of revolutionary ideas across Europe.
        """.strip(),
        "tags": "history, europe, revolution",
    },
]

def main():
    db.init_db()
    print("Seeding demo notes...")
    for note_data in SAMPLE_NOTES:
        content = note_data["content"]
        title   = note_data["title"]
        tags    = note_data["tags"]

        gen_title  = title or ai.generate_title(content)
        summary    = ai.generate_summary(content, num_sentences=3)
        keywords   = ai.extract_keywords(content, max_keywords=8)
        quiz       = ai.generate_quiz(content, num_questions=5)

        nid = db.create_note(
            title=gen_title,
            content=content,
            summary=summary,
            keywords=keywords,
            tags=tags,
            quiz=quiz,
        )
        print(f"  ✓ Created: [{nid}] {gen_title}")

    print(f"\nDone! {len(SAMPLE_NOTES)} notes seeded.")
    print("Run:  python app.py   and open http://127.0.0.1:5000")

if __name__ == '__main__':
    main()
