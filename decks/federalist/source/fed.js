
// ===================== Who wrote the Federalist Papers? (deck kit: DK) =====================
// 85 essays of 1787 and 1788, signed Publius. Data: how often each paper uses each of the
// 70 function words of Mosteller and Wallace (1964), counted from Project Gutenberg #1404.
// Every number on the slides is computed here, in the browser, from that file.
const FED = { H: 'Hamilton', M: 'Madison' };
const P = DK.PAL, CH = P.blue, CM = P.orange, CD = P.ink;   // Hamilton, Madison, disputed
FED.col = a => (a === 'Hamilton' ? CH : a === 'Madison' ? CM : CD);
FED.t = function (sel, tex, x, y, o = {}) {
    const size = o.size || 15, w = o.w || 90, h = Math.round(size * 2.4);
    const fo = sel.append('foreignObject').attr('x', x - w / 2).attr('y', y - h / 2).attr('width', w).attr('height', h).style('pointer-events', 'none');
    const div = fo.append('xhtml:div').style('color', o.color || P.ink).style('font-size', size + 'px').style('height', h + 'px')
        .style('display', 'flex').style('align-items', 'center').style('justify-content', 'center').style('white-space', 'nowrap');
    try { katex.render(tex, div.node(), { throwOnError: false }); } catch (e) { div.text(tex); }
};

FED.load = () => FED.data || (FED.data = Promise.all([
    d3.csv('/static/data/datasets/federalist_function_words.csv'),
    d3.json('/static/data/datasets/federalist_excerpts.json'),
]).then(([rows, ex]) => {
    const words = rows.columns.slice(3);
    const papers = rows.map(r => ({ num: +r.paper, author: r.author, n: +r.words, c: words.map(w => +r[w]), ex: ex[r.paper] }));
    papers.forEach(p => { p.L = d3.sum(p.c); p.rate = w => 1000 * p.c[words.indexOf(w)] / p.n; });
    const known = papers.filter(p => p.author === 'Hamilton' || p.author === 'Madison');
    return { words, papers, known, disputed: papers.filter(p => p.author === 'disputed') };
}));

// ---- Naive Bayes: each author is a die over the 70 function words
FED.fit = function (train, words, alpha = 1) {
    const die = a => { const c = words.map((_, k) => d3.sum(train.filter(p => p.author === a), p => p.c[k]) + alpha), s = d3.sum(c); return { count: c, phi: c.map(v => v / s), total: s - alpha * words.length }; };
    const H = die('Hamilton'), M = die('Madison'), nM = train.filter(p => p.author === 'Madison').length;
    return { H, M, prior: nM / train.length, nM, nH: train.length - nM };
};
// log odds for Madison, and each word's share of it (count times log ratio); NaN when 0/0
FED.score = function (m, p) {
    const parts = p.c.map((c, k) => {
        if (!c) return 0;
        const a = m.M.phi[k], b = m.H.phi[k];
        if (a === 0 && b === 0) return NaN;
        return c * (Math.log(a) - Math.log(b));
    });
    const prior = Math.log(m.prior / (1 - m.prior));
    return { prior, parts, total: prior + parts.reduce((s, v) => s + v, 0) };
};
FED.post = s => (isNaN(s) ? NaN : 1 / (1 + Math.exp(-s)));
FED.fmtP = p => (isNaN(p) ? 'no answer' : p > 0.9999 ? '> 99.99%' : p < 0.0001 ? '< 0.01%' : DK.pct(p, 1));

// ---------- 1. guess the author of an unsigned excerpt
FED.guess = function (D) {
    const box = document.getElementById('guess-text'); if (!box) return;
    const out = document.getElementById('guess-out'), r = DK.rng(7), pool = D.known.slice();
    let cur, right = 0, tries = 0;
    const next = () => { cur = pool[Math.floor(r() * pool.length)]; box.textContent = '"' + cur.ex + ' ..."'; out.innerHTML = 'Hamilton or Madison?'; };
    document.querySelectorAll('#guess-btns .btn').forEach(b => b.addEventListener('click', () => {
        if (!cur) return;
        tries++; const ok = b.dataset.a === cur.author; right += ok;
        out.innerHTML = `${ok ? '<b style="color:' + P.green + ';">Right.</b>' : '<b style="color:' + P.red + ';">No.</b>'} No. ${cur.num} is by <b style="color:${FED.col(cur.author)};">${cur.author}</b>. You: ${right} of ${tries}.`;
        cur = null; setTimeout(next, 1600);
    }));
    next();
};

// ---------- 2. the small words: one dot per paper, rate per 1,000 words
FED.marks = function (D) {
    const svg = d3.select('#viz-marks'); if (svg.empty()) return;
    const out = document.getElementById('marks-out');
    const draw = w => {
        document.querySelectorAll('#marks-words .btn').forEach(b => b.classList.toggle('active', b.dataset.w === w));
        svg.selectAll('*').remove();
        const max = Math.max(2, d3.max(D.papers, p => p.rate(w)));
        const s = DK.axes(svg, 700, 300, { l: 120, r: 20, t: 10, b: 46 }, [0, max * 1.05], [0, 3], `\\text{"${w}" per 1,000 words}`, null);
        svg.selectAll('g.axis').filter((d, i) => i === 1).remove();
        const rows = [['Hamilton', 2.4], ['Madison', 1.5], ['disputed', 0.6]], r = DK.rng(3);
        rows.forEach(([a, yy]) => {
            svg.append('text').attr('x', 110).attr('y', s.y(yy) + 5).attr('text-anchor', 'end').attr('fill', FED.col(a)).attr('font-size', 16).text(a);
            const ps = D.papers.filter(p => p.author === a);
            ps.forEach(p => svg.append('circle').attr('cx', s.x(p.rate(w))).attr('cy', s.y(yy) + (r() - 0.5) * 34).attr('r', 5).attr('fill', FED.col(a)).attr('fill-opacity', a === 'disputed' ? 0 : 0.75).attr('stroke', FED.col(a)).attr('stroke-width', 1.5));
            const m = d3.mean(ps, p => p.rate(w));
            svg.append('line').attr('x1', s.x(m)).attr('x2', s.x(m)).attr('y1', s.y(yy) - 24).attr('y2', s.y(yy) + 24).attr('stroke', FED.col(a)).attr('stroke-width', 3);
        });
        const mean = a => d3.mean(D.papers.filter(p => p.author === a), p => p.rate(w));
        out.innerHTML = `Average per 1,000 words: Hamilton <b style="color:${CH};">${DK.num(mean('Hamilton'), 2)}</b>, Madison <b style="color:${CM};">${DK.num(mean('Madison'), 2)}</b>, the disputed twelve <b>${DK.num(mean('disputed'), 2)}</b>.`;
    };
    document.querySelectorAll('#marks-words .btn').forEach(b => b.addEventListener('click', () => draw(b.dataset.w)));
    draw('upon');
};

// ---------- 3. each author is a die: the faces, and a paper written by rolling it
FED.dice = function (D) {
    const svg = d3.select('#viz-dice'); if (svg.empty()) return;
    const m = FED.fit(D.known, D.words), out = document.getElementById('dice-out');
    const top = d3.range(D.words.length).sort((a, b) => (m.H.phi[b] + m.M.phi[b]) - (m.H.phi[a] + m.M.phi[a])).slice(0, 16);
    const show = ['upon', 'on', 'by', 'there', 'also'].map(w => D.words.indexOf(w)).filter(k => !top.includes(k));
    const ks = top.concat(show);
    const x = d3.scaleBand().domain(ks).range([60, 690]).padding(0.25), y = d3.scaleLinear().domain([0, 0.2]).range([270, 20]);
    svg.append('g').attr('class', 'axis').attr('transform', 'translate(60,0)').call(d3.axisLeft(y).ticks(4));
    ks.forEach(k => {
        [['H', CH, 0], ['M', CM, 1]].forEach(([a, c, j]) => svg.append('rect').attr('x', x(k) + j * x.bandwidth() / 2).attr('width', x.bandwidth() / 2)
            .attr('y', y(m[a].phi[k])).attr('height', 270 - y(m[a].phi[k])).attr('fill', c));
        svg.append('text').attr('transform', `translate(${x(k) + x.bandwidth() / 2},${280}) rotate(-50)`).attr('text-anchor', 'end').attr('fill', show.includes(k) ? P.yellow : P.inkMuted).attr('font-size', 13).text(D.words[k]);
    });
    FED.t(svg, '\\phi_{k \\mid y}', 110, 14, { size: 15, color: P.inkMuted });
    const r = DK.rng(11);
    const roll = a => {
        const phi = m[a === 'Hamilton' ? 'H' : 'M'].phi, seq = [];
        for (let t = 0; t < 30; t++) { let u = r(), k = 0; while (u > phi[k] && k < phi.length - 1) { u -= phi[k]; k++; } seq.push(D.words[k]); }
        out.innerHTML = `<b style="color:${FED.col(a)};">${a}'s die</b>, rolled 30 times: ` + seq.map(w => (w === 'upon' || w === 'on' || w === 'by') ? `<b style="color:${P.yellow};">${w}</b>` : w).join(' ')
            + '. Nonsense as English, but with his rates of "upon", "on" and "by". That is all the model knows about him.';
    };
    document.querySelectorAll('#dice-btns .btn').forEach(b => b.addEventListener('click', () => roll(b.dataset.a)));
    out.textContent = 'Roll a die to write a paper the way the model thinks each author writes.';
};

// ---------- 4. weigh one paper: every word's vote, the prior, the verdict
FED.weigh = function (D) {
    const svg = d3.select('#viz-weigh'); if (svg.empty()) return;
    const sel = document.getElementById('weigh-paper'), out = document.getElementById('weigh-out');
    D.papers.filter(p => p.author !== 'Jay' && p.author !== 'joint').forEach(p => { const o = document.createElement('option'); o.value = p.num; o.textContent = `No. ${p.num}  (${p.author})`; sel.appendChild(o); });
    sel.value = '51';
    const draw = () => {
        const p = D.papers.find(q => q.num === +sel.value);
        const train = D.known.filter(q => q !== p);   // a known paper is never in its own training set
        const m = FED.fit(train, D.words), S = FED.score(m, p);
        const items = S.parts.map((v, k) => ({ w: D.words[k], v, c: p.c[k] })).filter(d => d.c).sort((a, b) => Math.abs(b.v) - Math.abs(a.v)).slice(0, 12);
        svg.selectAll('*').remove();
        const lim = Math.max(3, d3.max(items, d => Math.abs(d.v)), Math.abs(S.prior));
        const x = d3.scaleLinear().domain([-lim, lim]).range([150, 560]);
        svg.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 18).attr('y2', 360).attr('stroke', P.grid);
        svg.append('text').attr('x', x(-lim)).attr('y', 12).attr('fill', CH).attr('font-size', 13).text('points to Hamilton');
        svg.append('text').attr('x', x(lim)).attr('y', 12).attr('text-anchor', 'end').attr('fill', CM).attr('font-size', 13).text('points to Madison');
        [{ w: 'prior', v: S.prior, c: null }, ...items].forEach((d, i) => {
            const yy = 24 + i * 26;
            svg.append('text').attr('x', 140).attr('y', yy + 16).attr('text-anchor', 'end').attr('fill', P.ink).attr('font-size', 15).attr('font-family', d.c === null ? 'DM Sans' : 'JetBrains Mono').text(d.c === null ? 'before reading' : `${d.w} ×${d.c}`);
            svg.append('rect').attr('x', Math.min(x(0), x(d.v))).attr('width', Math.abs(x(d.v) - x(0))).attr('y', yy + 3).attr('height', 18).attr('rx', 3).attr('fill', d.v > 0 ? CM : CH).attr('opacity', d.c === null ? 0.5 : 0.9);
            svg.append('text').attr('x', 600).attr('y', yy + 16).attr('text-anchor', 'end').attr('fill', P.inkMuted).attr('font-size', 13).text(DK.num(d.v, 2));
        });
        const post = FED.post(S.total), who = S.total > 0 ? 'Madison' : 'Hamilton';
        out.innerHTML = `No. ${p.num}: log odds <b>${DK.num(S.total, 1)}</b>, so P(Madison | paper) = <b style="color:${FED.col(who)};">${FED.fmtP(post)}</b>: <b style="color:${FED.col(who)};">${who}</b>.`
            + (p.author === 'disputed' ? '' : ` It was written by ${p.author}, and left out of training here.`)
            + (p.num === 55 ? ' The weakest of the twelve: Mosteller and Wallace also found No. 55 the hardest case, still Madison but with far less certainty than the others.' : '');
    };
    sel.addEventListener('change', draw); draw();
};

// ---------- 5. never seen: train on three papers each, with and without smoothing
FED.smooth = function (D) {
    const out = document.getElementById('smooth-out'); if (!out) return;
    const r = DK.rng(4), pick = (a, n) => { const ps = D.known.filter(p => p.author === a).slice(); for (let i = ps.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [ps[i], ps[j]] = [ps[j], ps[i]]; } return ps.slice(0, n); };
    const train = pick('Hamilton', 3).concat(pick('Madison', 3)), test = D.known.filter(p => !train.includes(p));
    const draw = a => {
        document.querySelectorAll('#smooth-alpha .btn').forEach(b => b.classList.toggle('active', +b.dataset.a === a));
        const m = FED.fit(train, D.words, a);
        const unseen = D.words.filter((w, k) => !m.H.count[k] || !m.M.count[k]);
        let right = 0, none = 0, vetoed = 0;
        test.forEach(p => { const S = FED.score(m, p); if (isNaN(S.total)) none++; else { if (!isFinite(S.total)) vetoed++; right += (S.total > 0) === (p.author === 'Madison'); } });
        const dm = D.disputed.filter(p => FED.score(m, p).total > 0).length;
        out.innerHTML = `Trained on papers ${train.map(p => p.num).join(', ')} only. `
            + (a === 0 ? `<b>${unseen.length} words</b> never appear for one of the authors (${unseen.slice(0, 6).join(', ')}...), so their \\(\\phi\\) is exactly 0. Of the ${test.length} other known papers, <b style="color:${P.red};">${none} get no answer at all</b> (0 against 0). Of the other ${test.length - none}, ${vetoed} are decided by a single word one author never used, whatever the rest of the paper says; ${right} come out right.`
                : `With \\(\\alpha = ${a}\\), no \\(\\phi\\) is zero. Of the ${test.length} other known papers, <b style="color:${P.green};">${right} come out right</b> (${DK.pct(right / test.length, 0)}), and ${dm} of the 12 disputed go to Madison.`);
        DK.math(out);
    };
    document.querySelectorAll('#smooth-alpha .btn').forEach(b => b.addEventListener('click', () => draw(+b.dataset.a)));
    draw(0);
};

// ---------- 6. the verdict on the twelve
FED.verdict = function (D) {
    const tb = document.getElementById('verdict-table'); if (!tb) return;
    const m = FED.fit(D.known, D.words);
    tb.innerHTML = '<tr><th>paper</th>' + D.disputed.map(p => `<th>${p.num}</th>`).join('') + '</tr><tr><td>log odds</td>'
        + D.disputed.map(p => { const s = FED.score(m, p).total; return `<td style="color:${s > 0 ? CM : CH};">${DK.num(s, 1)}</td>`; }).join('') + '</tr>';
};

// ---------- 7. GDA: two words, one Gaussian per author
FED.gauss = function (pts) {
    const n = pts.length, mx = d3.mean(pts, p => p[0]), my = d3.mean(pts, p => p[1]);
    let a = 0, b = 0, c = 0; pts.forEach(p => { const u = p[0] - mx, v = p[1] - my; a += u * u; b += u * v; c += v * v; });
    return { mu: [mx, my], S: [[a / n, b / n], [b / n, c / n]], n };
};
FED.logN = (x, mu, S) => { const det = S[0][0] * S[1][1] - S[0][1] ** 2, u = x[0] - mu[0], v = x[1] - mu[1];
    const q = (S[1][1] * u * u - 2 * S[0][1] * u * v + S[0][0] * v * v) / det; return -0.5 * q - 0.5 * Math.log(det) - Math.log(2 * Math.PI); };
FED.gda = function (D) {
    const svg = d3.select('#viz-gda'); if (svg.empty()) return;
    const out = document.getElementById('gda-out'), sx = document.getElementById('gda-x'), sy = document.getElementById('gda-y');
    let shared = true;
    const fit = (train, wx, wy) => {
        const pt = p => [p.rate(wx), p.rate(wy)];
        const G = { H: FED.gauss(train.filter(p => p.author === 'Hamilton').map(pt)), M: FED.gauss(train.filter(p => p.author === 'Madison').map(pt)) };
        if (shared) { const n = G.H.n + G.M.n, S = [0, 1].map(i => [0, 1].map(j => (G.H.n * G.H.S[i][j] + G.M.n * G.M.S[i][j]) / n)); G.H.S = S; G.M.S = S; }
        const lp = Math.log(G.M.n / G.H.n);
        return { G, pt, lo: p => FED.logN(pt(p), G.M.mu, G.M.S) - FED.logN(pt(p), G.H.mu, G.H.S) + lp };
    };
    const draw = () => {
        document.getElementById('gda-shared').classList.toggle('active', shared); document.getElementById('gda-sep').classList.toggle('active', !shared);
        const wx = sx.value, wy = sy.value, F = fit(D.known, wx, wy);
        svg.selectAll('*').remove();
        const all = D.papers.filter(p => p.author !== 'Jay' && p.author !== 'joint');
        const xm = d3.max(all, p => p.rate(wx)) * 1.08 || 1, ym = d3.max(all, p => p.rate(wy)) * 1.08 || 1;
        const s = DK.axes(svg, 620, 420, { l: 64, r: 16, t: 12, b: 48 }, [0, xm], [0, ym], `\\text{"${wx}" per 1,000 words}`, `\\text{"${wy}" per 1,000 words}`);
        const N = 70, vals = [];   // where the log odds changes sign: the decision boundary
        for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) { const x = xm * i / (N - 1), y = ym * j / (N - 1); vals.push(F.lo({ rate: w => (w === wx ? x : y) })); }
        const gx = d3.scaleLinear().domain([0, N - 1]).range([s.x(0), s.x(xm)]), gy = d3.scaleLinear().domain([0, N - 1]).range([s.y(0), s.y(ym)]);
        const proj = d3.geoPath(d3.geoTransform({ point(px, py) { this.stream.point(gx(px), gy(py)); } }));
        svg.insert('g', 'g').selectAll('path').data(d3.contours().size([N, N]).thresholds([0])(vals)).join('path').attr('d', proj).attr('fill', CM).attr('fill-opacity', 0.1).attr('stroke', P.green).attr('stroke-width', 2.5);
        [['H', CH], ['M', CM]].forEach(([a, c]) => {   // one and two standard deviations
            const g = F.G[a], S = g.S, tr = S[0][0] + S[1][1], det = S[0][0] * S[1][1] - S[0][1] ** 2, l1 = tr / 2 + Math.sqrt(tr * tr / 4 - det), l2 = tr / 2 - Math.sqrt(tr * tr / 4 - det);
            const ang = Math.atan2(l1 - S[0][0], S[0][1] || 1e-12);
            [1, 2].forEach(k => svg.append('path').attr('d', d3.line()(d3.range(0, 6.3, 0.1).map(t => { const u = k * Math.sqrt(l1) * Math.cos(t), v = k * Math.sqrt(Math.max(l2, 0)) * Math.sin(t);
                return [s.x(g.mu[0] + u * Math.cos(ang) - v * Math.sin(ang)), s.y(g.mu[1] + u * Math.sin(ang) + v * Math.cos(ang))]; }))).attr('fill', 'none').attr('stroke', c).attr('stroke-opacity', k === 1 ? 0.8 : 0.4).attr('stroke-width', 1.6));
        });
        all.forEach(p => svg.append('circle').attr('cx', s.x(p.rate(wx))).attr('cy', s.y(p.rate(wy))).attr('r', 5.5).attr('fill', FED.col(p.author)).attr('fill-opacity', p.author === 'disputed' ? 0 : 0.8).attr('stroke', FED.col(p.author)).attr('stroke-width', 1.8));
        let loo = 0; D.known.forEach(p => { const f = fit(D.known.filter(q => q !== p), wx, wy); loo += (f.lo(p) > 0) === (p.author === 'Madison'); });
        const dm = D.disputed.filter(p => F.lo(p) > 0).length;
        out.innerHTML = `${shared ? 'One shared covariance: the boundary is a straight line.' : 'One covariance per author: the boundary curves.'} Leaving each known paper out in turn, GDA gets <b>${loo} of ${D.known.length}</b> right; it gives <b style="color:${CM};">${dm} of the 12</b> disputed papers to Madison (hollow dots).`;
    };
    [sx, sy].forEach(e => e.addEventListener('change', draw));
    document.getElementById('gda-shared').addEventListener('click', () => { shared = true; draw(); });
    document.getElementById('gda-sep').addEventListener('click', () => { shared = false; draw(); });
    draw();
};

// ---------- 8. where the Gaussian breaks: Madison's "upon"
FED.breaks = function (D) {
    const svg = d3.select('#viz-breaks'); if (svg.empty()) return;
    const v = D.known.filter(p => p.author === 'Madison').map(p => p.rate('upon')), g = FED.gauss(v.map(x => [x, 0]));
    const mu = g.mu[0], sd = Math.sqrt(g.S[0][0]);
    const s = DK.axes(svg, 560, 300, { l: 60, r: 14, t: 12, b: 46 }, [-1.2, 1.6], [0, 12], '\\text{"upon" per 1,000 words, Madison}', '\\text{papers}');
    const bins = d3.bin().domain([-1.2, 1.6]).thresholds(d3.range(-1.2, 1.61, 0.1))(v);
    bins.forEach(b => b.length && svg.append('rect').attr('x', s.x(b.x0) + 1).attr('width', s.x(b.x1) - s.x(b.x0) - 2).attr('y', s.y(b.length)).attr('height', s.y(0) - s.y(b.length)).attr('fill', CM).attr('rx', 2));
    const dens = x => v.length * 0.1 * Math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * Math.sqrt(2 * Math.PI));
    svg.append('path').attr('d', d3.line()(d3.range(-1.2, 1.61, 0.02).map(x => [s.x(x), s.y(dens(x))]))).attr('fill', 'none').attr('stroke', P.yellow).attr('stroke-width', 2.5);
    svg.append('line').attr('x1', s.x(0)).attr('x2', s.x(0)).attr('y1', s.y(0)).attr('y2', s.y(12)).attr('stroke', P.red).attr('stroke-dasharray', '4,4');
    const zero = v.filter(x => x === 0).length;
    const below = 0.5 * (1 + (function erf(z) { const t = 1 / (1 + 0.3275911 * Math.abs(z)); const y = 1 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-z * z); return z >= 0 ? y : -y; })((0 - mu) / (sd * Math.SQRT2)));
    document.getElementById('breaks-out').innerHTML = `<b>${zero} of ${v.length}</b> Madison papers never use "upon": a spike at exactly zero. The fitted Gaussian (yellow) is smooth and symmetric, and puts <b>${DK.pct(below, 0)}</b> of its weight on negative rates, which cannot exist.`;
};

// ---------- 9. generative or discriminative: who learns faster from few papers?
FED.curve = function (D) {
    const btn = document.getElementById('curve-run'); if (!btn) return;
    const svg = d3.select('#viz-curve'), out = document.getElementById('curve-out'), KS = [1, 2, 3, 4, 6, 8, 10], REP = 60;
    const lr = (train, words) => {   // logistic regression on standardized rates, gradient descent, a little L2
        const X = train.map(p => words.map((_, k) => 1000 * p.c[k] / p.n)), y = train.map(p => (p.author === 'Madison' ? 1 : 0)), d = words.length;
        const mu = d3.range(d).map(k => d3.mean(X, x => x[k])), sd = d3.range(d).map(k => (d3.deviation(X, x => x[k]) || 0) + 1e-6);
        const Z = X.map(x => x.map((v, k) => (v - mu[k]) / sd[k])), w = new Float64Array(d); let b = 0;
        for (let it = 0; it < 200; it++) {
            const g = new Float64Array(d); let gb = 0;
            Z.forEach((z, i) => { let s = b; for (let k = 0; k < d; k++) s += w[k] * z[k]; const e = 1 / (1 + Math.exp(-s)) - y[i]; for (let k = 0; k < d; k++) g[k] += e * z[k]; gb += e; });
            for (let k = 0; k < d; k++) w[k] -= 0.5 * (g[k] / Z.length + 0.1 * w[k]); b -= 0.5 * gb / Z.length;
        }
        return p => { let s = b; for (let k = 0; k < d; k++) s += w[k] * ((1000 * p.c[k] / p.n - mu[k]) / sd[k]); return s > 0; };
    };
    const draw = res => {
        svg.selectAll('*').remove();
        const s = DK.axes(svg, 600, 340, { l: 64, r: 16, t: 12, b: 46 }, [0, 10.5], [0.4, 1], '\\text{training papers per author}', '\\text{accuracy on the other known papers}');
        [['nb', P.green, 'Naive Bayes (generative)'], ['lr', P.purple, 'logistic regression (discriminative)']].forEach(([k, c, name], j) => {
            const pts = res.filter(r => r[k] != null);
            svg.append('path').attr('d', d3.line().x(r => s.x(r.k)).y(r => s.y(r[k]))(pts)).attr('fill', 'none').attr('stroke', c).attr('stroke-width', 2.6);
            pts.forEach(r => svg.append('circle').attr('cx', s.x(r.k)).attr('cy', s.y(r[k])).attr('r', 4.5).attr('fill', c));
            svg.append('text').attr('x', s.x(10.3)).attr('y', s.y(0.52) + j * 20).attr('text-anchor', 'end').attr('fill', c).attr('font-size', 14).text(name);
        });
    };
    btn.addEventListener('click', () => {
        btn.disabled = true; const r = DK.rng(5), res = [];
        const pick = (a, n) => { const ps = D.known.filter(p => p.author === a).slice(); for (let i = ps.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [ps[i], ps[j]] = [ps[j], ps[i]]; } return ps.slice(0, n); };
        let i = 0;
        const step = () => {
            const k = KS[i]; let a = 0, b = 0, n = 0;
            for (let rep = 0; rep < REP; rep++) {
                const train = pick('Hamilton', k).concat(pick('Madison', k)), test = D.known.filter(p => !train.includes(p));
                const m = FED.fit(train, D.words), f = lr(train, D.words);
                test.forEach(p => { const y = p.author === 'Madison'; a += (FED.score(m, p).total > 0) === y; b += f(p) === y; n++; });
            }
            res.push({ k, nb: a / n, lr: b / n }); draw(res);
            out.innerHTML = res.map(q => `${q.k} each: Naive Bayes <b style="color:${P.green};">${DK.pct(q.nb, 0)}</b>, logistic <b style="color:${P.purple};">${DK.pct(q.lr, 0)}</b>`).join('<br>');
            if (++i < KS.length) setTimeout(step, 0); else btn.disabled = false;
        };
        draw([]); setTimeout(step, 0);
    });
    draw([]);
};

FED.init = function () {
    FED.load().then(D => {
        [FED.guess, FED.marks, FED.dice, FED.weigh, FED.smooth, FED.verdict, FED.gda, FED.breaks, FED.curve]
            .forEach(f => { try { f(D); } catch (e) { console.error('FED', e); } });
    });
};
window.FED = FED;
