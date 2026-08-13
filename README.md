# SemAtlas Learn

An open framework for interactive teaching decks, designed so that a model you
run yourself can help you write them.

Slides are plain HTML files in a stable grammar. You can read them in any
browser, keep them private, or share them anywhere. No accounts, no server,
no build step. A language model, local or hosted, authors decks inside the
grammar; the framework carries the taste so the model does not have to.

## Quickstart

    ./serve.sh                    # opens http://localhost:8899

Browse the seed decks. Then generate one of your own against any
OpenAI-compatible endpoint (Ollama shown; LM Studio and hosted APIs work the
same way):

    ollama pull qwen2.5-coder:3b
    python3 adapter/generate.py "the central limit theorem" --model qwen2.5-coder:3b

The new deck lands in `decks/<topic>/index.html`, self-contained except for
the shared `framework/` folder.

## Layout

    framework/   vendored Reveal 6, KaTeX with fonts, D3; sal.css design
                 system; quiz.js (static MCQ), net-diagram.js, sal.js boot
    grammar/     the rules a model follows: SLIDE_RULEBOOK.md,
                 SLIDE_TEMPLATES.md, system_prompt.md, skeleton.html
    adapter/     generate.py, a stdlib-only CLI for any chat endpoint
    decks/       one folder per deck; each is shareable as-is
    experiments/ the measurement protocol for the core design bet

## The design bet

The framework's quality is measured by how small a model can produce a good
deck with it. Rulebook as system prompt, templates as vocabulary, skeleton as
boilerplate the model never writes: each piece shrinks the authoring task from
"invent an interactive lecture" toward "fill a constrained template." The
scaffolding converts intelligence into structure once, so it does not have to
be re-spent per deck. See `experiments/README.md` for how we measure this.

## Principles

Read `VISION.md` for the full picture. In short: open project, open models,
your data, your machine. Creation is private and local; sharing is a separate
social layer, added later. Design for the relationship between the person and
the model, not for maximal intelligence.

## Relationship to LearnSlides (the official deployment)

This open framework and the LearnSlides app are siblings with distinct jobs:

- **This repo** (GitHub Pages): the open framework. Grammar, adapter,
  experiments, and generated decks. Static, serverless, forkable. Also the
  testing ground: new decks and grammar changes land here first.
- **LearnSlides** (learn.sematlas.com, hosted on Render): the official
  course deployment. Accounts, live quizzes with results, slide-aware chat,
  the author's courses. Decks graduate there once they are ready for
  students.

Coordination rules:

1. The grammar (SLIDE_RULEBOOK.md, SLIDE_TEMPLATES.md) is canonical HERE in
   `grammar/`. LearnSlides carries mirrors, refreshed by its
   `scripts/sync_grammar.sh`.
2. Decks convert between the two formats with `scripts/deck_paths.py`
   (`to-learnslides` / `from-learnslides`): the only difference is where
   shared assets live.
3. learn.sematlas.com belongs to the LearnSlides app. This repo's public
   home is its GitHub Pages URL.

## Status

Early. The grammar, seed decks, and adapter work end to end. Not yet built:
the atlas view (a navigable semantic map over all decks, from the SemAtlas
lineage this project is named for), the feedback protocol for shared decks,
and the capability ladder (small model drafts, larger model refines).
