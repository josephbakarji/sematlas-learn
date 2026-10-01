"""Recompute every headline number the slides quote, from the data in this folder.
Exit status 1 if any of them no longer holds."""
import csv, math, sys, random
rows = list(csv.DictReader(open('data/federalist_function_words.csv')))
W = list(rows[0].keys())[3:]
P = [dict(num=int(r['paper']), a=r['author'], n=int(r['words']), c=[int(r[w]) for w in W]) for r in rows]
known = [p for p in P if p['a'] in ('Hamilton', 'Madison')]
disputed = [p for p in P if p['a'] == 'disputed']
fails = []
def check(name, got, want):
    ok = got == want
    print(f"{'ok ' if ok else 'FAIL'} {name}: {got}" + ('' if ok else f'  (slides say {want})'))
    if not ok: fails.append(name)

def fit(train, alpha=1):
    phi = {}
    for a in ('Hamilton', 'Madison'):
        c = [sum(p['c'][k] for p in train if p['a'] == a) + alpha for k in range(len(W))]
        s = sum(c); phi[a] = [v / s for v in c]
    return phi, sum(p['a'] == 'Madison' for p in train) / len(train)
def log_odds(p, phi, prior):
    return math.log(prior / (1 - prior)) + sum(c * (math.log(phi['Madison'][k]) - math.log(phi['Hamilton'][k])) for k, c in enumerate(p['c']))
rate = lambda p, w: 1000 * p['c'][W.index(w)] / p['n']
mean = lambda ps, w: sum(rate(p, w) for p in ps) / len(ps)

check('papers by author', {a: sum(p['a'] == a for p in P) for a in ('Hamilton', 'Madison', 'disputed', 'Jay', 'joint')},
      {'Hamilton': 51, 'Madison': 14, 'disputed': 12, 'Jay': 5, 'joint': 3})
H = [p for p in P if p['a'] == 'Hamilton']; M = [p for p in P if p['a'] == 'Madison']
check('upon per 1,000 (H, M, disputed)', [round(mean(g, 'upon'), 2) for g in (H, M, disputed)], [3.30, 0.16, 0.16])
check('Madison papers without upon', sum(p['c'][W.index('upon')] == 0 for p in M), 11)
check('Hamilton function words, upon', (sum(sum(p['c']) for p in H), sum(p['c'][W.index('upon')] for p in H)), (57905, 372))
loo = sum((log_odds(p, *fit([q for q in known if q is not p])) > 0) == (p['a'] == 'Madison') for p in known)
check('Naive Bayes leave-one-out', loo, 65)
phi, prior = fit(known)
lo = {p['num']: round(log_odds(p, phi, prior), 1) for p in disputed}
check('disputed to Madison', sum(v > 0 for v in lo.values()), 11)
check('No. 55 log odds', lo[55], -2.9)
sys.exit(1 if fails else 0)
