# Map and territory: SemAtlas and Learn as one project

Draft, 2026-10-02. Written by the LearnSlides session after the Federalist deck, for Joseph
and the SemAtlas session. Nothing here is decided until Joseph says so.

## The split

- **SemAtlas is the map.** Where knowledge sits and how it connects: question-first
  navigation over a linked graph (sematlas.com, `/q`), open source since 2026-10-01 (MIT),
  visitors pay for their own questions through OpenRouter.
- **Learn is the territory.** Places you walk through to understand one thing: story
  decks, one question each, on real data, with widgets you act on, quizzes and a tutor.
- **The bridge is the concept graph.** Every slide already has a stable address
  (`/slides/<deck>#/<slide-id>`) and tags saying which concepts it defines, uses,
  previews, and where a concept breaks (`data-defines`, `data-uses`, `data-previews`,
  `data-limits`; built by LearnSlides `services/concept_graph.py`). Exported in an open
  format, the map can send a reader to the slide that teaches a node, and a deck can
  show where it sits on the map.

## What changed our mind about how decks are made

The Federalist deck (Oct 1) was written from scratch around one question, with one
dataset and one notation table fixed before any slide. Next to the transferred
generative-learning deck it was clearer, less crowded and consistent, because the
inconsistencies of a transfer (notation from three sources, widgets ahead of their
definitions, patches on patches) never had a chance to appear. So:

**A story deck is one question, answered on real data, with a spine and a notation
table written before the first slide.** The old material is a coverage checklist, never
a layout.

## Designing at scale

1. **An open deck format.** A deck is a folder: `deck.html` in the grammar of
   `grammar/`, `story.yaml` (the question, the spine, the notation table, the concepts,
   the datasets with sources and licences), `data/`, and `verify.py`, which recomputes
   every number the slides quote. The Federalist deck becomes the reference example.
2. **A deck factory.** The steps done by hand for the Federalist and GNN decks become a
   repeatable workflow: question; find and verify real data; spine and notation;
   widgets on the shared kit; quizzes and a tutor; checks (overflow screenshots,
   `verify.py`, links, concept tags); human review. Many decks can then be drafted,
   compared and iterated.
3. **Style as a design system with a taste log.** The shared kit (`deck-kit.css/js`)
   carries the look; style decisions are recorded with before and after, and Joseph's
   verdicts on drafts are logged, so the style is refined deliberately across all decks
   at once.
4. **Open contribution.** Code under MIT; decks and data under CC BY-SA, like the
   Wikipedia text SemAtlas already builds on. A contribution is a pull request with a
   deck folder; continuous checks run `verify.py`, the deck checks and the screenshots.
5. **Beyond the courses.** Decks are questions anyone might ask ("Who wrote the
   Federalist Papers?", "Why does a forecast fail after ten days?"), so each deck is
   also a node on the map, of type question, linked to the concepts it teaches.

## Who runs what

- **sematlas-learn (public):** the open format, the grammar, the kit, the reference
  decks, the factory, the contribution checks. Static, readable anywhere (GitHub Pages).
- **LearnSlides (learn.sematlas.com):** the course runtime, with sign-in, quizzes,
  tutor conversations, grading and student data. Student data never leaves it; decks
  move between the two with `scripts/deck_paths.py`.
- **SemAtlas (sematlas.com):** the map, the question explorer, and the payment path
  (bring your own OpenRouter key), which the tutor could share.

## The interface between map and territory (to agree with the SemAtlas session)

- `concepts.json`: concept id, title, short definition, prerequisite edges, and for each
  concept the slides that define, use, preview and limit it, as stable URLs.
- `decks.json`: per deck, its question, concepts, datasets and part structure.
- SemAtlas reads both and draws them as a layer on the map; a deck links out to
  `sematlas.com/q?concept=<id>` (or whatever address the map prefers).

## First steps, small and reversible

1. Port the Federalist deck into this repo as the reference story deck, with
   `story.yaml` and `verify.py`.
2. Export the concept graph and deck index from LearnSlides as the two JSON files above.
3. Agree the interface with the SemAtlas session; it draws one layer from the files.
4. Write the factory as a skill and run it on two or three new questions, to see
   whether quality holds when decks are many.

## Open decisions for Joseph

- Is sematlas-learn the open home, with LearnSlides staying the private course runtime?
- Licences: MIT for code and CC BY-SA for decks and data?
- How much of the semester's time goes here, and how much to the remaining course decks?
