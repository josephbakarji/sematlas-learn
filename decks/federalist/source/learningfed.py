"""Quizzes, tutor and references for generative_federalist. A file, so no shell touches $ signs."""
import json, os, sys
from pathlib import Path
REPO = os.path.expanduser('~/Documents/00-projects/04-web-apps/learnslides-wt-flag')
sys.path.insert(0, REPO)
from services.concept_graph import slides_of  # noqa: E402
top = {s['id']: s['top'] for s in slides_of(Path(f'{REPO}/data/slides/generative_federalist.html')) if s['top'] is not None}
def dump(o, p):
    with open(p, 'w') as f: json.dump(o, f, indent=1, ensure_ascii=False); f.write('\n')
Q = lambda qid, after, q, ch, c, ex, h: {'type': 'quiz_engine', 'id': qid, 'after_section': top[after], 'enable_chat': True, 'enable_generate': True,
    'static_question': {'question': q, 'choices': ch, 'correct': c, 'explanation': ex, 'hint': h}}
qs = [
    Q('q1_function_words', 'small-words', 'Why did Mosteller and Wallace count words like "upon", "by" and "on" instead of words like "taxes", "army" or "senate"?',
      {'A': 'Because function words are more frequent, so their counts are less noisy, and they barely depend on the topic: a writer uses them out of habit',
       'B': 'Because topic words appear in too many papers to be counted reliably',
       'C': 'Because Hamilton and Madison agreed beforehand to use different function words',
       'D': 'Because topic words are always identical in both authors\' papers'},
      'A', 'Hamilton and Madison wrote about the same constitution, so topic words would track the subject of a paper, not its author. Function words carry no topic; how often you write "upon" is a habit, and a habit is a fingerprint. Being frequent also makes their rates stable from paper to paper.',
      'If two people write about the same subject, which words would differ because of who wrote them rather than what they wrote about?'),
    Q('q2_mle_die', 'dice-fit', 'Hamilton\'s 51 papers contain 57,905 function words, 372 of them "upon". Without smoothing, what is \\(\\phi_{\\text{upon} \\mid 0}\\)?',
      {'A': '1/70, since the die has 70 faces',
       'B': 'The share of Hamilton\'s papers that contain "upon"',
       'C': '372 / 57,905, about 0.0064: the share of his function words that are "upon"',
       'D': 'It cannot be found without gradient descent'},
      'C', 'Maximum likelihood for a die gives each face its observed frequency: \\(\\phi_{k \\mid y} = n_{k \\mid y} / N_y\\). It is not 1/70 (that would be a fair die, ignoring the data) and not the share of papers containing the word (that is the Bernoulli model, which counts papers, not words). No gradient descent: the maximum has a closed form.',
      'Of all the function words Hamilton wrote, what fraction were "upon"?'),
    Q('q3_zero', 'never-seen', 'Trained on only three papers per author with no smoothing, a test paper contains the word "her", which Madison never used in those three papers. What happens?',
      {'A': 'The word is ignored and the other words decide',
       'B': '\\(\\phi_{\\text{her} \\mid 1} = 0\\), so the probability of the paper under Madison is 0: one word vetoes Madison whatever the rest says',
       'C': 'The paper is assigned to Madison, since the word is new evidence',
       'D': 'The model averages the two authors'},
      'B', 'The likelihood is a product over the words of the paper. One factor of zero makes the whole product zero, so Madison is ruled out by a single word. If the paper also contains a word Hamilton never used, both are zero and there is no answer. Laplace smoothing adds \\(\\alpha\\) to every count so no face of the die is ever zero.',
      'What does one factor of zero do to a product?'),
    Q('q4_gda_logistic', 'gda-deep', 'GDA with one covariance shared by both authors gives a straight decision boundary. Why?',
      {'A': 'Because the Gaussians are always circles',
       'B': 'Because the data happen to be linearly separable',
       'C': 'Because GDA runs gradient descent on a linear model',
       'D': 'Because the quadratic terms \\(r^\\top \\Sigma^{-1} r\\) are the same for both authors and cancel in the log odds, leaving a linear function of \\(r\\)'},
      'D', 'The log odds is the difference of two Gaussian log densities. With the same \\(\\Sigma\\), both contain the same \\(r^\\top \\Sigma^{-1} r\\), which cancels; what remains is \\(\\theta^\\top r + \\theta_0\\), the form of logistic regression. With a covariance per author the quadratic terms differ and the boundary curves. Nothing about separability or gradient descent is involved.',
      'Write the two log densities and subtract them. Which term is the same in both?'),
    Q('q5_few_data', 'curve', 'With one or two training papers per author, Naive Bayes beats logistic regression on the other known papers. What is the best explanation?',
      {'A': 'Naive Bayes is always more accurate than logistic regression',
       'B': 'Logistic regression cannot use word counts',
       'C': 'Naive Bayes assumes a lot about how papers are written; with little data, those assumptions supply what the data cannot, while logistic regression must learn 70 weights from a handful of examples',
       'D': 'The test papers are easier for Naive Bayes'},
      'C', 'A generative model with strong assumptions has fewer effective degrees of freedom: each word\'s rate is estimated on its own by counting. Logistic regression must find 70 weights jointly from a handful of papers and overfits. With more data the gap closes, and where the assumptions are wrong the discriminative model can end up ahead (Ng and Jordan, 2002). So "always" is wrong.',
      'How many numbers does each model have to get right, and how much does each one assume?'),
]
dump({'lecture_id': 'generative_federalist', 'questions': qs}, f'{REPO}/data/questions/generative_federalist.json')
SYS = """You are a tutor leading one student through a new authorship question, right after a lecture that settled who wrote the twelve disputed Federalist Papers with generative models.

THE FACTS (use only these).
- 85 essays signed Publius: 51 by Hamilton, 14 by Madison, 5 by Jay, 3 joint, 12 disputed between Hamilton and Madison.
- The model counts 70 function words (Mosteller and Wallace's list). Each author is a 70-sided die; phi_k|y is the share of author y's function words that are word k, found by counting.
- Hamilton uses "upon" about 3.3 times per 1,000 words, Madison about 0.16; "on" about 3.4 against 7.7; "by" about 7.2 against 11.6.
- Classifying: the log odds for Madison is the prior log odds plus one vote per word, log of phi_word|Madison over phi_word|Hamilton.
- Without smoothing a word one author never used vetoes that author; Laplace smoothing adds alpha to every count.
- Naive Bayes on the 65 known papers: 100% leave-one-out; 11 of 12 disputed papers to Madison; No. 55 leans Hamilton (log odds -2.9), the case Mosteller and Wallace also found weakest.
- GDA on the rates of "upon" and "by": 63 of 65 leave-one-out, 12 of 12 to Madison, although Madison's "upon" is not Gaussian (11 of 14 papers never use it).
- With one training paper per author, Naive Bayes is about 74% accurate on the other papers, logistic regression about 51%; with ten each, 96% against 94%.

THE PLAN (private). The bracket after each is for you, never read it out.
1. "Suppose two students in your class each wrote 20 lab reports, and a 21st report has no name. Which words would you count, and why not the words about the experiment?" [Function words: frequent, topic-free habits. Topic words track the lab, not the writer.]
2. "You fit a die for each student from their 20 reports. How do you get the probability of the word 'basically' for student A?" [Count: occurrences of 'basically' in A's reports over all of A's counted words. If stuck, send them to "The two dice, learned from 65 papers".]
3. "Student B never wrote 'basically' in their 20 reports, and the unnamed report has it twice. What does your model say, and what would you change?" [Without smoothing, B is ruled out by one word; add alpha. If stuck, send them to "The word a die has never rolled".]
4. "Your model says student A with log odds +0.8, while for the Federalist papers most log odds were above +10. How sure should you be, and what would you check?" [Weak evidence: odds about 2 to 1; check leave-one-out accuracy on the known reports, look at which words carry the vote, compare with the hard case No. 55. If stuck, send them to "The verdict on the twelve".]
Transfer. "With only 3 reports per student instead of 20, would you rather use Naive Bayes or logistic regression, and why?" [Naive Bayes: strong assumptions learn faster from little data; logistic regression must fit many weights from few examples. Mention the curve on "Learning from a handful of papers".]
Closing. Ask them to say in three sentences what a generative model is, how it is fitted, and how it classifies. Tighten anything vague, and end.

SLIDES YOU CAN SEND THEM TO (exact titles): "The clue is in the small words", "The two dice, learned from 65 papers", "Bayes' rule turns the story around", "Weigh a paper", "The word a die has never rolled", "The verdict on the twelve", "Gaussian discriminant analysis", "Learning from a handful of papers".

HOW YOU LEAD.
- The plan is private. Never mention steps or the plan; talk about reports, words, dice and votes.
- Refer to slides only by their exact titles, never by number.
- Do not label an answer as a mistake; say what it leaves out.
- Open at once with a one-sentence frame and the first question. One question at a time, and wait. Two to four sentences per reply.
- Diagnose before explaining: ask a smaller question that exposes the gap. If they miss the same point twice, send them to a slide by its exact title with something to do there, then give a concrete hint. Never the answer itself.
- When they get one right, say in one sentence exactly what was right, then move on.
- Never state a number that is not in the facts; the lab reports are hypothetical, so invent no results for them.

HOUSE STYLE. No em-dashes and no arrow characters anywhere the student reads. Write mathematics in LaTeX between $ signs."""
dump({'lecture_id': 'generative_federalist', 'exercises': [{'id': 'unnamed_report', 'after_section': top['curve'], 'title': 'The unnamed lab report', 'mode': 'solve',
      'min_turns': 6, 'model': 'claude-sonnet-5', 'prompt': 'A lab report arrives with no name. The tutor walks you through building the model that would tell which of two students wrote it.', 'system_prompt': SYS}]},
     f'{REPO}/data/conversations/generative_federalist.json')
R = lambda t, u, n, s, kind='reading': {'title': t, 'url': u, 'kind': kind, 'required': False, 'note': n, 'slides': s}
dump({'items': [
    R('Mosteller and Wallace, Inference in an authorship problem (JASA, 1963)', 'https://doi.org/10.1080/01621459.1963.10500849', 'The original study: Bayes, function words, and the twelve disputed papers.', ['publius', 'verdict']),
    R('The Federalist Papers (Project Gutenberg #1404)', 'https://www.gutenberg.org/ebooks/1404', 'The full text the counts on these slides come from.', ['guess', 'small-words']),
    R('CS229 lecture notes: generative learning algorithms (Andrew Ng, Tengyu Ma)', 'https://cs229.stanford.edu/main_notes.pdf', 'GDA, Naive Bayes, Laplace smoothing and event models, in full.', ['story', 'bayes', 'gda', 'never-seen']),
    R('Ng and Jordan, On discriminative vs. generative classifiers (NeurIPS 2001)', 'https://papers.nips.cc/paper/2001/hash/7b7a53e239400a13bd6be6c91c4f6c4e-Abstract.html', 'Why the generative model learns faster from few examples, and when the discriminative one wins.', ['two-kinds', 'curve']),
    R('Reconstruction of the Mosteller and Wallace corpus (GitHub)', 'https://github.com/ariddell/corpora-mosteller-wallace-federalist', 'The papers and attributions, prepared for analysis.', ['publius']),
]}, f'{REPO}/data/references/generative_federalist.json')
print({q['id']: (q['after_section'], q['static_question']['correct']) for q in qs})
