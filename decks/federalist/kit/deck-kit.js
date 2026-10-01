/* The deck kit: helpers every transformed deck shares (D13, 2026-09-30).
   A deck loads this before its own script and builds its widgets on DK, so plotting,
   math labels and colours change in one place. Decks written before the kit keep their
   own PAL and axes() until they are transformed; DK never touches those names.

     DK.PAL                     the One Dark palette the decks use
     DK.axes(svg, W, H, M, xd, yd, xTex, yTex)   linear axes with KaTeX labels, returns {x, y}
     DK.intTicks(svg, s, vals)  integer ticks on the y axis
     DK.tex(sel, tex, x, y, {color, size, w, anchor})   a KaTeX label inside an SVG
     DK.math(el)                render \( \) math inside an element
     DK.rng(seed), DK.gauss(r)  repeatable random numbers
     DK.pct(v, d), DK.num(v, d) formatting (a true minus sign)
     DK.solve(A, b)             small linear systems, partial pivoting
     DK.onShow(sectionId, fn)   run fn once, the first time a slide is shown (or when printing)
*/
(function () {
    'use strict';
    if (window.DK) return;
    const PAL = { blue: '#61afef', green: '#98c379', yellow: '#e5c07b', red: '#e06c75', purple: '#c678dd',
                  cyan: '#56b6c2', orange: '#d19a66', grid: '#4a5261', ink: '#e6ebf5', inkMuted: '#dbe4f5', bg: '#0d1017' };
    const DK = { PAL };
    DK.math = el => { if (el && window.renderMathInElement) renderMathInElement(el, { delimiters: [{ left: '\\(', right: '\\)', display: false }], throwOnError: false }); };
    DK.num = (v, d = 2) => Number(v).toFixed(d).replace('-', '−');
    DK.pct = (v, d = 1) => (100 * v).toFixed(d) + '%';
    DK.rng = seed => () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
    DK.gauss = r => Math.sqrt(-2 * Math.log(r() + 1e-12)) * Math.cos(2 * Math.PI * r());
    DK.tex = function (sel, tex, x, y, opt = {}) {
        const w = opt.w || 280, anchor = opt.anchor || 'start';
        const fo = sel.append('foreignObject').attr('x', anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x).attr('y', y - 15).attr('width', w).attr('height', 30);
        const div = fo.append('xhtml:div').style('color', opt.color || PAL.ink).style('font-size', (opt.size || 15) + 'px').style('line-height', '30px')
            .style('white-space', 'nowrap').style('text-align', anchor === 'middle' ? 'center' : anchor === 'end' ? 'right' : 'left');
        try { katex.render(tex, div.node(), { throwOnError: false }); } catch (e) { div.text(tex); }
        return fo;
    };
    DK.axes = function (svg, W, H, M, xdom, ydom, xlab, ylab) {
        const x = d3.scaleLinear().domain(xdom).range([M.l, W - M.r]);
        const y = d3.scaleLinear().domain(ydom).range([H - M.b, M.t]);
        svg.append('g').attr('class', 'axis').attr('transform', `translate(0,${H - M.b})`).call(d3.axisBottom(x).ticks(5));
        svg.append('g').attr('class', 'axis').attr('transform', `translate(${M.l},0)`).call(d3.axisLeft(y).ticks(5));
        if (xlab) DK.tex(svg, xlab, (M.l + W - M.r) / 2, H - 12, { anchor: 'middle', size: 16, w: W });
        if (ylab) {
            const g = svg.append('g').attr('transform', `translate(16,${(M.t + H - M.b) / 2}) rotate(-90)`);
            DK.tex(g, ylab, 0, 0, { anchor: 'middle', size: 16, w: H });
        }
        return { x, y };
    };
    DK.intTicks = (svg, s, vals) => svg.selectAll('g.axis').filter((d, i) => i === 1).call(d3.axisLeft(s.y).tickValues(vals).tickFormat(d3.format('d')));
    DK.solve = function (A, b) {
        const n = b.length, M = A.map((r, i) => [...r, b[i]]);
        for (let c = 0; c < n; c++) {
            let p = c; for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[p][c])) p = r;
            [M[c], M[p]] = [M[p], M[c]];
            for (let r = 0; r < n; r++) if (r !== c) { const f = M[r][c] / M[c][c]; for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]; }
        }
        return M.map((r, i) => r[n] / r[i]);
    };
    DK.onShow = function (id, fn) {
        let done = false;
        const run = () => { if (done) return; const s = window.Reveal && Reveal.getCurrentSlide(); if ((s && s.id === id) || /print-pdf/.test(location.search)) { done = true; fn(); } };
        if (window.Reveal) { Reveal.on('slidechanged', run); Reveal.on('ready', run); }
        run();
    };
    window.DK = DK;
})();
