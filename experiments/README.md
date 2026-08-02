# The core experiment

Claim under test: the grammar lowers the intelligence bar enough that a small
local model can produce a usable interactive deck.

## Protocol

For a fixed topic and audience, generate a deck with models of increasing
size and score each deck on the same rubric. The adapter records timing and
token usage in `meta.json`; use `--suffix` to keep runs side by side:

    python3 adapter/generate.py "gradient descent" --model qwen2.5-coder:3b --suffix 3b
    python3 adapter/generate.py "gradient descent" --model qwen2.5-coder:14b --suffix 14b

## Rubric (score each 0, 1, or 2)

1. Renders without errors, math typesets
2. Grammar compliance: correct classes, fragments, no em-dashes, ASCII code
3. Pedagogy: one idea per slide, symbols defined, honest assumptions
4. Interactivity: working quiz, sensible fragments
5. Taste: would you present this without embarrassment after light edits

A deck scoring 7 or more is "usable with light edits." The interesting number
is the smallest model that reliably crosses that line, and how it moves as
the grammar improves. Log results below.

## Results log

| date | model | topic | sections | time | score | notes |
|---|---|---|---|---|---|---|
| 2026-08-02 | qwen2.5-coder:3b (1.9GB) | VAEs up to the ELBO | 9 | 17s | 7/10* | Narrative arc PERFECT (primer, probabilistic latent, KL + reparam, ELBO, architecture, loss, quiz). Copy-resistant quiz fix worked: wrote its own on-topic question. But: only 2 display equations where the topic needs ~8; "derivation" states rather than derives; one REAL math error (E over p(z|x) instead of q(z|x) in the first ELBO, correct in the second); instruction leakage ("Define every symbol:" as slide text); compressed 14 requested slides to 9; kept correct=B from the structure example (position bias). *Rubric v1 has no mathematical-correctness item; on deep-math topics that is the binding constraint. Proposal: rubric v2 adds item 6 (math correctness 0-2), making this run 8/12. Conclusion: 3b crosses the grammar bar, not the correctness bar; this is the data that justifies the capability ladder (small drafts, larger verifies). |
| 2026-07-30 | qwen2.5-coder:3b (1.9GB) | gradient descent | 9 | 14.5s | 7/10 | Run 1 failed framing (md headings, no sections): fixed with a prompt nudge plus adapter salvage mode. Run 2 clean: renders 2/2, grammar 2/2, pedagogy 1/2 (generic content, eta defined inline), interactivity 1/2 (working quiz but it parroted the example question from the system prompt; some choices in plain text not KaTeX), taste 1/2. Grammar TODO: replace the quiz example with a copy-resistant one; reinforce the define-every-symbol rule. |
