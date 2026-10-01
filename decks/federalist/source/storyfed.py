"""generative_federalist: generative learning (Naive Bayes, GDA, generative against
discriminative) told as one story on one dataset, written from scratch (Oct 1, 2026).
Who wrote the twelve disputed Federalist Papers? Page head from intro_ml_10n."""
import html, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.expanduser('~/Documents/00-projects/04-web-apps/learnslides-wt-flag')
SRC = open(f'{REPO}/data/slides/intro_ml_10n.html').read()
HEAD = SRC[:SRC.index('<div class="slides">')].replace('<title>Introduction to Neural Networks</title>', '<title>Who Wrote the Federalist Papers?</title>')
HEAD = HEAD.replace('</style>', '''    .excerpt { font-family: 'Newsreader', Georgia, serif; font-size: 0.95em; line-height: 1.5; color: #e6ebf5; border-left: 3px solid var(--accent-yellow); padding: 0.2em 0 0.2em 0.8em; min-height: 6.2em; }
    .notation td { padding: 0.18em 0.6em; vertical-align: top; }
    .verdict th, .verdict td { padding: 0.2em 0.45em; text-align: center; font-family: 'JetBrains Mono', monospace; }
    select.pick { background: #161b26; color: #e6ebf5; border: 1px solid #4a5261; border-radius: 6px; font-size: 0.6em; padding: 3px 6px; }
</style>''', 1)
code = lambda f: html.escape(open(os.path.join(HERE, f)).read().strip('\n'))
NQ = 5
part = lambda n, name, q: f'''<section id="part-{n}" class="centered part-divider" data-part="{n}" data-part-name="{name}" data-part-question="{q}">
    <p class="part-eyebrow">Part {n} of {NQ}</p>
    <h1 class="part-title">{name}</h1>
    <p class="part-q">{q}</p>
    <nav class="part-map"></nav>
</section>'''
WORDS = ['upon', 'on', 'by', 'there', 'to', 'also', 'an', 'of']
opts = lambda sel: ''.join(f'<option{" selected" if w == sel else ""}>{w}</option>' for w in WORDS)

S = [r'''<section id="start" class="centered">
    <p class="tiny-text muted" style="letter-spacing: 2px; text-transform: uppercase;">Generative learning</p>
    <h1 style="margin-top: 0.3em;">Who Wrote the Federalist Papers?</h1>
    <p class="small-text" style="max-width: 860px; margin: 0.6em auto 0;">Naive Bayes, Gaussian discriminant analysis, and why a model of how the data was made can learn from very little of it.</p>
</section>''',
r'''<section id="roadmap" data-part="1" data-part-name="The mystery" data-part-question="Who wrote the twelve disputed papers?">
    <h2>Five questions for today</h2>
    <ol class="road"></ol>
</section>''',
r'''<section id="publius" data-previews="generative-model">
    <h2>Eighty-five essays, one pen name<span class="sub">New York, 1787 and 1788: arguing for the new Constitution, signed "Publius"</span></h2>
    <div class="two-column" style="gap: 30px; align-items: flex-start;">
        <div style="flex: 1;">
            <table class="data-table small-text" style="width: 100%;">
                <tr><td style="text-align: left; color: var(--accent-blue);">Alexander Hamilton</td><td>51</td></tr>
                <tr><td style="text-align: left; color: var(--accent-orange);">James Madison</td><td>14</td></tr>
                <tr><td style="text-align: left;">John Jay</td><td>5</td></tr>
                <tr><td style="text-align: left;">Hamilton and Madison together</td><td>3</td></tr>
                <tr><td style="text-align: left;"><b>Claimed by both</b></td><td><b>12</b></td></tr>
            </table>
        </div>
        <div style="flex: 1.2;">
            <p class="small-text">Days before his fatal duel in 1804, Hamilton left a list of his papers that claimed the twelve. Madison later said they were his. Historians argued for 160 years.</p>
            <p class="small-text fragment">In 1963, Frederick Mosteller and David Wallace settled it with counting and Bayes' rule. Today we redo their work, and it is the whole of generative learning.</p>
        </div>
    </div>
</section>''',
r'''<section id="guess">
    <h2>Can you tell them apart?<span class="sub">The opening of a paper by Hamilton or by Madison. Guess.</span></h2>
    <p id="guess-text" class="excerpt"></p>
    <div class="viz-controls" id="guess-btns" style="justify-content: flex-start; gap: 12px;"><button class="btn" data-a="Hamilton">Hamilton</button><button class="btn" data-a="Madison">Madison</button></div>
    <p class="small-text" id="guess-out"></p>
    <p class="small-text fragment">Both write long, careful, eighteenth-century sentences about the same constitution. Topic gives little away, and neither does style, read by eye.</p>
</section>''',
r'''<section id="small-words" data-uses="feature">
    <h2>The clue is in the small words<span class="sub">One dot per paper: how often it uses the word, per 1,000 words</span></h2>
    <svg id="viz-marks" width="700" height="300"></svg>
    <div class="viz-controls" id="marks-words" style="justify-content: flex-start;">''' + ''.join(f'<button class="btn" data-w="{w}">{w}</button>' for w in ['upon', 'on', 'by', 'there', 'also', 'of']) + r'''</div>
    <p class="small-text" id="marks-out"></p>
    <p class="small-text fragment">Words like "upon" and "by" carry no topic, so a writer uses them out of habit. That makes them a fingerprint. Mosteller and Wallace used 70 of them; so do we.</p>
</section>''',
part(2, 'Each author is a die', 'How would each of them write a paper?'),
r'''<section id="story" data-defines="generative-model" data-uses="bernoulli">
    <h2>A story of how a paper gets written<span class="sub">A generative model: a recipe that could have produced the data</span></h2>
    <div class="two-column" style="gap: 30px; align-items: flex-start;">
        <div style="flex: 1.1;">
            <p class="small-text"><b>1.</b> Pick the author: Madison with probability \(\phi_y\), Hamilton otherwise.</p>
            <p class="small-text"><b>2.</b> Each author owns a 70-sided die, one face per function word. Roll that author's die once for every function word in the paper.</p>
            <p class="small-text fragment">That is the whole model. It ignores word order and meaning, which is naive, and it is enough.</p>
        </div>
        <div class="box-b" style="flex: 1;"><span class="tab">Notation, used all lecture</span>
            <table class="notation small-text">
                <tr><td>\(y\)</td><td>the author: 1 for Madison, 0 for Hamilton</td></tr>
                <tr><td>\(k\)</td><td>one of the 70 function words</td></tr>
                <tr><td>\(x_t\)</td><td>the \(t\)-th function word of a paper, \(t = 1, \dots, L\)</td></tr>
                <tr><td>\(\phi_y\)</td><td>\(P(y = 1)\): how likely a paper is Madison's</td></tr>
                <tr><td>\(\phi_{k \mid y}\)</td><td>\(P(x_t = k \mid y)\): the face \(k\) of author \(y\)'s die</td></tr>
            </table>
        </div>
    </div>
</section>''',
r'''<section id="dice" data-uses="generative-model">
    <h2>The two dice, learned from 65 papers<span class="sub">Each face's probability is a count divided by a total</span></h2>
    <svg id="viz-dice" width="700" height="330"></svg>
    <div class="viz-controls" id="dice-btns" style="justify-content: flex-start;"><button class="btn" data-a="Hamilton" style="color: var(--accent-blue);">Roll Hamilton's die</button><button class="btn" data-a="Madison" style="color: var(--accent-orange);">Roll Madison's die</button></div>
    <p class="small-text" id="dice-out"></p>
</section>''',
r'''<section id="dice-fit" data-layer="deep" data-uses="maximum-likelihood">
    <h2>Why counting is the best estimate<span class="sub">Maximum likelihood for one die</span></h2>
    <div class="two-column" style="gap: 34px; align-items: flex-start;">
        <div style="flex: 1;">
            <p class="small-text">Hamilton's papers contain \(N\) function words, \(n_k\) of them word \(k\). The probability his die gives to all of them is</p>
            <div class="eq-box" style="font-size: 0.8em;">\( L(\phi) = \prod_{k=1}^{70} \phi_{k \mid 0}^{\,n_k}, \qquad \sum_k \phi_{k \mid 0} = 1 \)</div>
            <p class="small-text">Take the log, \( \sum_k n_k \log \phi_{k \mid 0} \), and maximize it while the faces sum to one (a Lagrange multiplier):</p>
            <div class="eq-box" style="font-size: 0.8em;">\( \phi_{k \mid 0} = \dfrac{n_k}{N} \)</div>
        </div>
        <div class="box-b green" style="flex: 1;"><span class="tab">In words</span>
            <p class="small-text">The best die is the one whose faces match how often he actually used each word. Training is counting.</p>
            <p class="small-text">For \(\phi_y\), the same argument gives the share of training papers that are Madison's: \( 14 / 65 \).</p>
            <p class="small-text">The coin of the <a href="/slides/intro_ml_07n">maximum likelihood lecture</a>, with 70 faces instead of two.</p>
        </div>
    </div>
</section>''',
part(3, 'Run the story backwards', 'Given a paper, which die rolled it?'),
r'''<section id="bayes" data-uses="bayes-rule naive-bayes-assumption" data-defines="naive-bayes">
    <h2>Bayes' rule turns the story around</h2>
    <div class="eq-box" style="font-size: 0.86em;">\( \log \dfrac{P(y = 1 \mid x)}{P(y = 0 \mid x)} \;=\; \log \dfrac{\phi_y}{1 - \phi_y} \;+\; \sum_{t=1}^{L} \log \dfrac{\phi_{x_t \mid 1}}{\phi_{x_t \mid 0}} \)</div>
    <div class="two-column" style="gap: 26px; margin-top: 0.6em;">
        <div class="box-b small-text" style="flex: 1;"><span class="tab">Read it as a vote</span>Start from the prior. Every function word in the paper adds its own vote: positive if Madison's die favours it, negative if Hamilton's does. Above zero, Madison.</div>
        <div class="box-b green small-text" style="flex: 1;"><span class="tab">Why a sum</span>The model rolls the die independently for each word, so the probability of the paper is a product, and its log is a sum. The derivation is the next deep dive.</div>
    </div>
</section>''',
r'''<section id="bayes-deep" data-layer="deep" data-uses="bayes-rule naive-bayes-assumption logistic-regression">
    <h2>From Bayes' rule to a sum of votes</h2>
    <p class="small-text"><b>1.</b> Bayes for each author: \( P(y \mid x) = P(x \mid y)\, P(y) / P(x) \).</p>
    <p class="small-text"><b>2.</b> Divide Madison by Hamilton: \(P(x)\) cancels.</p>
    <div class="eq-box" style="font-size: 0.78em;">\( \dfrac{P(y = 1 \mid x)}{P(y = 0 \mid x)} = \dfrac{\phi_y}{1 - \phi_y} \cdot \dfrac{P(x \mid y = 1)}{P(x \mid y = 0)} \)</div>
    <p class="small-text"><b>3.</b> The die is rolled independently: \( P(x \mid y) = \prod_{t=1}^{L} \phi_{x_t \mid y} \). This is the naive assumption.</p>
    <p class="small-text"><b>4.</b> Take the log: products become sums, one vote per word.</p>
    <p class="small-text"><b>5.</b> Back to a probability: \( P(y = 1 \mid x) = 1 / (1 + e^{-\text{log odds}}) \), the sigmoid. A word used \(c\) times votes \(c\) times, so the log odds is linear in the word counts: Naive Bayes draws the same kind of boundary as logistic regression.</p>
</section>''',
r'''<section id="weigh" data-uses="naive-bayes bayes-rule">
    <h2>Weigh a paper<span class="sub">The twelve largest votes, and the verdict. Pick any paper.</span></h2>
    <div class="two-column" style="gap: 22px; align-items: flex-start;">
        <div style="flex: 0 0 610px;"><svg id="viz-weigh" width="610" height="370"></svg></div>
        <div style="flex: 1;">
            <p><select class="pick" id="weigh-paper"></select></p>
            <p class="small-text" id="weigh-out"></p>
            <p class="small-text fragment">"upon" can only vote for Hamilton: Madison used it in 3 of his 14 papers. Ten of the twelve disputed papers never use it; No. 50 uses it once, No. 54 twice.</p>
        </div>
    </div>
</section>''',
r'''<section id="never-seen" data-defines="laplace-smoothing" data-uses="naive-bayes maximum-likelihood" data-limits="maximum-likelihood">
    <h2>The word a die has never rolled<span class="sub">Train on only three papers per author, and a zero appears</span></h2>
    <div class="viz-controls" id="smooth-alpha" style="justify-content: flex-start;"><span class="ix">smoothing \(\alpha\)</span><button class="btn" data-a="0">0: plain counting</button><button class="btn" data-a="0.1">0.1</button><button class="btn" data-a="1">1: Laplace</button></div>
    <p class="small-text" id="smooth-out" style="min-height: 4.4em;"></p>
    <div class="eq-box fragment" style="font-size: 0.8em;">\( \phi_{k \mid y} = \dfrac{n_{k \mid y} + \alpha}{N_y + 70\,\alpha} \)</div>
    <p class="small-text fragment">\(n_{k \mid y}\): how often author \(y\) used word \(k\) in training; \(N_y\): all their function words. Adding \(\alpha\) pretend sightings of every face turns "never seen, so impossible" into "never seen, so rare".</p>
</section>''',
r'''<section id="verdict" data-uses="naive-bayes">
    <h2>The verdict on the twelve<span class="sub">Trained on all 65 known papers, with \(\alpha = 1\). Positive: Madison.</span></h2>
    <table class="verdict data-table small-text" id="verdict-table" style="margin: 0.6em auto;"></table>
    <div class="two-column" style="gap: 26px; margin-top: 0.6em;">
        <div class="box-b small-text" style="flex: 1;"><span class="tab">Checked first</span>Leaving each of the 65 known papers out in turn and predicting it, the model is right every time.</div>
        <div class="box-b yellow small-text" style="flex: 1;"><span class="tab">The hard one</span>No. 55 leans Hamilton here. Mosteller and Wallace also found it the weakest case: still Madison, but at odds of only a few hundred to one, far weaker than for the others. A model that hesitates where historians hesitate is telling you something true.</div>
    </div>
</section>''',
part(4, 'Two numbers instead of seventy', 'What if the features are continuous?'),
r'''<section id="gda" data-defines="gda" data-uses="multivariate-gaussian generative-model">
    <h2>Gaussian discriminant analysis<span class="sub">Each paper as two rates. Each author as a cloud: a 2D Gaussian.</span></h2>
    <div class="two-column" style="gap: 20px; align-items: flex-start;">
        <div style="flex: 0 0 620px;"><svg id="viz-gda" width="620" height="420"></svg></div>
        <div style="flex: 1;">
            <p class="small-text">across <select class="pick" id="gda-x">''' + opts('upon') + r'''</select> &nbsp; up <select class="pick" id="gda-y">''' + opts('by') + r'''</select></p>
            <div class="viz-controls" style="justify-content: flex-start;"><button class="btn" id="gda-shared">one shared \(\Sigma\)</button><button class="btn" id="gda-sep">one \(\Sigma\) per author</button></div>
            <div class="eq-box" style="font-size: 0.66em; text-align: left;">\( y \sim \text{Bernoulli}(\phi_y) \)<br>\( r \mid y \sim \mathcal{N}(\mu_y, \Sigma) \)</div>
            <p class="tiny-text">\(r\): the paper's two rates, per 1,000 words. \(\mu_y\): author \(y\)'s average. \(\Sigma\): the spread. Fitting is averaging, the continuous version of counting.</p>
            <p class="small-text" id="gda-out"></p>
        </div>
    </div>
</section>''',
r'''<section id="gda-breaks" data-uses="gda multivariate-gaussian" data-limits="gda">
    <h2>Where the Gaussian is wrong<span class="sub">A model that is wrong about the data, and still right about the author</span></h2>
    <div class="two-column" style="gap: 24px; align-items: flex-start;">
        <div style="flex: 0 0 560px;"><svg id="viz-breaks" width="560" height="300"></svg></div>
        <div style="flex: 1;">
            <p class="small-text" id="breaks-out"></p>
            <p class="small-text fragment">GDA still separates the authors, because the two clouds are far apart. A generative model makes a strong claim about how the data was made; when the claim is wrong, its probabilities are off even when its decisions are right. Pick "on" against "by" on the last slide: closer to Gaussian, and the clouds overlap more.</p>
        </div>
    </div>
</section>''',
r'''<section id="gda-deep" data-layer="deep" data-uses="gda logistic-regression multivariate-gaussian">
    <h2>A shared \(\Sigma\) gives a straight boundary</h2>
    <p class="small-text">The log odds is the difference of two Gaussian log densities plus the prior:</p>
    <div class="eq-box" style="font-size: 0.74em;">\( \log \dfrac{P(y = 1 \mid r)}{P(y = 0 \mid r)} = -\tfrac{1}{2}(r - \mu_1)^\top \Sigma^{-1} (r - \mu_1) + \tfrac{1}{2}(r - \mu_0)^\top \Sigma^{-1} (r - \mu_0) + \log \dfrac{\phi_y}{1 - \phi_y} \)</div>
    <p class="small-text">Expand: the \( r^\top \Sigma^{-1} r \) terms are the same for both authors and cancel. What is left is linear in \(r\):</p>
    <div class="eq-box" style="font-size: 0.74em;">\( \log \dfrac{P(y = 1 \mid r)}{P(y = 0 \mid r)} = \theta^\top r + \theta_0, \qquad \theta = \Sigma^{-1} (\mu_1 - \mu_0) \)</div>
    <p class="small-text">So \( P(y = 1 \mid r) = \sigma(\theta^\top r + \theta_0) \): exactly the form of logistic regression. With one \(\Sigma\) per author the quadratic terms stay, and the boundary curves.</p>
</section>''',
part(5, 'Generative or discriminative?', 'Which learns faster from few examples?'),
r'''<section id="two-kinds" data-defines="discriminative-model" data-uses="generative-model logistic-regression">
    <h2>Two ways to learn the same boundary</h2>
    <div class="two-column" style="gap: 26px; margin-top: 0.4em;">
        <div class="box-b green" style="flex: 1;"><span class="tab">Generative: Naive Bayes, GDA</span>
            <p class="small-text">Model how each author writes, \(P(x \mid y)\) and \(P(y)\), then flip it with Bayes' rule. Strong assumptions. Fitting is counting and averaging.</p></div>
        <div class="box-b purple" style="flex: 1;"><span class="tab">Discriminative: logistic regression</span>
            <p class="small-text">Model only the answer, \(P(y \mid x)\), and fit the boundary directly by gradient descent. Weaker assumptions. Never says how a paper is written.</p></div>
    </div>
    <p class="small-text fragment" style="margin-top: 0.8em;">Both end in a sigmoid of a linear score. The question is which finds a good one from less data.</p>
</section>''',
r'''<section id="curve" data-uses="generative-model discriminative-model generalization">
    <h2>Learning from a handful of papers<span class="sub">Train on a few papers per author, test on all the other known ones; 60 random draws per point</span></h2>
    <div class="two-column" style="gap: 22px; align-items: flex-start;">
        <div style="flex: 0 0 600px;"><svg id="viz-curve" width="600" height="340"></svg>
            <div class="viz-controls" style="justify-content: flex-start;"><button class="btn" id="curve-run">Run the experiment</button></div></div>
        <div style="flex: 1;">
            <p class="small-text" id="curve-out"></p>
            <p class="small-text fragment">With very few papers, the model that assumes more learns faster: its assumptions fill in what the data cannot. With enough data the discriminative model catches up, and where the assumptions are wrong it eventually wins. Ng and Jordan (2002) proved this trade-off.</p>
        </div>
    </div>
</section>''',
r'''<section id="code-nb" data-layer="code" data-uses="naive-bayes laplace-smoothing">
    <h2>Mosteller and Wallace in twenty lines<span class="sub">Naive Bayes from scratch, on the same counts. Press Run.</span></h2>
    <pre data-runnable data-packages="numpy pandas" data-files="/static/data/datasets/federalist_function_words.csv" style="font-size: 0.56em; width: 96%;"><code class="language-python" data-trim>
''' + code('code_nb.py') + r'''
    </code></pre>
    <p class="tiny-text">You should see a leave-one-out accuracy of 1.0, and eleven positive log odds: every disputed paper but No. 55 goes to Madison.</p>
</section>''',
r'''<section id="takeaways">
    <h2>What to take away</h2>
    <ol class="small-text" style="line-height: 1.6;">
        <li>A generative model is a story of how the data was made: here, each author rolls a die of function words.</li>
        <li>Fitting it is counting (or averaging): maximum likelihood gives the observed frequencies. Smoothing keeps an unseen word from vetoing everything.</li>
        <li>Classifying is running the story backwards with Bayes' rule; the log odds is a sum of one vote per word.</li>
        <li>GDA does the same with Gaussian clouds; with a shared covariance its boundary is exactly a logistic regression.</li>
        <li>Strong assumptions learn fast from little data, and are wrong in ways you should check. On the twelve disputed papers, 65 known ones were enough to agree with Mosteller and Wallace.</li>
    </ol>
</section>''',
]
body = '\n\n'.join(S)
PARTS = re.findall(r'<section id="(part-\d|roadmap)"[^>]*data-part="(\d)" data-part-name="([^"]+)" data-part-question="([^"]+)"', body)
assert len(PARTS) == NQ, PARTS
body = body.replace('<ol class="road"></ol>', '<ol class="road">' + ''.join(
    f'<li><a href="#/{pid}"><span class="rn">{n}</span><span class="rt">{name}</span><span class="rq">{q}</span></a></li>' for pid, n, name, q in PARTS) + '</ol>', 1)
TAIL = r'''
</div>
</div>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@6/dist/reveal.js"></script>
<script src="https://cdn.jsdelivr.net/npm/reveal.js@6/dist/plugin/highlight.js"></script>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script src="/static/js/deck-kit.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script>
''' + open(os.path.join(HERE, 'fed.js')).read() + r'''
Reveal.initialize({ width: 1280, height: 720, center: false, hash: true, slideNumber: true, transition: 'fade', transitionSpeed: 'fast', scrollActivationWidth: 600, plugins: [RevealHighlight] });
Reveal.on('ready', () => {
    const rm = () => renderMathInElement(document.body, { delimiters: [{ left: '$$', right: '$$', display: true }, { left: '\\[', right: '\\]', display: true }, { left: '\\(', right: '\\)', display: false }] });
    if (window.renderMathInElement) { rm(); FED.init(); } else window.addEventListener('load', () => { rm(); FED.init(); });
});
</script>
</body>
</html>
'''
out = HEAD + '<div class="slides">\n\n' + body + '\n' + TAIL
open(f'{REPO}/data/slides/generative_federalist.html', 'w').write(out)
print('built', out.count('<section'), 'sections')
