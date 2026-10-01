"""Snapshot the course's concept graph for the graph lab (graph.json).

Reads the concept tree straight from a LearnSlides checkout (services/concept_graph.py:
concepts from the slides' data-defines/data-uses tags, prerequisite edges), the
Wikipedia article SemAtlas matched to each concept (sematlas.com/learn/bridge.json),
and the story decks of this repo (decks.json) as question nodes.

    python3 lab/concept-graph/build.py [path to learnslides checkout]
"""
import json, sys, pathlib, urllib.request
HERE = pathlib.Path(__file__).resolve().parent
LS = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '~/Documents/00-projects/04-web-apps/learnslides-wt-flag').expanduser()
sys.path.insert(0, str(LS))
import os; os.chdir(LS)
from services import concept_graph  # noqa: E402

g = concept_graph.build()
try:
    bridge = json.load(urllib.request.urlopen('https://www.sematlas.com/learn/bridge.json', timeout=15))['concepts']
except Exception as e:
    print('no bridge:', e); bridge = {}
decks_used = [d for d in g['order'] if any(c['deck'] == d for c in g['concepts'].values())]
deck = {d: {'id': d, 'title': g['titles'].get(d, d), 'i': i, 'course': next(c['course'] for c in g['concepts'].values() if c['deck'] == d)}
        for i, d in enumerate(decks_used)}
nodes = []
for k, c in g['concepts'].items():
    b = bridge.get(k, {})
    nodes.append({'id': k, 'name': k.replace('-', ' '), 'slide': c['title'], 'deck': c['deck'],
                  'url': 'https://learn.sematlas.com' + c['url'], 'course': c['course'],
                  'uses': len(c['used_on']) + len(c['previewed_on']),
                  'quizzes': len(c['resources']['quizzes']), 'limits': len(c['resources']['limits']),
                  'wiki': b.get('wiki')})
edges = [{'source': a, 'target': b} for a, b in g['edges']]
stories = json.load(open(HERE.parent.parent / 'decks.json'))['decks']
keys = {n['id'] for n in nodes}
questions = [{'id': 'q:' + s['id'], 'question': s['question'], 'url': s['url'],
              'teaches': [k for k in s['teaches'] if k in keys], 'needs': [k for k in s['needs'] if k in keys]} for s in stories]
out = {'decks': list(deck.values()), 'nodes': nodes, 'edges': edges, 'questions': questions}
(HERE / 'graph.json').write_text(json.dumps(out, ensure_ascii=False))
print(len(deck), 'decks', len(nodes), 'concepts', len(edges), 'edges', len(questions), 'question nodes',
      sum(1 for n in nodes if n['wiki']), 'with a Wikipedia article')
