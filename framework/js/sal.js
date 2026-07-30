/* SemAtlas Learn boot helper.
   One call wires up Reveal, KaTeX auto-render, quizzes, and media hygiene:

     SAL.init();                       // defaults
     SAL.init({ width: 1280, height: 720, extraPlugins: [] });

   Load order in a deck (all relative to the deck folder):
     ../../framework/vendor/reveal.js
     ../../framework/vendor/highlight.js      (optional, for code)
     ../../framework/vendor/katex/katex.min.js
     ../../framework/vendor/katex/contrib/auto-render.min.js
     ../../framework/js/quiz.js               (optional, for quizzes)
     ../../framework/js/net-diagram.js        (optional, for networks)
     ../../framework/js/sal.js
*/

const SAL = {};

SAL.init = function (opts) {
    opts = opts || {};
    const plugins = [];
    if (typeof RevealHighlight !== 'undefined') plugins.push(RevealHighlight);
    (opts.extraPlugins || []).forEach(p => plugins.push(p));

    Reveal.initialize({
        hash: true,
        slideNumber: opts.slideNumber || false,
        progress: opts.progress !== undefined ? opts.progress : false,
        transition: opts.transition || 'fade',
        transitionSpeed: 'fast',
        width: opts.width || 1280,
        height: opts.height || 720,
        preloadIframes: false,
        plugins: plugins,
    });

    Reveal.on('ready', () => {
        if (typeof renderMathInElement === 'function') {
            renderMathInElement(document.body, { delimiters: [
                { left: '\\(', right: '\\)', display: false },
                { left: '$$', right: '$$', display: true }]});
        }
        if (typeof SALQuiz !== 'undefined') SALQuiz.init();
    });

    // lazy iframes + pause media when leaving a slide
    Reveal.on('slidechanged', e => {
        const ifr = e.currentSlide.querySelector('iframe[data-src]');
        if (ifr && !ifr.src) ifr.src = ifr.dataset.src;
        document.querySelectorAll('video, audio').forEach(m => {
            if (!e.currentSlide.contains(m)) m.pause();
        });
    });

    // fragment-driven canvas hooks: give a fragment data-action="name"
    // and register SAL.actions.name = { show: fn, hide: fn }
    SAL.actions = SAL.actions || {};
    Reveal.on('fragmentshown', e => {
        const a = SAL.actions[e.fragment.dataset.action];
        if (a && a.show) a.show();
    });
    Reveal.on('fragmenthidden', e => {
        const a = SAL.actions[e.fragment.dataset.action];
        if (a && a.hide) a.hide();
    });
};

window.SAL = SAL;
