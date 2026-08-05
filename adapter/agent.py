#!/usr/bin/env python3
"""
SemAtlas Learn agentic deck builder.

Where generate.py asks the model for a whole deck in one shot, this script
runs a small, readable agent loop that makes a small model behave like a
bigger one:

    1. OUTLINE   one structured call: slide list with goals and equations
    2. DRAFT     one call per slide (narrow tasks suit small models)
    3. LINT      deterministic checks, no LLM: grammar, math hazards, quizzes
    4. FIX       one call per slide that failed lint, with the issue list
    5. VERIFY    a checklist pass over all equations (optionally a larger
                 verifier model: the capability ladder)
    6. FIX       one call per finding
    7. ASSEMBLE  splice into the skeleton, exactly like generate.py

The loop is intentionally plain: it is meant to be read. Structure
substitutes for scale; that is the claim this script exists to test.

Stdlib only. Works with Ollama (native structured outputs when available)
or any OpenAI-compatible endpoint.
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GRAMMAR = ROOT / 'grammar'


# ---------------------------------------------------------------- llm calls

def http_json(url, payload, timeout=1800):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def detect_ollama(base_url):
    root = re.sub(r'/v1/?$', '', base_url.rstrip('/'))
    try:
        req = urllib.request.Request(root + '/api/tags')
        urllib.request.urlopen(req, timeout=2).read()
        return root
    except Exception:
        return None


class LLM:
    def __init__(self, base_url, api_key, model):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.ollama_root = detect_ollama(base_url)
        self.calls = 0
        self.tokens = 0
        self.seconds = 0.0

    def chat(self, system, user, temperature=0.6, max_tokens=4000, schema=None):
        """Returns text. If schema is given and we are on Ollama, generation
        is constrained to that JSON schema (no salvage needed, by design)."""
        t0 = time.time()
        if self.ollama_root:
            payload = {
                'model': self.model, 'stream': False,
                'messages': [{'role': 'system', 'content': system},
                             {'role': 'user', 'content': user}],
                'options': {'temperature': temperature, 'num_predict': max_tokens},
            }
            if schema:
                payload['format'] = schema
            out = http_json(self.ollama_root + '/api/chat', payload)
            text = out['message']['content']
            self.tokens += out.get('prompt_eval_count', 0) + out.get('eval_count', 0)
        else:
            req = urllib.request.Request(
                self.base_url + '/chat/completions',
                data=json.dumps({
                    'model': self.model, 'temperature': temperature,
                    'max_tokens': max_tokens,
                    'messages': [{'role': 'system', 'content': system},
                                 {'role': 'user', 'content': user}],
                }).encode(),
                headers={'Content-Type': 'application/json',
                         'Authorization': 'Bearer ' + (self.api_key or 'none')})
            with urllib.request.urlopen(req, timeout=1800) as r:
                out = json.load(r)
            text = out['choices'][0]['message']['content']
            u = out.get('usage', {})
            self.tokens += u.get('total_tokens', 0)
        self.calls += 1
        self.seconds += time.time() - t0
        return text

    def chat_json(self, system, user, schema, **kw):
        text = self.chat(system, user, schema=schema, **kw)
        text = re.sub(r'^```[a-zA-Z]*\s*|```\s*$', '', text.strip())
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            m = re.search(r'\{.*\}', text, flags=re.S)
            if m:
                return json.loads(m.group(0))
            raise


# ---------------------------------------------------------------- linter

def lint_section(html, is_title=False, is_quiz=False):
    """Deterministic checks. Returns a list of issue strings (empty = pass)."""
    issues = []
    if html.count('<section') != 1:
        issues.append('must contain exactly one <section> element')
    for ch, name in [('—', 'em-dash'), ('&mdash;', 'em-dash entity')]:
        if ch in html:
            issues.append(f'contains an {name}: replace with comma, colon, or period')
    for m in re.finditer(r'\$\$(.*?)\$\$|\\\((.*?)\\\)', html, flags=re.S):
        body = m.group(1) or m.group(2) or ''
        if re.search(r'(?<!\\)<(?![a-zA-Z/])', body):
            issues.append('bare < inside math: write \\lt instead')
            break
    for m in re.finditer(r'\$\$(.*?)\$\$', html, flags=re.S):
        body = m.group(1)
        if re.search(r'\\\\[a-zA-Z]', body):
            issues.append('double-escaped LaTeX command inside math (\\\\frac etc.): use single backslash')
            break
        if '\\n' in body and 'align' not in body:
            issues.append('literal \\n inside math: remove it')
            break
    if not is_title and not is_quiz:
        if 'class="fragment' not in html:
            issues.append('no fragments: add class="fragment" to elements that should appear on click')
        if '<h2' not in html:
            issues.append('content slide needs an <h2> title')
        if '$$' in html and 'eqbox' not in html:
            issues.append('display equations belong inside <div class="eqbox">')
    if is_quiz:
        m = re.search(r"data-quiz='(.*?)'", html, flags=re.S)
        if not m:
            issues.append("quiz slide needs a div with data-quiz='...' JSON")
        else:
            try:
                q = json.loads(m.group(1))
                for k in ('question', 'choices', 'correct', 'explanation'):
                    if k not in q:
                        issues.append(f'quiz JSON missing "{k}"')
            except json.JSONDecodeError as e:
                issues.append(f'quiz JSON does not parse: {e}')
    for pre in re.findall(r'<(?:pre|code)[^>]*>(.*?)</(?:pre|code)>', html, flags=re.S):
        if any(ord(c) > 127 for c in pre):
            issues.append('non-ASCII characters inside code')
            break
    if len(html) > 4500:
        issues.append('section too long, likely overflows the slide: cut to one idea')
    return issues


def extract_one_section(text):
    text = re.sub(r'^```[a-zA-Z]*\s*|```\s*$', '', text.strip())
    m = re.search(r'<section\b.*?</section>', text, flags=re.S)
    if m:
        return m.group(0)
    if '<' in text:
        return '<section>\n' + text.strip() + '\n</section>'
    return None


# ---------------------------------------------------------------- pipeline

OUTLINE_SCHEMA = {
    'type': 'object',
    'properties': {
        'title': {'type': 'string'},
        'slides': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'goal': {'type': 'string'},
                    'type': {'type': 'string', 'enum': ['title', 'concept', 'equation', 'quiz']},
                    'equations': {'type': 'array', 'items': {'type': 'string'}},
                    'symbols_to_define': {'type': 'array', 'items': {'type': 'string'}},
                },
                'required': ['title', 'goal', 'type'],
            },
        },
    },
    'required': ['title', 'slides'],
}

FINDINGS_SCHEMA = {
    'type': 'object',
    'properties': {
        'findings': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'slide': {'type': 'integer'},
                    'issue': {'type': 'string'},
                    'correction': {'type': 'string'},
                },
                'required': ['slide', 'issue', 'correction'],
            },
        },
    },
    'required': ['findings'],
}


def main():
    ap = argparse.ArgumentParser(description='Agentic SAL deck builder')
    ap.add_argument('topic')
    ap.add_argument('--model', default='qwen2.5-coder:3b')
    ap.add_argument('--verifier-model', default=None,
                    help='optional larger model for the verify pass (capability ladder)')
    ap.add_argument('--base-url', default='http://localhost:11434/v1')
    ap.add_argument('--api-key', default='ollama')
    ap.add_argument('--slides', type=int, default=12)
    ap.add_argument('--audience', default='undergraduate students seeing this for the first time')
    ap.add_argument('--suffix', default='agent')
    ap.add_argument('--max-fix-rounds', type=int, default=2)
    ap.add_argument('--no-verify', action='store_true',
                    help='skip the LLM verify pass (lint only)')
    args = ap.parse_args()

    grammar = (GRAMMAR / 'system_prompt.md').read_text()
    skeleton = (GRAMMAR / 'skeleton.html').read_text()
    llm = LLM(args.base_url, args.api_key, args.model)
    verifier = (LLM(args.base_url, args.api_key, args.verifier_model)
                if args.verifier_model else llm)
    t_start = time.time()
    stats = {'lint_issues': 0, 'lint_fixed': 0, 'verify_findings': 0}

    # 1. OUTLINE
    print(f'[1/5] outline ({args.model})...')
    outline = llm.chat_json(
        'You plan teaching decks. Output JSON only.',
        f'Plan a deck of exactly {args.slides} slides teaching: {args.topic}\n'
        f'Audience: {args.audience}\n'
        'First slide type "title", last slide type "quiz". Build up carefully: '
        'every important equation in the buildup appears in some slide\'s '
        '"equations" list, written in LaTeX. List the symbols each slide must define.',
        OUTLINE_SCHEMA, max_tokens=3000)
    slides = outline['slides']
    if not slides or slides[-1].get('type') != 'quiz':
        slides.append({'title': 'Check yourself', 'goal': 'One question testing the key idea of the deck',
                       'type': 'quiz', 'equations': [], 'symbols_to_define': []})
    print(f'      {len(slides)} slides planned: ' + ' | '.join(s['title'][:28] for s in slides[:6]) + ' ...')

    # 2 + 3 + 4. DRAFT each slide, LINT, FIX
    sections = []
    for i, sl in enumerate(slides):
        is_title = sl['type'] == 'title' or i == 0
        is_quiz = sl['type'] == 'quiz' or i == len(slides) - 1
        brief = (
            f'Deck topic: {args.topic}\nAudience: {args.audience}\n'
            f'You are writing SLIDE {i + 1} of {len(slides)}.\n'
            f'Slide title: {sl["title"]}\nSlide goal: {sl["goal"]}\n'
            f'Slide type: {sl["type"]}\n'
            + (('Equations to include, each alone in an eqbox as $$...$$:\n'
                + ''.join(f'    {e}\n' for e in sl.get('equations', [])))
               if sl.get('equations') else '')
            + (('Symbols to define in bullets: '
                + ', '.join(sl.get('symbols_to_define', [])) + '\n')
               if sl.get('symbols_to_define') else '')
            + (f'Previous slide was: {slides[i - 1]["title"]}\n' if i else '')
            + (f'Next slide will be: {slides[i + 1]["title"]}\n' if i + 1 < len(slides) else '')
            + 'Output ONE <section>...</section> block and nothing else.'
        )
        raw = llm.chat(grammar, brief, max_tokens=2000)
        sec = extract_one_section(raw) or '<section><h2>' + sl['title'] + '</h2></section>'
        for _ in range(args.max_fix_rounds):
            issues = lint_section(sec, is_title, is_quiz)
            if not issues:
                break
            stats['lint_issues'] += len(issues)
            fixed = llm.chat(
                grammar,
                'This slide has problems. Rewrite it fixing ONLY these issues, '
                'keep everything else the same. Output ONE <section> block.\n\n'
                'ISSUES:\n- ' + '\n- '.join(issues) + '\n\nSLIDE:\n' + sec,
                max_tokens=2200)
            new = extract_one_section(fixed)
            if new:
                sec = new
                stats['lint_fixed'] += len(issues)
        sections.append(sec)
        print(f'[2/5] slide {i + 1}/{len(slides)}: {sl["title"][:40]}'
              + (' (lint fixed)' if lint_section(sec, is_title, is_quiz) == [] and stats['lint_issues'] else ''))

    # 5. VERIFY math with a checklist pass
    vmodel = args.verifier_model or args.model
    print(f'[3/5] verify pass ({vmodel})...')
    eq_report = []
    for i, sec in enumerate(sections):
        eqs = re.findall(r'\$\$(.*?)\$\$', sec, flags=re.S)
        for e in eqs:
            eq_report.append(f'slide {i + 1}: $${" ".join(e.split())}$$')
    findings = {'findings': []}
    if eq_report and not args.no_verify:
        findings = verifier.chat_json(
            'You are a strict mathematics reviewer for teaching material. '
            'Output JSON only.',
            f'Topic: {args.topic}\n\nBelow are all display equations in a deck, '
            'with slide numbers. Check each for mathematical errors: wrong '
            'subscripts, wrong distribution in expectations, sign errors, '
            'missing terms, wrong inequality direction. Report ONLY real '
            'errors, with the corrected equation.\n\n' + '\n'.join(eq_report),
            FINDINGS_SCHEMA, temperature=0.2, max_tokens=2000)
    stats['verify_findings'] = len(findings['findings'])

    # 6. FIX verified findings
    for f in findings['findings']:
        idx = f['slide'] - 1
        if 0 <= idx < len(sections):
            print(f'[4/5] fixing slide {f["slide"]}: {f["issue"][:60]}')
            fixed = llm.chat(
                grammar,
                'A mathematics reviewer found an error in this slide. Apply the '
                'correction exactly. Output ONE <section> block.\n\n'
                f'ISSUE: {f["issue"]}\nCORRECTION: {f["correction"]}\n\n'
                'SLIDE:\n' + sections[idx],
                max_tokens=2200)
            new = extract_one_section(fixed)
            if new and lint_section(new) == lint_section(sections[idx]):
                sections[idx] = new

    # 7. ASSEMBLE
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', args.topic.lower()).strip('-')[:40]
    out_dir = ROOT / 'decks' / (slug + '-' + args.suffix)
    out_dir.mkdir(parents=True, exist_ok=True)
    html = skeleton.replace('{{TITLE}}', outline.get('title', args.topic.title()))
    html = html.replace('{{SECTIONS}}', '\n\n'.join(sections))
    (out_dir / 'index.html').write_text(html)
    (out_dir / 'outline.json').write_text(json.dumps(outline, indent=1))
    meta = {
        'topic': args.topic, 'model': args.model,
        'verifier_model': args.verifier_model, 'mode': 'agentic',
        'slides_planned': len(slides), 'sections_produced': len(sections),
        'llm_calls': llm.calls + (verifier.calls if verifier is not llm else 0),
        'tokens_total': llm.tokens + (verifier.tokens if verifier is not llm else 0),
        'wall_seconds': round(time.time() - t_start, 1),
        **stats,
    }
    (out_dir / 'meta.json').write_text(json.dumps(meta, indent=1))
    print(f'[5/5] done: {len(sections)} slides, {meta["llm_calls"]} calls, '
          f'{meta["wall_seconds"]}s, lint issues fixed: {stats["lint_fixed"]}, '
          f'verify findings: {stats["verify_findings"]}')
    print(f'deck: {out_dir}/index.html')


if __name__ == '__main__':
    main()
