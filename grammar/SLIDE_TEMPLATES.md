# Slide Templates & Nativization Learnings

Working notes from rebuilding Keynote decks as native Reveal 6 decks.
Living exemplar: `data/slides/intro_ml_04n.html` (linear regression). Read it
alongside this doc — every pattern below has a working instance there.

## Reveal 6 gotchas (learned the hard way)

1. **Plugin paths changed.** 4.x: `plugin/highlight/highlight.js`. 6.x (Vite build):
   `dist/plugin/highlight.js`, themes at `dist/plugin/highlight/monokai.css`.
   Blind-sedding the CDN version on 4.5.0 decks WILL break every deck that loads a
   plugin — the migration needs the path rewrite too.
2. **`.controls` is Reveal's class** (navigation arrows) and its CSS wins. Never
   name your own elements `.controls` / `.progress` / `.backgrounds` / `.overlay`.
   House convention: `.viz-controls`.
3. **KaTeX scripts are `defer`red** — `renderMathInElement` may not exist at
   Reveal `ready`. Boot pattern: try at ready, fall back to `window` `load`.
4. `scrollActivationWidth: 600` gives phones the scroll view for free.

## D3-in-slides patterns that work

- **Fixed SVG dimensions** (`width="700" height="350"` attributes), never
  `clientWidth`: hidden slides have zero layout, so measuring forces re-init
  hacks on `slidechanged`. Fixed sizes render correctly before the slide is
  ever shown, and Reveal scales the whole slide anyway.
- **One namespace object per viz** (`FIT`, `GD`, `LAND`, `MC`) with `init()` +
  `render()`; all `init()`s run once at boot. Controls call `NS.method()` via
  inline `onclick`/`oninput` — survives the LearnSlides injector.
- **Deterministic data**: precomputed noise offsets, no `Math.random()` at
  module level — the deck renders identically every load (and screenshots are
  reproducible). Random is fine *inside* user-triggered actions (SGD steps).
- **Animations**: `setInterval` stored on the namespace; stop it on
  `slidechanged` when leaving the slide.
- **Analytic ground truth in JS**: closed-form least squares (`lsq()`) powers
  the "best fit" button, the contour ★, and convergence checks — one source of
  truth for every viz.
- **Contours**: `d3.contours()` on a 72×56 grid + `d3.geoTransform` to map grid
  coords into the axis scales. Thresholds geometric (`Jmin + 1.6^k`) so rings
  hug the minimum.

## Template catalog (section-level, copy from intro_ml_04n.html)

| Template | Instance in exemplar | Notes |
|---|---|---|
| Title | §1 | uppercase course kicker, two-line title, subtitle |
| Data-table concept | §2 "Data" | real numbers, `.hl` column for target, fragment bullets |
| Two-box concept | §3 "Inputs and Outputs" | paired highlight/principle boxes + eq-box right |
| Equation | §6 "Linear Hypothesis" | eq-box center, green variant for the punchline form |
| Interactive fit | §7 | sliders + literal squared-error squares + best-fit button |
| Linked dual-view | §9 "Loss Landscape" | drag on contour ↔ line view; the conceptual heart |
| Derivation (vertical stack) | §10 gradient descent | idea slide above, hand-derivation below |
| Algorithm stepper | §11 "Watch It Learn" | step/play/reset, α slider, divergence, SGD toggle |
| Intuition-viz + fragments | §10 GD idea | left column of fragment boxes, right a small steppable viz (1D bowl) |
| Code step-through | §12 | `data-line-numbers="1-4\|6-9\|11-14"`, ≤14 lines, comments carry the narration |
| MCQ | §13, §17 | options plain, answer+teach in fragment principle-box |
| Comparison (vertical) | §15 GD vs NE | two boxes + reconciliation box fragment |
| Provocation | §17 "Why not interpolate all points?" | one centered question + fragment tease of next lecture |
| Summary | §19 | 2×2 boxes: model / objective / solvers / knob |

## Template Book variants (source: data/slides/template_book.html, served at /slides/template_book)

- Typography: Newsreader headings / DM Sans body / JetBrains Mono labels+code (Google Fonts).
- Boxes: **A** soft left border (legacy default) · **B** tab-on-hairline-border · **C** header-bar
  card · **D** ruled aside (remarks) · **E** corner brackets. Semantic accents: blue=definition,
  green=key idea, red=warning, yellow=action.
- Key results: **K1** framed+tab+glow · **K2** filled block (red/blue, dark-Keynote style). Max one per slide.
- Comparisons: **C-pair** header-bar cards · **T-row** bare table.
- Code: **CS1** (default) centered monokai card: width 88%, `font-size: 0.64em`, drop
  shadow, line numbers, `data-line-numbers="|a-b|c"` step-through (the revealjs.com demo
  look: the block is a distinct centered card with big type, never a full-width strip) ·
  **CS2** `data-auto-animate` + shared `data-id` on consecutive sections so the block
  morphs as code grows · **CS3** titled card with filename chip header · **CS4** terminal
  (prompt + output, no line numbers).
- Others: **DL** definition rows · **EA** equation anatomy · **P** provocation.

## NetDiagram: math-first network diagrams (static/js/net-diagram.js)

Joseph's Keynote network grammar, reproduced: LaTeX symbols ARE the nodes (no circles
around inputs), white ⊕ circles sum, orange σ circles activate, thin white arrows carry
yellow w_ij labels, bold W_k labels over edge bundles. KaTeX renders into an HTML overlay
synced to SVG coordinates (NOT foreignObject: Safari blurs those under Reveal scaling).
Spec: nodes / edges / labels with `stage` (fade in at fragment k) and `until` (fade out:
lets a σ node splice into an existing wire). `bindFragments(sectionEl)` drives stages from
the section's fragments. Working instances: intro_ml_10n slides 2-4 and 6 (linear predictor
drawn, two outputs make a matrix, σ splice, full network + composition strip). Reuse for
L11 computation graphs.

**Platform limits learned building it** (now in the rulebook):
- Local `/static/js` script tags used to be DROPPED by the DB parser (fixed, PARSER_VERSION 3).
- `<section>` attributes (id, data-auto-animate) do NOT survive DB reassembly: anchor JS via
  `document.getElementById(innerId).closest('section')`, and expect auto-animate (CS2) to
  work only in raw decks until the assembler preserves section attributes.
- `const X = ...` at script top level does not create `window.X`; export explicitly.

## Stolen from the dark Keynote decks (design language worth keeping)

- **x → h → y flow diagram** (colored blocks, function name on the arrow) for any
  input/output mapping slide.
- **Equation anatomy**: `\underbrace{...}_{\text{unknown parameters}}` labels under
  the symbols — one line that teaches the notation.
- **1D bowl before the 2D landscape**: teach descent on J(θⱼ) with "initial guess"
  and arrow steps before showing contours.
- **`while not converged:` pseudocode framing** for iterative update rules.
- **Multiple model-class buttons** (linear / polynomial / k-NN) on the same data —
  plants the generalization question two lectures early.

## Keynote → native decision rule (per slide)

- **Bullets / text / tables** → native HTML (styleable, searchable, chat-visible).
- **Algorithmic figures** (anything a loop can draw) → D3 interactive; it beats
  N static build stages every time.
- **Hand-drawn, photos, cinematic motion** → keep Keynote, import via
  `keynote2reveal.py` sections (mixed decks are the end state).

## Palette (see `static/css/tokens.css`)

One Dark on near-black `#0d1017`. Chart-series constraint (validated with the
dataviz six-checks): don't rely on yellow↔green adjacency (protan ΔE 3.3);
give series distinct mark shapes and direct labels, keep yellow for UI accents.
