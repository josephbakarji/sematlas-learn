import numpy as np, pandas as pd

d = pd.read_csv('federalist_function_words.csv')
words = d.columns[3:]                                   # the 70 function words
known = d[d.author.isin(['Hamilton', 'Madison'])]

def fit(train, alpha=1):
    phi = {}
    for a in ['Hamilton', 'Madison']:
        c = train[train.author == a][words].sum() + alpha    # how often a wrote each word, plus alpha
        phi[a] = c / c.sum()                                  # the author's die
    return phi, (train.author == 'Madison').mean()

def log_odds(paper, phi, prior):                        # above 0 means Madison
    return np.log(prior / (1 - prior)) + (paper[words] * np.log(phi['Madison'] / phi['Hamilton'])).sum()

hits = 0
for i, p in known.iterrows():                           # leave one paper out, predict it
    phi, prior = fit(known.drop(i))
    hits += (log_odds(p, phi, prior) > 0) == (p.author == 'Madison')
print('leave-one-out accuracy:', round(hits / len(known), 3))

phi, prior = fit(known)
for _, p in d[d.author == 'disputed'].iterrows():
    print(f'No. {p.paper}: log odds for Madison {log_odds(p, phi, prior):+.1f}')
