#!/usr/bin/env python3
"""
SemAtlas Learn deck generator.

Points at any OpenAI-compatible chat endpoint: Ollama, LM Studio, llama.cpp
server, or a hosted API. The model writes only <section> blocks in the SAL
grammar; this script owns the boilerplate and splices them into the skeleton.
The scaffolding lowers the intelligence bar: that is the design bet.

Examples:
    # local model via Ollama (default base URL)
    python3 generate.py "gradient descent" --model qwen2.5-coder:3b

    # LM Studio
    python3 generate.py "bayes theorem" --model local-model \
        --base-url http://localhost:1234/v1

    # hosted API
    ANTHROPIC-style APIs differ; any OpenAI-compatible endpoint works:
    python3 generate.py "entropy" --model gpt-4o-mini \
        --base-url https://api.openai.com/v1 --api-key $OPENAI_API_KEY

No dependencies beyond the standard library.
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


def slugify(s):
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')
    return s[:60] or 'deck'


def call_llm(base_url, api_key, model, system, user, temperature, max_tokens):
    req = urllib.request.Request(
        base_url.rstrip('/') + '/chat/completions',
        data=json.dumps({
            'model': model,
            'messages': [
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': user},
            ],
            'temperature': temperature,
            'max_tokens': max_tokens,
        }).encode(),
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + (api_key or 'none'),
        },
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=1800) as r:
        out = json.load(r)
    dt = time.time() - t0
    msg = out['choices'][0]['message']['content']
    usage = out.get('usage', {})
    return msg, usage, dt


def extract_sections(text):
    # strip markdown fences if the model added them anyway
    text = re.sub(r'^```[a-zA-Z]*\s*', '', text.strip())
    text = re.sub(r'```\s*$', '', text.strip())
    sections = re.findall(r'<section\b.*?</section>', text, flags=re.S)
    return sections, False


def salvage_sections(text):
    """Small models often emit the right vocabulary in the wrong framing:
    markdown headings and --- separators instead of <section> wrappers.
    The scaffolding meets the model halfway: split, clean, wrap."""
    text = re.sub(r'^```[a-zA-Z]*\s*', '', text.strip())
    text = re.sub(r'```\s*$', '', text.strip())
    chunks = re.split(r'\n\s*---+\s*\n', text)
    secs = []
    for c in chunks:
        c = re.sub(r'^#{1,6} .*$', '', c, flags=re.M)          # drop md headings
        c = re.sub(r'^\*\*[^*]+\*\*\s*$', '', c, flags=re.M)  # drop bold-line headings
        c = re.sub(r'^Kicker:\s*(.+)$', r'<p class="kicker">\1</p>', c, flags=re.M)
        c = c.strip()
        if c and '<' in c:
            secs.append('<section>\n' + c + '\n</section>')
    return secs


def main():
    ap = argparse.ArgumentParser(description='Generate a SAL deck with any OpenAI-compatible model')
    ap.add_argument('topic')
    ap.add_argument('--model', default='qwen2.5-coder:3b')
    ap.add_argument('--base-url', default='http://localhost:11434/v1',
                    help='OpenAI-compatible endpoint (default: local Ollama)')
    ap.add_argument('--api-key', default='ollama')
    ap.add_argument('--slides', type=int, default=8)
    ap.add_argument('--audience', default='undergraduate students seeing this for the first time')
    ap.add_argument('--out', default=None, help='output deck folder (default: decks/<slug>)')
    ap.add_argument('--temperature', type=float, default=0.7)
    ap.add_argument('--max-tokens', type=int, default=8000)
    ap.add_argument('--suffix', default='', help='append to the deck folder name (for experiments)')
    args = ap.parse_args()

    system = (GRAMMAR / 'system_prompt.md').read_text()
    skeleton = (GRAMMAR / 'skeleton.html').read_text()

    user = (
        f'Write a deck of about {args.slides} sections teaching: {args.topic}\n'
        f'Audience: {args.audience}\n'
        'Remember: output only the <section> blocks, first one is the title '
        'slide, last one is a quiz. Start your reply with "<section>" as the '
        'very first characters, and wrap every slide in <section>...</section>. '
        'Do not use markdown headings or --- separators.'
    )

    print(f'model: {args.model} @ {args.base_url}')
    print(f'topic: {args.topic}')
    print('generating...')
    try:
        raw, usage, dt = call_llm(args.base_url, args.api_key, args.model,
                                  system, user, args.temperature, args.max_tokens)
    except Exception as e:
        sys.exit(f'LLM call failed: {e}\n'
                 'Is the server running? For Ollama: `ollama serve` then `ollama pull <model>`.')

    sections, salvaged = extract_sections(raw)
    if not sections:
        sections = salvage_sections(raw)
        salvaged = bool(sections)
    slug = slugify(args.topic) + (('-' + args.suffix) if args.suffix else '')
    out_dir = Path(args.out) if args.out else ROOT / 'decks' / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / 'raw_response.txt').write_text(raw)
    if not sections:
        sys.exit(f'No <section> blocks found in the response. '
                 f'Raw output saved to {out_dir}/raw_response.txt')

    html = skeleton.replace('{{TITLE}}', args.topic.title())
    html = html.replace('{{SECTIONS}}', '\n\n'.join(sections))
    (out_dir / 'index.html').write_text(html)

    meta = {
        'topic': args.topic, 'model': args.model, 'base_url': args.base_url,
        'slides_requested': args.slides, 'sections_produced': len(sections),
        'audience': args.audience, 'temperature': args.temperature,
        'generation_seconds': round(dt, 1), 'usage': usage,
        'salvaged': salvaged,
    }
    (out_dir / 'meta.json').write_text(json.dumps(meta, indent=1))

    print(f'sections: {len(sections)}  time: {dt:.0f}s  tokens: {usage}')
    print(f'deck:     {out_dir}/index.html')
    print(f'view:     ./serve.sh  then open /decks/{out_dir.name}/')


if __name__ == '__main__':
    main()
