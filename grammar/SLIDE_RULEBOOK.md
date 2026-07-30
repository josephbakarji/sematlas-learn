# Slide Generation Rulebook

Hard rules for ANY agent generating or editing LearnSlides decks. Load this file
before writing slide HTML. These rules come from Joseph's explicit feedback;
violating them means rework. The companion visual catalog is the Template Book
(`data/slides/template_book.html`, served at `/slides/template_book`); pattern
implementations live in `docs/SLIDE_TEMPLATES.md`.

## 1. Typography and punctuation

- **Font trio (brand)**: Newsreader (headings, serif), DM Sans (body), JetBrains Mono
  (code, labels, numeric readouts). Load from Google Fonts; set on `.reveal` and
  `h1/h2/h3`. Serif display over near-black is the LearnSlides look.
- **Equations never break across lines.** If a display equation wraps, use a more
  compact form (norms, matrix notation) or split into two display lines deliberately.
- **No em-dashes. Anywhere.** Not in prose, captions, box text, or code comments.
  Use commas, colons, periods, or parentheses.
- **No arrow symbols in prose.** No inline ⟺, ⇒, →, ↓ in sentences or titles.
  Write the words: "is the same as", "gives", "leads to", "maps to".
  Arrows are allowed ONLY (a) inside display math where standard, and
  (b) as drawn diagram elements (flow diagrams, D3 annotations).
- Minimal bold. Bold marks at most one phrase per box: the term being defined
  or the verdict. Never bold mid-sentence connectives.

## 2. Code slides

- **ASCII only in code, including comments.** No `∇`, `ᵀ`, `θ`, `≈`, `×`, `₀`,
  Unicode minus. A human must be able to type every character. Write
  `# grad J = X.T @ (X @ theta - y)`, not `# ∇J = Xᵀ(Xθ − y)`.
  This holds even when the Unicode version reads better.
- Step-through with `data-line-numbers="1-4|6-9|11-14"`. Max ~14 lines per block.
  Comments carry the narration; no comment restates its own line.

## 3. Pedagogical ordering (chronology)

- **Never show a term, acronym, or symbol before defining it.** If an
  interactive needs a quantity before its formal slide (e.g., an error readout
  before the cost function), define it in plain words on the spot, in the
  caption, at first use. Formalize later and connect back.
- Notation is introduced once, with anatomy labels (`\underbrace`) at first use.
- Every lecture ends by planting the question the next lecture answers.

## 4. Quizzes: ALWAYS the interactive MCQ system, never static slides

- **Do not write static MCQ `<section>`s in deck HTML.** Quiz slides must go
  through the questions pipeline so students can select answers, get graded
  feedback, and open the chat with the LLM:
  - Write `data/questions/<lecture_id>.json` with `type: "quiz_engine"`,
    `after_section: <horizontal index in the FINAL deck>`,
    `enable_chat: true`, `enable_generate: true`, and a `static_question`
    with `question`, `choices` (A-D), `correct`, `explanation`, `hint`.
  - Math in questions uses `$...$` delimiters.
  - The injector inserts the widget as its own slide after `after_section`.
- Question quality follows the question-evaluation framework (plausible
  distractors, explanation teaches, prediction/interpretation over recall).

## 5. Boxes and layout

- Pick box styles from the Template Book and use them by role (definition,
  key result, warning, aside), not by color whim. Max ~2 boxed elements per
  slide; if everything is in a box, nothing is.
- **Box titles sit ABOVE box content, never beside it.** Use the `.box-title`
  block header. (Reveal's theme makes bare `<ul>` inline-block; the shared CSS
  must force `ul { display: block }` inside boxes, or titles float beside
  bullet columns.)
- Asides and small remarks prefer the ruled-aside style (indent + vertical
  rule) over another box.

## 6. Charts (D3)

- One Dark palette from `static/css/tokens.css`. Series get distinct mark
  shapes plus direct labels; never yellow next to green as adjacent series
  (protan-indistinguishable). Yellow is a UI accent, not a data series.
- Fixed SVG `width`/`height` attributes (hidden slides have no layout).
- Axes always labeled with units. Legend for 2+ series.
- **Math is KaTeX everywhere, including plots and controls.** Axis labels are
  passed to `axes()` as TeX (`'\\theta_1'`, `'P(y{=}1)'`, `'\\text{size (cm)}'`)
  and rendered via the KaTeX overlay built into the helper; buttons, slider
  labels, and readouts with symbols use `\( ... \)` markup, never unicode
  approximations (φ, x², θ₁ as plain text are banned). Tick numbers stay SVG.
- Namespace pattern: one object per viz (`FIT`, `GD`), `init()` at boot,
  controls call methods via inline handlers. Class name `.viz-controls`
  (`.controls` belongs to Reveal).

## 7. Platform integration

- Reveal 6 CDN paths: plugins live at `dist/plugin/<name>.js` (flat), themes at
  `dist/plugin/highlight/monokai.css`.
- Deterministic decks: no `Math.random()` at module scope; precompute noise.
- Slide text must exist as text (not only inside images) so search and the
  chatbot can see it; Keynote-imported slides embed hidden `.kn-text`.
- **Verify through the served route** (`localhost:5050/slides/<id>`) with
  console-error capture, never only the raw file: the app serves the
  DB-assembled copy (re-imported automatically on file change via source hash).
- **Section attributes do not survive DB reassembly** (the assembler emits bare
  `<section>` tags): never anchor JS to a section id or rely on
  `data-auto-animate` in served decks; use `innerEl.closest('section')`.
- **ALWAYS draw networks, circuits, and computation graphs with
  `static/js/net-diagram.js` (the ND pattern).** Never hand-roll SVG text
  labels or ASCII diagrams for these. The grammar is fixed: LaTeX symbols as
  nodes, white ⊕ sum circles, orange σ activation circles, thin white arrows
  with yellow `w_ij` labels, bold `W_k` over edge bundles; build the diagram
  in stages bound to fragments (`stage`/`until` + `bindFragments`). Live
  reference: Template Book "ND" slide and intro_ml_10n slides 3-5, 8.
- After MCQ JSON changes, restart the app and verify the widget renders and is
  selectable on the served deck.

## 8. Story decks (the second deck mode)

Some lectures are stories, not labs: Joseph talking about something general
(models, thinking, taste). These use the **story-deck mode**, piloted by
`what_is_a_model.html`:

- Typography IS the design: Newsreader on near-black, one idea per slide,
  `.t-huge/.t-big/.t-line/.t-word/.kicker` scale, amber `.em` for the single
  emphasized phrase. No slide numbers, no progress bar, slow fades.
- **The script is the deck's soul**: full narration in each slide's
  `<aside class="notes">` (speaker view = teleprompter) plus a standalone
  `docs/scripts/<deck>_SCRIPT.md` with per-passage archive provenance.
- The words are JOSEPH'S: curated verbatim from memos and the archive
  (rag_search over BrainStorm + transcripts), stitched, never ventriloquized.
- At most 1-2 quiet simulations; restraint is the aesthetic.
- **Every section gets a named `id` anchor** and the deck is registered in
  `docs/REFERENCE_DECKS.md` so future lectures can deep-link
  (`/slides/<deck>#/<anchor>`, works in lightbox chips). Anchors survive the
  DB assembler as of parser v4.
- Pipeline: voice memo → archive sweep (verbatim passages + sources) →
  curated script → sparse deck → speaker-view walkthrough.

## 9. Voice

- Textbook prose in explanatory text: complete sentences, no bullet-point
  telegraphese outside actual lists (ml4science CLAUDE.md style).
- Captions under interactives say what to DO and what to NOTICE, one line each.
