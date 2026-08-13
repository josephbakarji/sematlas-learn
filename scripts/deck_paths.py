#!/usr/bin/env python3
"""
Convert a deck between SemAtlas Learn (vendored paths) and LearnSlides
(CDN paths) formats, so decks flow both ways:

    # graduate a SAL deck into the LearnSlides app (official deployment)
    python3 scripts/deck_paths.py to-learnslides decks/vae-14b/index.html \
        ~/Documents/00-projects/04-web-apps/learnslides/data/slides/vae.html

    # bring a LearnSlides deck into SAL (open, static, shareable)
    python3 scripts/deck_paths.py from-learnslides \
        ~/Documents/00-projects/04-web-apps/learnslides/data/slides/intro_ml_04n.html \
        decks/linear-regression/index.html

The two formats differ only in where shared assets live. Content is
untouched: a deck is a deck.
"""
import re
import sys
from pathlib import Path

V = '../../framework/vendor'
PAIRS = [
    ('https://cdn.jsdelivr.net/npm/reveal.js@6/dist/reset.css', f'{V}/reset.css'),
    ('https://cdn.jsdelivr.net/npm/reveal.js@6/dist/reveal.css', f'{V}/reveal.css'),
    ('https://cdn.jsdelivr.net/npm/reveal.js@6/dist/theme/night.css', f'{V}/night.css'),
    ('https://cdn.jsdelivr.net/npm/reveal.js@6/dist/plugin/highlight/monokai.css', f'{V}/monokai.css'),
    ('https://cdn.jsdelivr.net/npm/reveal.js@6/dist/plugin/highlight.js', f'{V}/highlight.js'),
    ('https://cdn.jsdelivr.net/npm/reveal.js@6/dist/reveal.js', f'{V}/reveal.js'),
    ('https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css', f'{V}/katex/katex.min.css'),
    ('https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js', f'{V}/katex/katex.min.js'),
    ('https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js', f'{V}/katex/contrib/auto-render.min.js'),
    ('https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js', f'{V}/d3.min.js'),
    ('/static/js/net-diagram.js', '../../framework/js/net-diagram.js'),
]
GOOGLE_FONTS = ('<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600;6..72,700'
                '&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700'
                '&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">')


def from_learnslides(s):
    for cdn, local in PAIRS:
        s = s.replace(cdn, local)
    s = re.sub(r'<link rel="preconnect"[^>]*>\s*', '', s)
    s = re.sub(r'<link href="https://fonts\.googleapis\.com[^"]*"[^>]*>',
               f'<link rel="stylesheet" href="{V}/fonts/fonts.css">', s)
    return s


def to_learnslides(s):
    for cdn, local in PAIRS:
        s = s.replace(local, cdn)
    s = s.replace(f'<link rel="stylesheet" href="{V}/fonts/fonts.css">', GOOGLE_FONTS)
    # sal.css has no CDN twin; inline a pointer comment so the deck still
    # renders in learnslides (its own theme covers the shared classes)
    s = s.replace('<link rel="stylesheet" href="../../framework/css/sal.css">',
                  '<!-- sal.css classes: ensure learnslides theme includes the SAL design system -->')
    s = s.replace('<script src="../../framework/js/quiz.js"></script>',
                  '<!-- quiz: learnslides uses its own quiz pipeline (data/questions/<id>.json) -->')
    s = s.replace('<script src="../../framework/js/sal.js"></script>\n<script>SAL.init();</script>',
                  '<!-- boot: learnslides assembler injects its own Reveal.initialize -->')
    return s


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ('to-learnslides', 'from-learnslides'):
        sys.exit(__doc__)
    mode, src, dst = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    s = src.read_text()
    out = to_learnslides(s) if mode == 'to-learnslides' else from_learnslides(s)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out)
    leftover = re.findall(r'\.\./\.\./framework/[^"\')\s]+', out) if mode == 'to-learnslides' else \
               re.findall(r'https://cdn\.jsdelivr[^"\')\s]+', out)
    print(f'wrote {dst}')
    if leftover:
        print('note, unconverted refs remain:', *leftover[:5], sep='\n  ')


if __name__ == '__main__':
    main()
