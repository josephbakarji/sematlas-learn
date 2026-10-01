"""Build decks.json, the index SemAtlas reads, from every decks/*/story.yaml.

The index is generated, never edited by hand, so it cannot drift from the decks.
Each spine anchor must exist as a slide id in the deck's index.html, or the build
fails: the map must never link into nothing. Concept keys are the kebab-case keys of
learn.sematlas.com's concepts.json; a key the course does not have yet is kept (the
SemAtlas bridge matches it to Wikipedia) and reported. Renaming a key breaks links
from the map: record a rename in moves.yaml instead (old key: new key).

    python3 scripts/build_index.py            # writes decks.json
"""
import json, re, sys, pathlib, urllib.request
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://josephbakarji.github.io/sematlas-learn/decks/'
COURSE = 'https://learn.sematlas.com/static/data/concepts.json'

def course_keys():
    try:
        with urllib.request.urlopen(COURSE, timeout=10) as r:
            return set(json.load(r)['concepts'])
    except Exception as e:
        print(f'(could not read the course concepts, {e}; keys not checked)')
        return None

def main():
    known, decks, errors = course_keys(), [], []
    for story in sorted(ROOT.glob('decks/*/story.yaml')):
        d, s = story.parent, yaml.safe_load(story.read_text())
        ids = set(re.findall(r'<section id="([^"]+)"', (d / 'index.html').read_text()))
        for part in s.get('spine', []):
            if part.get('anchor') and part['anchor'] not in ids:
                errors.append(f'{d.name}: spine anchor "{part["anchor"]}" is not a slide id')
        if known is not None:
            new = [k for k in s.get('teaches', []) + s.get('needs', []) if k not in known]
            if new:
                print(f'{d.name}: keys the course does not have yet (kept): {", ".join(new)}')
        decks.append({
            'id': d.name, 'question': s['question'], 'answer': s.get('answer', ''),
            'url': BASE + d.name + '/',
            'teaches': s.get('teaches', []), 'needs': s.get('needs', []),
            'spine': [{k: p[k] for k in ('part', 'question', 'anchor') if k in p} for p in s.get('spine', [])],
            'data': [{k: x.get(k, '') for k in ('what', 'source', 'licence')} for x in s.get('data', [])],
            'licence': s.get('licence', {}),
        })
    if errors:
        print('\n'.join(errors)); sys.exit(1)
    moves = ROOT / 'moves.yaml'
    out = {'version': 1, 'decks': decks, 'moves': yaml.safe_load(moves.read_text()) if moves.exists() else {}}
    (ROOT / 'decks.json').write_text(json.dumps(out, indent=1, ensure_ascii=False) + '\n')
    print(f'decks.json: {len(decks)} deck(s)')

if __name__ == '__main__':
    main()
