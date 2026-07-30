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

## Status

Early. The grammar, seed decks, and adapter work end to end. Not yet built:
the atlas view (a navigable semantic map over all decks, from the SemAtlas
lineage this project is named for), the feedback protocol for shared decks,
and the capability ladder (small model drafts, larger model refines).
