/* SemAtlas Learn static quiz component.
   No server, no accounts. A quiz is a div with a data-quiz JSON attribute:

   <div class="quiz" data-quiz='{
     "question": "What does the least squares objective minimize?",
     "choices": {"A": "...", "B": "...", "C": "...", "D": "..."},
     "correct": "B",
     "explanation": "...",
     "hint": "..."
   }'></div>

   KaTeX delimiters \\( \\) and $$ $$ work inside all fields. */

const SALQuiz = {};

SALQuiz.init = function () {
    document.querySelectorAll('.quiz[data-quiz]').forEach(el => {
        let spec;
        try { spec = JSON.parse(el.dataset.quiz); }
        catch (e) { el.textContent = 'quiz JSON error: ' + e.message; return; }
        SALQuiz.build(el, spec);
    });
};

SALQuiz.build = function (el, spec) {
    el.innerHTML = '';
    const q = document.createElement('div');
    q.className = 'q';
    q.innerHTML = spec.question;
    el.appendChild(q);

    const explain = document.createElement('div');
    explain.className = 'explain';

    const keys = Object.keys(spec.choices);
    keys.forEach(k => {
        const b = document.createElement('button');
        b.className = 'choice';
        b.innerHTML = '<b>' + k + '.</b> ' + spec.choices[k];
        b.onclick = () => {
            if (k === spec.correct) {
                b.classList.add('correct');
                explain.innerHTML = '<b>Correct.</b> ' + (spec.explanation || '');
                explain.classList.add('show');
                el.querySelectorAll('.choice').forEach(c => { c.disabled = true; });
            } else {
                b.classList.add('wrong');
                b.disabled = true;
                explain.innerHTML = (spec.hint ? '<b>Not quite.</b> ' + spec.hint : '<b>Not quite.</b> Try again.');
                explain.classList.add('show');
            }
            SALQuiz.math(el);
        };
        el.appendChild(b);
    });
    el.appendChild(explain);
    SALQuiz.math(el);
};

SALQuiz.math = function (el) {
    if (typeof renderMathInElement === 'function') {
        renderMathInElement(el, { delimiters: [
            { left: '\\(', right: '\\)', display: false },
            { left: '$$', right: '$$', display: true }]});
    }
};

window.SALQuiz = SALQuiz;
