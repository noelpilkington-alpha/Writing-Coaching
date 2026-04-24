# Writing Coaching Card Principles

**Audience:** anyone (human or AI agent) building a new writing coaching card for a student.
**Scope:** every card committed to this repo must follow these rules. When in doubt, prefer the rule over the shortcut — each rule exists because it was violated in a past card and the user caught it.

Read this before you run the pipeline or write HTML. If you are delegating card creation to a sub-agent, pass this file as required reading.

---

## 1. Pipeline — how a card gets built

Every card follows the same four-step pipeline. Never skip steps; never ship a card without steps 1–3.

### 1.1 Longitudinal analysis

```
cd c:/Users/noelp/Timeback/
python longitudinal_analysis.py "FirstName LastName" G<n>
mv longitudinal_output.json longitudinal_<name>.json
```

This fetches **all** of the student's Writing tests at their current grade level from the Timeback API, parses question-level answers, and classifies each question against the AlphaWrite skill plan. Output includes strengths, weaknesses, mixed skills, improving/declining trends, and the full `standard_history`.

### 1.2 Card data builder

```
cd c:/Users/noelp/Student Deep Dives/AlphaWrite Deep Dives/Writing-Coaching-Temp/
cp c:/Users/noelp/Timeback/longitudinal_<name>.json .
python card_data_builder.py longitudinal_<name>.json [--holefilling "Sentences"]
```

Outputs `longitudinal_<name>_card_data.json`: score timeline, strength chips, growth chips, root cause teaser, pattern notes keyed by skill, and two-tier practice recommendations.

### 1.3 Build HTML card

Use the latest well-formed card as your structural reference (today: `Kira-Fuerst-G3-4/index.html`). Copy CSS and JS **verbatim**. Only change:
- `<title>` in `<head>`
- The cards inside `<div class="card-container">` (7 cards total)
- The completion overlay text

### 1.4 Register on homepage

Edit `index.html` to add the new card to:
- **Latest** tab: a new `data-date="YYYY-MM-DD"` section at the top, grouped by DRI
- **By Campus** tab: the student's campus section (update the `student-count-badge` accordingly)
- Header `.student-count` totals (students and card sets)

### 1.5 Prior score lookup

Every student's prior test history must be fetched **automatically** from the writing-results CSV — never hardcoded or bolted on after QC catches a gap.

- The authoritative source is the latest `writing-results-YYYY-MM-DD.csv` in `c:/Users/noelp/Timeback/Daily workflow/`
- The Timeback API is equally authoritative and can include same-day tests the CSV snapshot missed
- Prior card HTML files are a **bonus** source for pattern notes — never the primary timeline source
- A student with no prior coaching card still has a full test history; the pipeline must surface it

**Why:** the user caught 6 students missing longitudinal journey cards because an earlier pipeline only checked for prior card HTML.

---

## 2. Scoring methodology

Writing tests are **weighted rubrics**, not simple averages of 11 questions. The TimeBack longitudinal API returns pre-calculated scores using this system. You only need to compute scores manually when reading raw CSV data.

### 2.1 G3–G5 tests (45 points total)

| Questions | Type | Points each | Total |
|-----------|------|-------------|-------|
| Q1–Q5 | Editing | **2 pts** | 10 |
| Q6–Q10 | Sentence Writing | **3 pts** | 15 |
| Q11 | Paragraph | **20 pts** | 20 |

### 2.2 G6+ tests (30 points total)

| Questions | Type | Points each | Total |
|-----------|------|-------------|-------|
| Q1–Q10 | Multiple Choice | **1 pt** | 10 |
| Q11 | Essay | **20 pts** | 20 |

### 2.3 Mapping CSV fractions to points

The CSV "Score" column is a fraction of each question's max. Convert carefully:

| CSV fraction | On Q1–Q5 (2 pts) | On Q6–Q10 (3 pts) | On Q11 (20 pts) |
|--------------|-----------------|-------------------|-----------------|
| 0.33 | 0.67 pts | **1 of 3** | 6.6/20 |
| 0.5 | **1 of 2** | 1.5/3 | 10/20 |
| 0.67 | 1.33/2 | **2 of 3** | 13.3/20 |
| 0.85 | 1.7/2 | 2.55/3 | **17/20** |
| 1.0 | 2/2 | 3/3 | 20/20 |

### 2.4 Student-facing score references — DO THIS

- ✅ "Q6 earned 2 of 3 points" (Q6–Q10 is a 3-point question)
- ✅ "Q1 missed 1 point out of 2" (Q1 is a 2-point question)
- ✅ "13/20" or "17/20" for Q11
- ✅ Overall score as a percentage (e.g., "66%")

### 2.5 Student-facing score references — DO NOT DO THIS

- ❌ "0.67 / 1" (Q6–Q10 is not scaled to 1)
- ❌ "0.33 on G3.4 instead of 1.0" (treats the CSV fraction as the point value)
- ❌ "a half point" for a 0.5 partial on a Q1-style question (that's 1 point of 2)
- ❌ Simple-averaging all 11 questions (massively underweights Q11)

**Why the score-naming rule is strict:** a Q6–Q10 at "0.67" is 2 of 3 points, not "0.67 out of 1" — framing it as "out of 1" hides that the student left **2 full points** on the table, not 0.33 of one point.

---

## 3. Content rules — what the student sees

### 3.1 No teacher references

Cards must never say "teacher," "your teacher," or "the teacher."

Use instead:
- "grading feedback"
- "your feedback noted..."
- Passive constructions: "your essay was praised for..."

**Why:** cards are generated from AI grading + test scoring data, not a specific teacher's comments. Using "teacher" is inaccurate and confusing.

### 3.2 Address the student directly

Use second person ("you") and the student's first name throughout. Never third-person references ("the student," "students should...").

The card is FOR the student — first person feels personal and actionable.

### 3.3 Student-friendly vocabulary

All text visible to students must use simple, age-appropriate words.

**Never use** these abbreviations in student-facing text (spell them out):

| Jargon | Plain replacement |
|--------|-------------------|
| BP1, BP2 | Body 1, Body 2 |
| TS | Topic Sentence |
| CONC | Ending / Closing |
| E1, X1 | Evidence, Explain why |
| CS | Closing Sentence |
| MCQ | multiple choice |
| SPO | Paragraph Outline (add "(Paragraph Outline)" parenthetical) |

**Avoid** advanced words that many target-grade students won't know:
- concede, interrogative, cognitive, fluency, legitimate, bare verb

Curriculum terms (e.g., "appositives") are fine when that's the skill being taught. Test: could a typical student in the target grade read this without asking "what does that mean?"

**Kernel Expansion** exception: keep "Kernel Expansion" for AlphaWrite practice link labels (that's the platform name), but use "Adding Details to Sentences" in the explanation copy.

### 3.4 Evidence, not direct quotes

Cards must **never** tell students that direct quotes are required for essay evidence. Students can quote OR paraphrase — both are valid. The key requirement is **specific details** from the passage + **explain what they show**.

**Use** this language:
- "Evidence Sandwich" (not "Quote Sandwich")
- "Use specific details from the passage (quoted or paraphrased)"
- "No specific evidence from the passage" (when flagging a gap — not "no direct quotes")

**Model rewrites** can use direct quotes as one example, but the teaching language must not present quoting as the only correct approach. When praising a student who DID quote, it's fine to mention — just don't prescribe quoting.

**Show HOW to quote and paraphrase.** Saying "quoted or paraphrased" without showing the point-earning technique is not enough. Every card that teaches Evidence Sandwich must include concrete DO/DO NOT guidance:

**Quoting well:**
- DO pull a short, exact phrase (2–8 words) and put it in "double quotation marks"
- DO introduce with "The article says…" / "The passage explains…" so the grader sees it's the author's words
- DON'T copy a whole sentence or paragraph — long quotes don't show understanding, they fill space
- DON'T drop a bare quote — always add a sentence explaining what it shows

**Paraphrasing well:**
- DO put the idea in your own words while keeping the **specific fact** (name, place, date, number, what someone did)
- DO keep the detail specific — "people played sports" is too general; "British schools wrote down cricket rules in the 1800s" has the fact
- DON'T copy word-for-word without quotation marks — that's not paraphrasing and can lose points
- DON'T leave out the specific fact — every paraphrase needs at least one concrete detail anchored in the passage

### 3.5 Q6–Q10 on G3–G5 are one-sentence, three-point questions

On G3–G5 writing tests, Questions 6–10 are **Write Sentence from a Prompt** items. The prompt explicitly instructs students to write **one sentence** that includes a reason, explanation, or example. Each question is worth **3 points**.

**Coaching rules:**
- Prescribe **one sentence** that joins the opinion to a reason/example from the passage using "because" (or similar joining word)
- Never "write two sentences" or "first sentence... second sentence..."
- Two-part prompts (e.g., "What is one rule? Why is it important?") still expect one sentence — the "because" clause covers part 2 inside the same sentence
- Reference scores as "X of 3 points", never "X / 1" or "X.XX out of 1.0"

**Why:** on Ozzie's and Brooks's initial drafts I violated both rules. The test prompt itself says "in one sentence" — telling students to write two directly contradicts the assessment.

### 3.6 Tests are digital — no paper-based instructions

The Alpha Standardized Writing tests run in a browser. Students type answers into a text box; there is no paper, no pencil, and no margin.

**Never** instruct students to:
- ❌ "Circle the word 'and'"
- ❌ "Underline the verb"
- ❌ "Jot the outline in the margin"
- ❌ "Put down your pencil"
- ❌ "Mark the passage with a highlighter"

**Use** digital-friendly alternatives:
- ✅ "Look for the word 'and'" / "notice the second question mark"
- ✅ "Find the verb and say it out loud to yourself"
- ✅ "Type a quick outline at the top of the answer box, draft your paragraph below it, then delete the outline before you submit"
- ✅ "Your hand is off the keyboard"
- ✅ "Re-read the passage in the panel above"

**Why:** Ozzie's card told him to "circle or underline the word 'and'" on a digital test. Students literally cannot do this. Paper-era habits (margin notes, pencil marks) don't translate — the coaching has to match the actual test environment.

### 3.7 Score references must name the correct denominator

Every student-facing score reference must match the question's actual point value from Section 2.

**Examples:**
- ✅ "Q1 earned 0 of 2 points" (Q1-Q5 on G3-G5 is 2-point)
- ✅ "Q6 earned 2 of 3 points" (Q6-Q10 on G3-G5 is 3-point)
- ✅ "Q11 earned 13/20"
- ✅ Q1-Q10 total on G3-G5 is out of **25 points** (Q1-Q5 = 10, Q6-Q10 = 15)
- ❌ "Q1-Q10 = 9.5/10" (Q1-Q10 is worth 25 points, not 10)
- ❌ "Q6 got 0.67 / 1" (Q6-Q10 is 3-point)
- ❌ "Q1 lost a half point" (partial 0.5 on a 2-pt Q1 = 1 point lost)

**Why:** Ozzie's card showed "9.5/10" for Questions 1-10 and elsewhere said "Q1 got 0 pts" — the numbers were internally inconsistent (if Q1-Q10 is out of 10 and Q1 is 0, the rest can't average to 9.5). The Q1-Q10 box must use the correct /25 denominator so the overall percentage math checks out.

### 3.8 Pacing: the test typically takes 30–40 minutes, not 60

The Alpha Writing tests have a generous time limit (roughly 60 minutes available) but most students who do well finish in **about 30–40 minutes**. That's the realistic working time, not a target to race against and not a target to pad.

**Use** this framing:
- ✅ "Most students who do well take about 30–40 minutes"
- ✅ "Give the test the time it needs — don't race, don't pad"
- ✅ "If you finish in 15 minutes you've rushed — go back and proofread"
- ✅ Pacing plan: 5–7 min passage read + 10–12 min Q1–Q10 + 1 min SPO + 10–12 min Q11 + 5–8 min proofread ≈ 30–40 min total

**Don't** use these patterns:
- ❌ "You have 60 minutes — use them all"
- ❌ "Don't submit until the clock shows 30 minutes at minimum"
- ❌ Score-grid box that says "60 / Minutes Allowed" (implies the full 60 is the target)
- ❌ Pacing plans that allocate the full 60 minutes — that tells a student a proper test takes an hour

**Why:** Alex's prep card originally told him "you have 60 minutes, use them" and allocated a 60-minute pacing plan. The user flagged that a good test usually takes 30–40 minutes; a 60-minute plan sets an unrealistic and counterproductive target. The goal is "enough time to do careful work," not "maximum time."

### 3.9 Use "Supporting Detail" — not "Body" — for paragraph structure

When teaching paragraph structure on G3–G5 cards, use the term **Supporting Detail** (not "Body," "Body 1 / Body 2," or "body sentence"). The curriculum term for the middle rows of a Single Paragraph Outline is Supporting Detail (often abbreviated **D1 / D2** in shorthand outlines).

**Use** this language:
- ✅ SPO rows: TOPIC / **DETAIL 1** / **DETAIL 2** / CLOSE
- ✅ "2–3 supporting details, each pulling a specific fact from the passage"
- ✅ Shorthand outlines: "D1: …" / "D2: …"

**Don't** use:
- ❌ "Body 1 / Body 2 / B1 / B2"
- ❌ "body sentence," "body point," "body idea"
- ❌ Tag labels like `BODY 1` / `BODY 2` on outline rows

"Body" is essay-level vocabulary (body paragraphs) — it's inaccurate and confusing when applied to a single paragraph's internal structure.

### 3.10 Pre-test prep cards must not reference real test passages

When a card is a **pre-test prep** for a student who hasn't yet taken the test, every example — prompts, model paragraphs, SPO topics, proofread discrim challenges — must use **invented, clearly-labeled practice content**. Don't pull phrases, characters, places, or topics from any real test form.

**Use** this pattern:
- ✅ Invent a generic topic (e.g., a community garden, a bakery opening, a kid building a fort) and label it as "a made-up practice passage"
- ✅ Put a one-line disclaimer on the card: "the examples here use a made-up practice passage — the goal is to show you the structure, not to give you content"
- ✅ In discrim prompts, prefix with "Practice prompt (made-up): …"

**Don't** use:
- ❌ Passage names or topics that appear on any real test: Sports and Society, Pokemon / Satoshi Tajiri, Anna + Sally the seal, Layla + the geode, Garissa Camel Library, Hershey Bears, Soil vs Dirt, or any other real passage
- ❌ Character names from real passages (Anna, Jim, Sally, Layla, Tajiri, etc.)
- ❌ Specific model paragraphs that mirror the organization or facts of a real passage

**Why:** Alex's prep card originally used the Sports and Society passage (from G3.4) as its SPO example, and Anna/Sally/Lucy references in the proofread card. If a student studying the prep card later sees the same passage on a real test, the prep card has given them advance content — which is both unfair and useless (they've already practiced the specific answer). Prep content must teach **structure and habits** using clearly invented examples.

**Double-check:** before shipping a prep card, grep the final HTML for every test passage you know of — sports/cricket/britain/1800s, pokemon/tajiri/bug, anna/sally/seal, layla/geode, garissa/camel, hershey/bear, soil/dirt, lucy/rocket — and confirm zero matches.

---

## 4. Design principles — how cards teach

These come from the Writing Brainlift (Alpha's K–12 writing curriculum document) and the Elliott Wendt full-journey card that established the standard.

### 4.1 Discrimination before production

On every fix card, students must first **identify the problem** via an interactive challenge BEFORE seeing the explanation.

- Implement with `.discrim-challenge` containing force-correct multiple choice
- Wrong answer: reset after 2 seconds with feedback
- Correct answer: reveal `.discrim-then` content (the teaching, models, examples)

**Why (SPOV Truth 9):** seeing the answer first means students don't build the discrimination muscle. Making them choose first activates retrieval.

### 4.2 Wise feedback / Mentor Mindset

Card 1 must frame feedback as "I have high standards because I know you can meet them."

- Reference the student's **proven capability** on past tests
- Never deficit-frame ("you are bad at X")
- Acknowledge real struggle honestly, then point to their own prior evidence of capability

**Why (Yeager research):** high-standards-plus-belief framing outperforms both pure praise and pure correction on measurable learning.

### 4.3 Bridge language

Explicitly connect sentence-level skills to essay/paragraph quality.

- "This same skill is what makes body paragraphs convincing in your essays"
- "Kernel Expansion is also what lifts a 15/20 paragraph to 18/20"

Don't let students think sentence fixes and essay fixes are unrelated silos.

### 4.4 Planning elevation

Planning before writing is the **single highest-leverage intervention** (Brainlift Insight 3, effect size g=5.54).

- Elevate planning to checklist item **#1**
- Include a "30-second planning trick" on essay/paragraph cards
- Recommend Writing SPOs (Paragraph Outlines) alongside Write a Paragraph from Prompt whenever paragraphs are a growth area

### 4.5 "So what?" prompts

After every piece of evidence, the student should ask **"So what? Why does this matter?"** — the answer is the explanation.

This replaces abstract instruction about "elaboration." Include a "So What? Why Does This Matter?" box in every fix card's `.discrim-then`.

### 4.6 Root cause diagnosis on the Journey card

Connect related skills rather than listing them as separate issues.

- Example: Kernel Expansion (sentence-level idea expansion) is often the root cause of weak essay scores — they share the same underlying skill
- Present the foundational skill as the root cause and explain the connection
- Don't just list "Kernel Expansion" and "Essays" as two separate weaknesses

### 4.7 Never show false "no weaknesses"

If a student's overall score is below 90%, they must **always** see growth areas on the Journey card.

- Mixed-range skills (70–89%) get promoted into growth areas when no skill falls below 70%
- Never display "no weaknesses" for a student scoring 82–89% overall — it's misleading

### 4.8 Paragraph practice recommendations

When paragraph writing is a growth area:
- Prefer **"Write a Paragraph from Prompt"** over "Write a Free-Form Paragraph" (more structured, builds fluency)
- Always also recommend **"Writing SPOs (Paragraph Outlines)"** — planning is foundational to paragraph quality

---

## 5. Required UI features

Every new card must include all of these. If any are missing, the card is not shippable.

### 5.1 Structural HTML

- `<meta name="viewport" content="width=device-width, initial-scale=1.0">` in `<head>`
- `<div class="progress-bar" id="progressBar"></div>` at top
- `<div class="card-breadcrumb" id="breadcrumb"></div>` below progress bar
- `<div class="sticky-indicator" id="stickyIndicator"></div>` for fixed scroll indicator
- `<div class="completion-overlay" id="completionOverlay">` with emoji, title, 3 goals, close button
- `<canvas id="confettiCanvas"></canvas>` before the `<script>` block
- `<script src="../tracking.js"></script>` as the LAST script, just before `</body>`

### 5.2 Progress bar with labels

- `data-title` attribute on each `.card` div
- Tooltip on each progress dot (appears on hover)
- Breadcrumb below dots: "Card X of Y — Title"
- Sticky "X / Y" pill in top-right when progress bar scrolls off screen

### 5.3 Reveal interaction on every `.better` div

Every `.better` (improved/model answer) must be wrapped in `.reveal-wrapper` with `.reveal-cover` + `.reveal-content`:

```html
<div class="reveal-wrapper">
  <div class="reveal-cover" onclick="revealBetter(this)">
    <div class="reveal-icon"><svg>...</svg></div>
    <div>
      <div class="reveal-text">Tap to see the improved version</div>
      <div class="reveal-hint">Read yours first — then compare</div>
    </div>
  </div>
  <div class="reveal-content">
    <div class="better">...</div>
  </div>
</div>
```

**Why:** forces students to read their own writing before seeing the model — prevents passive skim-and-nod.

### 5.4 Discrimination challenge on every fix card

```html
<div class="discrim-challenge">
  <div class="discrim-prompt">...</div>
  <div class="discrim-options">
    <div class="discrim-option" data-correct="false"
         data-wrong-feedback="..." onclick="handleDiscrim(this)">...</div>
    <div class="discrim-option" data-correct="true"
         data-right-feedback="..." onclick="handleDiscrim(this)">...</div>
  </div>
  <div class="discrim-feedback"></div>
</div>
<div class="discrim-then">
  <!-- teaching content, models, "so what?" box -->
</div>
```

The `handleDiscrim()` JS in the template handles force-correct logic.

### 5.5 Tappable checkboxes with progress

- `.check-item` with `onclick="toggleCheck(this)"`
- 28px `.check-box` inside each item
- Green `.checked` state with strikethrough text
- Progress bar (`.checklist-progress`) above the checklist with live "X of Y checked" label

### 5.6 Pattern notes (purple banner) on fix cards

Connect the specific error on this card to the longitudinal trend:

```html
<div class="pattern-note">
  <span class="pattern-note-icon">🔍</span>
  <span><b>Pattern alert:</b> You've missed this skill on 3 of 4 tests — the pattern is the same each time.</span>
</div>
```

### 5.7 Print button on the checklist card

Every card's Card 7 (checklist) must include a functional Print button:

```html
<button class="print-btn" onclick="printChecklist(this)">
  <svg viewBox="0 0 24 24"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/></svg>
  Print this checklist
</button>
```

`printChecklist()` must remove checked state before printing (so the student has a blank checklist to use) and restore it after.

### 5.8 Completion celebration

On clicking "Done" on the last card:
- Trigger `.completion-overlay` with student name + 3 concrete goals for next test
- Launch confetti animation via `launchConfetti()`

### 5.9 Clean print CSS

`@media print` rules must hide: `.progress-bar`, `.nav`, `.print-btn`, `.card-breadcrumb`, `.sticky-indicator`, `.completion-overlay`, `#confettiCanvas`, `.reveal-cover`, `.checklist-progress`, `.discrim-challenge`. Show only the `.card.print-target` with revealed content expanded.

### 5.10 Two-tier practice recommendations

On Card 7, below the checklist:

- **Tier 1 (Start Here)**: present ONLY if the student has an assigned hole-filling course. Lists activities in that course that target the exact skills from this review.
- **Tier 2 (Extra Practice)**: AlphaWrite practice links for growth-area skills not covered by Tier 1. Always include "Write a Paragraph from Prompt" + "Writing SPOs (Paragraph Outlines)" if paragraphs are a growth area.

All links use `https://alphawrite.alpha.school/practice/<grade>/2/<slug>` format.

---

## 6. 7-card structure (standard template)

| # | Card | Purpose |
|---|------|---------|
| 1 | Score Overview | Header with score boxes, wise-feedback framing, big-idea teaser |
| 2 | Your Writing Journey | Score timeline, strength chips, growth chips, root cause teaser — NO practice links |
| 3 | Fix Card 1 | Biggest/root-cause growth area — discrim challenge + pattern note + teaching |
| 4 | Fix Card 2 | Second growth area — same structure |
| 5 | Fix Card 3 | Third growth area — same structure |
| 6 | Fix Card 4 — Proofread / CUPS | Personalized proofreading checklist with specific errors from this student's tests |
| 7 | Your Checklist & Practice | PLAN FIRST as item #1, other goals, two-tier practice, Print button |

You can vary the middle cards' focus based on the student's data, but never ship fewer than 7 cards or skip the Journey card.

---

## 7. QC checklist — run before committing

Grep/search the finished HTML for each of these:

### Content
- [ ] Zero "teacher" references: `grep -i teacher index.html` returns no hits
- [ ] No "direct quote required" language: `grep -iE "must (use|include) .*(direct )?quote|quotation marks? required"` returns nothing
- [ ] No "0.33 / 1" or "0.67 / 1" style scores — all Q6-Q10 references use "X of 3"
- [ ] No "two sentences" / "Sentence 1 ... Sentence 2" on Q6-Q10 coaching
- [ ] No jargon abbreviations visible to students (BP1, TS, MCQ, CONC, bare SPO)
- [ ] Student's first name appears frequently; no third-person references

### Structural
- [ ] `<meta name="viewport">` present
- [ ] `discrim-challenge` appears on every fix card
- [ ] `print-btn` + `printChecklist(` both present
- [ ] `toggleCheck` present
- [ ] `tracking.js` script tag at end
- [ ] `reveal-wrapper` wraps every `.better` div
- [ ] `completion-overlay` + `confettiCanvas` present
- [ ] `data-title` on all 7 cards

### Design
- [ ] Card 1 opens with wise feedback (not deficit framing)
- [ ] Card 2 (Journey) shows growth areas if student is below 90%
- [ ] Every fix card has a pattern note connecting to longitudinal history
- [ ] Every fix card has a "So what?" box
- [ ] Checklist item #1 is PLAN FIRST
- [ ] Tier 2 practice includes Write a Paragraph from Prompt + Writing SPOs if paragraphs are a growth area
- [ ] Completion overlay has 3 concrete goals naming specific next-test actions

---

## 8. What NOT to do

Patterns from past violations the user has flagged:

- ❌ Shipping a "surface-level" card with sentence-fix content only, no journey integration or discrimination challenges
- ❌ Hardcoding prior test scores in the card — always fetch from writing-results CSV / Timeback API
- ❌ Telling a student their 82% score has "no weaknesses"
- ❌ Listing related weaknesses (e.g., Kernel Expansion + Essays) as separate bullets without naming the root-cause connection
- ❌ Using the word "teacher" anywhere in student-facing copy
- ❌ Prescribing two sentences on Q6–Q10 (the prompt asks for one)
- ❌ Framing Q6–Q10 partial credit as "0.67 / 1" (it's 2 of 3 points)
- ❌ Writing "Quote Sandwich" or telling students direct quotes are required
- ❌ Omitting the Print button, completion celebration, reveal interaction, or discrimination challenges
- ❌ Skipping the longitudinal analysis step and relying on prior card HTML alone
- ❌ Showing the Q1–Q10 score box as "9.5/10" (Q1–Q10 is worth 25 points on G3–G5, not 10)
- ❌ Telling students to "circle" or "underline" words on the test — the test is digital
- ❌ Prescribing margin-based planning ("jot the outline in the margin") — there is no margin in a text box
- ❌ Teaching Evidence Sandwich as just "quoted or paraphrased" without showing HOW to quote and paraphrase in a point-earning way (short exact phrase in quotation marks introduced with an attribution; paraphrase in own words keeping the specific fact)
- ❌ Telling students the test takes 60 minutes and they should use all 60 — it typically takes 30–40 minutes for students who do well. Frame pacing as "give the test the time it needs," not "use the full time limit"
- ❌ Using "Body 1 / Body 2" or "body sentence" for paragraph structure — the curriculum term is "Supporting Detail" (D1 / D2 in shorthand)
- ❌ Using real test passage content (Sports and Society, Pokemon/Tajiri, Anna + Sally the seal, Layla + geode, Garissa camel library, etc.) in pre-test prep cards — every example must be an invented, clearly-labeled practice passage
