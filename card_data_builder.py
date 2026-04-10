"""Build structured card data from longitudinal analysis JSON.

Takes the JSON output from longitudinal_analysis.py and produces a card-data
JSON blob that can feed into Writing Card HTML template generation.

Usage:
    python card_data_builder.py longitudinal_elliott.json [--holefilling "Sentences"]
"""

import json
import sys
from pathlib import Path

# AlphaWrite practice URL slugs — kept in sync with longitudinal_analysis.py
SKILL_PRACTICE_SLUGS = {
    "Fragment or Sentence?": "fragment-or-sentence",
    "Unscramble Sentences": "unscramble-sentences",
    "Identify the Sentence Type": "identify-sentence-type",
    "Change the Sentence Type": "change-sentence-type",
    "Write the Sentence Type": "write-sentence-type",
    "Because, But, So": "basic-conjunctions",
    "Identify Appositives": "identify-appositives",
    "Write Appositives": "write-appositives",
    "Complete Subordinating Conjunctions": "subordinating-conjunctions",
    "Combine Sentences": "combine-sentences",
    "Kernel Expansion": "kernel-expansion",
    "Write Sentence from a Prompt": "write-sentence-from-prompt",
    "Identify Topic Sentences": "identify-topic-sentence",
    "Identify Topic Sentence and Sequence Details": "identify-ts-and-sequence-details",
    "Eliminate Irrelevant Sentences": "eliminate-irrelevant-sentences",
    "Elaborate on Paragraphs": "elaborate-paragraphs",
    "Using Transition Words": "using-transition-words",
    "Write a Free-Form Paragraph": "write-freeform-paragraph",
    "Write a Paragraph from Prompt": "write-paragraph-from-prompt",
    "Writing SPOs": "writing-spos",
    "Turn Outline into Draft": "turn-outline-into-draft",
}


def get_practice_url(skill_name: str, grade: int) -> str | None:
    slug = SKILL_PRACTICE_SLUGS.get(skill_name)
    if not slug:
        return None
    return f"https://alphawrite.alpha.school/practice/{grade}/2/{slug}"


def score_color(score: int) -> str:
    if score >= 90:
        return "green"
    if score >= 70:
        return "amber"
    return "red"


def build_card_data(longitudinal: dict, holefilling_course: str | None = None) -> dict:
    """Transform longitudinal analysis output into card-ready data.

    Args:
        longitudinal: Parsed JSON from longitudinal_analysis.py
        holefilling_course: Name of the assigned hole-filling course, if any
            (e.g. "Sentences", "Paragraphs", "Essays")

    Returns:
        Structured dict ready for template rendering.
    """
    grade_level = longitudinal["grade_level"]  # e.g. "G6"
    grade_num = int(grade_level[1:])
    card_width = "640px" if grade_num <= 5 else "680px"

    tests = longitudinal["tests_analyzed"]
    latest = tests[-1] if tests else None

    # Score timeline
    score_timeline = []
    for t in tests:
        score = t["score"]
        score_timeline.append({
            "test": t["test_number"],
            "date": t["date"],
            "score": score,
            "color": score_color(score),
        })

    # Strength chips — only fully mastered skills (avg >= 0.9)
    strength_chips = []
    for s in longitudinal.get("strengths", []):
        strength_chips.append({
            "name": s["label"],
            "course": s.get("course", ""),
        })

    # Growth areas — weaknesses + mixed skills below 90% (if student hasn't passed)
    overall_avg = sum(t["score"] for t in tests) / len(tests) if tests else 0
    passed = overall_avg >= 90

    growth_areas = []
    for w in longitudinal.get("weaknesses", []):
        growth_areas.append({
            "name": w["label"],
            "course": w.get("course", ""),
            "avg": w["avg_score"],
            "practice_url": w.get("practice_url"),
            "trend": w.get("trend"),
            "severity": "weak",
        })

    if not passed:
        # Promote mixed skills into growth areas
        for m in longitudinal.get("mixed", []):
            growth_areas.append({
                "name": m["label"],
                "course": m.get("course", ""),
                "avg": m["avg_score"],
                "practice_url": m.get("practice_url"),
                "trend": m.get("trend"),
                "severity": "mixed",
            })

    # Sort: weakest first
    growth_areas.sort(key=lambda x: x["avg"])

    # Root cause teaser — identify the single biggest driver
    root_cause_teaser = _build_root_cause_teaser(longitudinal, growth_areas)

    # Pattern notes — mapped to skill names, to be attached to relevant fix cards
    pattern_notes = _build_pattern_notes(longitudinal)

    # Practice recommendations — two tiers
    practice_recs = _build_practice_recommendations(
        longitudinal, growth_areas, grade_num, holefilling_course
    )

    # Trends
    improving = [
        {"name": r["label"], "from": r.get("first_avg", 0), "to": r.get("second_avg", 0)}
        for r in longitudinal.get("improving", [])
    ]
    declining = [
        {"name": r["label"], "from": r.get("first_avg", 0), "to": r.get("second_avg", 0)}
        for r in longitudinal.get("declining", [])
    ]

    return {
        "student_name": longitudinal["student_name"],
        "grade_level": grade_level,
        "grade_number": grade_num,
        "card_width": card_width,
        "latest_test": {
            "test_number": latest["test_number"],
            "date": latest["date"],
            "score": latest["score"],
        } if latest else None,
        "overall_avg": round(overall_avg, 1),
        "passed": passed,
        "score_timeline": score_timeline,
        "strength_chips": strength_chips,
        "growth_areas": growth_areas,
        "root_cause_teaser": root_cause_teaser,
        "pattern_notes": pattern_notes,
        "practice_recommendations": practice_recs,
        "improving": improving,
        "declining": declining,
    }


def _build_root_cause_teaser(longitudinal: dict, growth_areas: list) -> str:
    """Generate a 1-line root cause teaser for the Journey Context card."""
    # Check if Essays are in growth areas — this is usually the biggest driver
    essay_area = next((g for g in growth_areas if g["name"] == "Essays"), None)

    if essay_area:
        grade_num = int(longitudinal["grade_level"][1:])
        if grade_num >= 6:
            return (
                "Your essay scores have a clear pattern across tests "
                "\u2014 keep reading to see what drives them up and down."
            )
        else:
            return (
                "Your paragraph writing scores have a clear pattern across tests "
                "\u2014 keep reading to see what makes the difference."
            )

    # Fall back to the weakest skill
    if growth_areas:
        weakest = growth_areas[0]
        return (
            f"{weakest['name']} has been tricky for you across multiple tests "
            "\u2014 the next cards show you the pattern and how to fix it."
        )

    return "Keep reading to see specific feedback on your latest test."


def _build_pattern_notes(longitudinal: dict) -> dict:
    """Build pattern note text keyed by skill name.

    These get attached to the relevant fix cards in the slideshow.
    """
    notes = {}

    # Check essay/paragraph writing pattern
    essay_history = longitudinal.get("standard_history", {}).get("Essays", [])
    paragraph_history = longitudinal.get("standard_history", {}).get(
        "Write a Free-Form Paragraph", []
    )

    writing_history = essay_history or paragraph_history
    if len(writing_history) >= 2:
        scores = [e["correct_fraction"] for e in writing_history if e["correct_fraction"] is not None]
        if scores:
            avg = sum(scores) / len(scores)
            if avg < 0.9:
                test_count = len(writing_history)
                skill_name = "Essays" if essay_history else "Write a Free-Form Paragraph"
                notes[skill_name] = (
                    f"This is part of a pattern across your last {test_count} tests. "
                    "The structure of your writing is the consistent difference-maker."
                )

    # Check MCQ weaknesses
    for w in longitudinal.get("weaknesses", []):
        label = w["label"]
        if label in ("Essays", "Write a Free-Form Paragraph"):
            continue
        entries = w.get("entries", [])
        wrong_count = sum(1 for e in entries if e.get("correct_fraction", 1) < 1.0)
        total = len(entries)
        if wrong_count >= 2:
            notes[label] = (
                f"You've missed {label} questions on {wrong_count} of {total} tests "
                "\u2014 the pattern is the same each time."
            )

    # Check declining trends
    for d in longitudinal.get("declining", []):
        label = d["label"]
        if label not in notes:
            first = d.get("first_avg", 0)
            second = d.get("second_avg", 0)
            notes[label] = (
                f"{label} started strong ({first:.0%}) but has been slipping ({second:.0%}) "
                "\u2014 this card explains why."
            )

    return notes


def _build_practice_recommendations(
    longitudinal: dict,
    growth_areas: list,
    grade_num: int,
    holefilling_course: str | None = None,
) -> dict:
    """Build two-tier practice recommendation structure."""
    tier1 = None
    if holefilling_course:
        tier1 = {
            "course_name": holefilling_course,
            "xp_per_activity": 15,
        }

    # Tier 2: AlphaWrite practice for skills NOT covered by hole-filling
    tier2 = []
    seen = set()

    for area in growth_areas:
        name = area["name"]
        if name in seen:
            continue
        if name in ("Essays",):
            # Essays don't have direct practice — recommend related paragraph skills
            continue
        url = area.get("practice_url") or get_practice_url(name, grade_num)
        if url and (not holefilling_course or area.get("course") != holefilling_course):
            tier2.append({"name": name, "url": url})
            seen.add(name)

    # Always recommend paragraph planning skills if paragraphs/essays are a growth area
    writing_weak = any(
        a["name"] in ("Essays", "Write a Free-Form Paragraph") for a in growth_areas
    )
    if writing_weak:
        for extra_skill in [
            "Writing SPOs",
            "Write a Paragraph from Prompt",
            "Elaborate on Paragraphs",
            "Write a Free-Form Paragraph",
        ]:
            if extra_skill not in seen:
                url = get_practice_url(extra_skill, grade_num)
                if url:
                    tier2.append({"name": extra_skill, "url": url})
                    seen.add(extra_skill)

    return {
        "tier1_holefilling": tier1,
        "tier2_extra": tier2,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python card_data_builder.py <longitudinal.json> [--holefilling <course>]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    holefilling = None

    if "--holefilling" in sys.argv:
        idx = sys.argv.index("--holefilling")
        if idx + 1 < len(sys.argv):
            holefilling = sys.argv[idx + 1]

    with open(input_path, encoding="utf-8") as f:
        longitudinal = json.load(f)

    card_data = build_card_data(longitudinal, holefilling)

    out_path = input_path.with_name(input_path.stem + "_card_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(card_data, f, indent=2, default=str)

    print(f"Card data written to {out_path}")
    print(f"Student: {card_data['student_name']}")
    print(f"Timeline: {' -> '.join(f'{t['test']}: {t['score']}%' for t in card_data['score_timeline'])}")
    print(f"Strengths: {len(card_data['strength_chips'])}")
    print(f"Growth areas: {len(card_data['growth_areas'])}")
    print(f"Pattern notes: {list(card_data['pattern_notes'].keys())}")
    print(f"Tier 2 practice: {[p['name'] for p in card_data['practice_recommendations']['tier2_extra']]}")


if __name__ == "__main__":
    main()
