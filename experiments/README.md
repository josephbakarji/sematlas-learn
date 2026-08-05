# The core experiment

Claim under test: the grammar lowers the intelligence bar enough that a small
local model can produce a usable interactive deck.

## Protocol

For a fixed topic and audience, generate a deck with models of increasing
size and score each deck on the same rubric. The adapter records timing and
token usage in `meta.json`; use `--suffix` to keep runs side by side:

    python3 adapter/generate.py "gradient descent" --model qwen2.5-coder:3b --suffix 3b
    python3 adapter/generate.py "gradient descent" --model qwen2.5-coder:14b --suffix 14b

## Rubric v2 (score each 0, 1, or 2)

1. Renders without errors, math typesets
2. Grammar compliance: correct classes, fragments, no em-dashes, ASCII code
3. Pedagogy: one idea per slide, symbols defined, honest assumptions
4. Interactivity: working quiz, sensible fragments
5. Taste: would you present this without embarrassment after light edits
6. Mathematical correctness: standard notation, no wrong terms or subscripts

A deck scoring 9 or more (of 12) is "usable with light edits." (Rubric v1
lacked item 6; v1 scores in the log are out of 10.) The interesting number
is the smallest model that reliably crosses that line, and how it moves as
the grammar improves. Log results below.

## Results log

| date | model | topic | sections | time | score | notes |
|---|---|---|---|---|---|---|
| 2026-08-05 | qwen2.5-coder:14b (9GB) ONE-SHOT | VAEs up to the ELBO | 14 | 80s | 11/12 | Honored the full 14-slide request. 7 equations, all essentially correct: E over q in the ELBO, loss = recon + beta KL with the right sign, elementwise reparam. 25 fragments, working quiz. The remaining point: derivation still stated rather than derived. Scale delivers, at 5x the size and 5x the one-shot latency of the 3b. |
| 2026-08-05 | LADDER v1: 3b draft + 14b verify | VAEs up to the ELBO | 8 | 146s | 6/12 | PREDICTION PARTLY WRONG, informatively. The 14b's findings were sensible, but two failure channels: (a) run-to-run draft variance, this 3b draft used odd E(x) notation from the start; (b) corrections routed THROUGH the 3b are lossy: redundant equations survived, final loss has a sign error (recon + KL with no negation). Fix for v2 is structural, not intellectual: apply the verifier's corrected equation MECHANICALLY (verbatim string replacement of the $$ block), keeping the LLM out of the fix path. Also: dedupe equations at outline level. |
| 2026-08-05 | 3b AGENTIC, lint only (agent.py --no-verify) | VAEs up to the ELBO | 8 | 64s | 10/12 | 20 calls, 11 lint issues auto-fixed. CORE MATH CORRECT: KL(q||p) right order, reparam trick present, ELBO with expectation over q (the one-shot's error, gone). One naming slip (calls the ELBO "VAE loss" unnegated). Compressed 12 requested to 8 and dropped the quiz (outline-level; quiz-append fix added after this run). Per-slide briefs are the win: asked for one specific equation at a time, the 3b writes the standard form. |
| 2026-08-05 | 3b AGENTIC + 3b self-verify | VAEs up to the ELBO | 10 | 121s | 5/12 | NEGATIVE RESULT, the important kind: the 3b verifier hallucinated a systematic "missing subscript" rule; the fix loop propagated nonstandard z_x notation deck-wide, lost the reparam equation, swapped KL argument order. A 3b cannot review a 3b: it invents conventions instead of finding errors. The capability ladder (stronger verifier than drafter) is a REQUIREMENT, not an optimization. Also caught and fixed a harness bug: outline equations passed through json.dumps leaked double-escaped LaTeX into drafts; lint now catches double escapes. |
| 2026-08-02 | qwen2.5-coder:3b (1.9GB) | VAEs up to the ELBO | 9 | 17s | 7/10* | Narrative arc PERFECT (primer, probabilistic latent, KL + reparam, ELBO, architecture, loss, quiz). Copy-resistant quiz fix worked: wrote its own on-topic question. But: only 2 display equations where the topic needs ~8; "derivation" states rather than derives; one REAL math error (E over p(z|x) instead of q(z|x) in the first ELBO, correct in the second); instruction leakage ("Define every symbol:" as slide text); compressed 14 requested slides to 9; kept correct=B from the structure example (position bias). *Rubric v1 has no mathematical-correctness item; on deep-math topics that is the binding constraint. Proposal: rubric v2 adds item 6 (math correctness 0-2), making this run 8/12. Conclusion: 3b crosses the grammar bar, not the correctness bar; this is the data that justifies the capability ladder (small drafts, larger verifies). |
| 2026-07-30 | qwen2.5-coder:3b (1.9GB) | gradient descent | 9 | 14.5s | 7/10 | Run 1 failed framing (md headings, no sections): fixed with a prompt nudge plus adapter salvage mode. Run 2 clean: renders 2/2, grammar 2/2, pedagogy 1/2 (generic content, eta defined inline), interactivity 1/2 (working quiz but it parroted the example question from the system prompt; some choices in plain text not KaTeX), taste 1/2. Grammar TODO: replace the quiz example with a copy-resistant one; reinforce the define-every-symbol rule. |
