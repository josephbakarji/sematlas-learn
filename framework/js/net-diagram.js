/*
 * NetDiagram: math-first network diagrams for Reveal decks, in the style of
 * Joseph's Keynote slides. LaTeX symbols ARE the nodes (KaTeX in an HTML
 * overlay synced to SVG coordinates; no foreignObject, so Reveal's scaling
 * cannot blur or displace labels). White ⊕ circles sum, orange σ circles
 * activate, thin white arrows carry w_ij labels.
 *
 * Usage:
 *   const d = NetDiagram.create({
 *     container: '#nd-one',          // a <div class="nd-wrap"> (positioned)
 *     width: 760, height: 320,
 *     nodes: [
 *       { id: 'x1', x: 90, y: 70, tex: 'x_1' },                 // symbol node
 *       { id: 'p1', x: 430, y: 130, kind: 'plus', stage: 1 },   // ⊕
 *       { id: 's1', x: 505, y: 130, kind: 'sigma', stage: 3 },  // σ
 *       { id: 'y1', x: 590, y: 130, tex: '\\hat y_1', stage: 1 },
 *     ],
 *     edges: [
 *       { from: 'x1', to: 'p1', tex: 'w_1', t: 0.5, dy: -12, stage: 1 },
 *       { from: 'p1', to: 'y1', stage: 1 },
 *     ],
 *     labels: [
 *       { x: 260, y: 40, tex: '\\mathbf{W}_1', size: 1.3, color: '#fff', stage: 1 },
 *     ],
 *   });
 *   d.setStage(3);            // show everything with stage <= 3
 *   d.bindFragments(section); // drive stage from Reveal fragments in a section
 *
 * Stages default to 0. Elements fade in/out with the current stage.
 * Requires: d3, katex (loaded globally).
 */
const NetDiagram = (function () {
    const COLORS = {
        edge: '#e8edf7',
        plus: '#f2f4f8',
        sigma: '#e5a52e',
        label: '#dbe4f5',
        weight: '#e5c07b',
    };

    function create(spec) {
        const wrap = document.querySelector(spec.container);
        wrap.classList.add('nd-wrap');
        wrap.style.position = 'relative';
        wrap.style.width = spec.width + 'px';
        wrap.style.height = spec.height + 'px';
        wrap.style.margin = '0 auto';
        wrap.innerHTML = '';

        const svg = d3.select(wrap).append('svg')
            .attr('width', spec.width).attr('height', spec.height)
            .style('position', 'absolute').style('inset', 0)
            .style('background', 'transparent');
        const overlay = d3.select(wrap).append('div')
            .style('position', 'absolute').style('inset', 0)
            .style('pointer-events', 'none');

        // one arrowhead marker per diagram
        const mid = 'nd-arrow-' + Math.abs(spec.container.split('').reduce((a, c) => a * 31 + c.charCodeAt(0) | 0, 7));
        svg.append('defs').append('marker')
            .attr('id', mid).attr('viewBox', '0 0 10 10')
            .attr('refX', 9).attr('refY', 5).attr('markerWidth', 7).attr('markerHeight', 7)
            .attr('orient', 'auto')
            .append('path').attr('d', 'M0,0 L10,5 L0,10 z').attr('fill', COLORS.edge);

        const items = [];   // { stage, els: [d3 selections and/or DOM nodes] }
        const byId = {};
        for (const n of spec.nodes) byId[n.id] = n;

        function nodeRadius(n) {
            if (n.kind === 'plus' || n.kind === 'sigma') return n.r || 15;
            return n.r || 20;   // clearance around a bare symbol
        }

        function texSpan(tex, color, size) {
            const el = document.createElement('div');
            el.style.position = 'absolute';
            el.style.transform = 'translate(-50%, -50%)';
            el.style.color = color || COLORS.label;
            el.style.fontSize = (size || 1) * 21 + 'px';
            el.style.whiteSpace = 'nowrap';
            try { katex.render(tex, el, { throwOnError: false }); }
            catch (e) { el.textContent = tex; }
            return el;
        }

        // ---- edges (drawn first, under nodes) ----
        for (const e of spec.edges || []) {
            const a = byId[e.from], b = byId[e.to];
            const ra = nodeRadius(a), rb = nodeRadius(b) + 4; // leave room for arrowhead
            const dx = b.x - a.x, dy = b.y - a.y, L = Math.hypot(dx, dy);
            const x1 = a.x + dx / L * ra, y1 = a.y + dy / L * ra;
            const x2 = b.x - dx / L * rb, y2 = b.y - dy / L * rb;
            const els = [];
            els.push(svg.append('line')
                .attr('x1', x1).attr('y1', y1).attr('x2', x2).attr('y2', y2)
                .attr('stroke', e.color || COLORS.edge)
                .attr('stroke-width', e.width || 1.5)
                .attr('marker-end', e.noArrow ? null : `url(#${mid})`));
            if (e.tex) {
                const t = e.t === undefined ? 0.5 : e.t;
                const lx = x1 + (x2 - x1) * t + (e.dx || 0);
                const ly = y1 + (y2 - y1) * t + (e.dy || -12);
                const span = texSpan(e.tex, e.texColor || COLORS.weight, e.texSize || 0.72);
                span.style.left = lx + 'px'; span.style.top = ly + 'px';
                overlay.node().appendChild(span);
                els.push(span);
            }
            items.push({ stage: e.stage || 0, until: e.until, els });
        }

        // ---- nodes ----
        for (const n of spec.nodes) {
            const els = [];
            if (n.kind === 'plus' || n.kind === 'sigma') {
                els.push(svg.append('circle')
                    .attr('cx', n.x).attr('cy', n.y).attr('r', n.r || 15)
                    .attr('fill', n.kind === 'plus' ? COLORS.plus : COLORS.sigma));
                const span = texSpan(n.kind === 'plus' ? '+' : '\\sigma', '#0d1017', n.kind === 'plus' ? 1.0 : 0.9);
                span.style.left = n.x + 'px'; span.style.top = (n.y + (n.kind === 'plus' ? 0 : 1)) + 'px';
                span.style.fontWeight = '700';
                overlay.node().appendChild(span);
                els.push(span);
            } else {
                const span = texSpan(n.tex, n.color, n.size || 1.05);
                span.style.left = n.x + 'px'; span.style.top = n.y + 'px';
                overlay.node().appendChild(span);
                els.push(span);
            }
            items.push({ stage: n.stage || 0, until: n.until, els });
        }

        // ---- free labels ----
        for (const l of spec.labels || []) {
            const span = texSpan(l.tex, l.color, l.size || 0.9);
            span.style.left = l.x + 'px'; span.style.top = l.y + 'px';
            if (l.plain) { span.innerHTML = ''; span.textContent = l.plain; span.style.fontFamily = "'DM Sans', sans-serif"; }
            overlay.node().appendChild(span);
            items.push({ stage: l.stage || 0, until: l.until, els: [span] });
        }

        const diagram = {
            setStage(k) {
                for (const it of items) {
                    const on = it.stage <= k && (it.until === undefined || k < it.until);
                    for (const el of it.els) {
                        if (el.style) {
                            el.style.transition = 'opacity 0.35s';
                            el.style.opacity = on ? 1 : 0;
                        } else {
                            el.transition().duration(350).attr('opacity', on ? 1 : 0);
                        }
                    }
                }
            },
            bindFragments(section) {
                const count = () =>
                    section.querySelectorAll('.fragment.visible').length;
                const update = () => diagram.setStage(count());
                Reveal.on('fragmentshown', e => { if (section.contains(e.fragment)) update(); });
                Reveal.on('fragmenthidden', e => { if (section.contains(e.fragment)) update(); });
                Reveal.on('slidechanged', e => { if (e.currentSlide === section) update(); });
                update();
            },
        };
        diagram.setStage(0);
        return diagram;
    }

    return { create };
})();
window.NetDiagram = NetDiagram;
