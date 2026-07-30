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
