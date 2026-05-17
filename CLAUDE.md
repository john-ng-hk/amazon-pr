# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

A CLI skill that generates Amazon-style Press Release & FAQ (PR/FAQ) documents using the "Working Backwards" methodology. Given a product brief, it produces a full structured deck — Press Release + External FAQs + Internal FAQs — using Claude as the generation engine.

Reference: `Amazon Style Press Release.pdf` contains the source methodology and examples.

## Setup

```bash
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
```

## Running the skill

```bash
# Interactive mode (guided questions)
python pr_skill.py

# One-liner brief
python pr_skill.py --brief "My product idea..."

# Brief from file
python pr_skill.py --file brief.txt

# Save output to markdown file
python pr_skill.py --output result.md

# Different model
python pr_skill.py --model claude-sonnet-4-6
```

## Architecture

`pr_skill.py` is a single-file CLI with three logical parts:

1. **Brief gathering** (`gather_brief_interactively`) — 9-question guided prompt that collects company, product, customer, problems, solution, benefit, differentiator, pricing, and URL.

2. **Generation** (`generate` / `generate_to_string`) — Calls Claude with a structured system prompt (writing rules from the PDF) and a generation prompt that specifies all 14 required sections in exact order. `generate` streams to stdout; `generate_to_string` returns the full string for file output.

3. **CLI** (`main`) — `argparse` entry point wiring `--brief`, `--file`, `--output`, and `--model`.

## PR/FAQ Structure (from the PDF)

**Press Release** (write from 18 months in the future; ~1.5 pages; each paragraph 3–4 sentences):
- Heading — `[COMPANY] ANNOUNCES [TOOL] TO ENABLE [CUSTOMER] TO [BENEFIT]`
- Sub-Heading — one sentence, market + benefit
- Date — launch announcement paragraph
- Problem — top 3–4 pains ranked worst-first, no solution language
- Summary — the most important paragraph; must stand alone
- Solution — how it fixes each problem
- Company Quote — fake spokesperson quote on the why
- How the Product Works — customer onboarding + day-to-day
- Customer Quote — fake customer with name/job/city
- How to Get Started — CTA + URL

**External FAQs**: where to get it, price, how it works (customer perspective).

**Internal FAQs** (business/execution only, not product spec): customer definition, market size, TAM, timing rationale, willingness to pay, access constraints, ROI/P&L, product specs, known flaws, GTM strategy, dependencies.

## Key Writing Principles (enforced via system prompt)

- Future tense — write as if the product already launched 18 months from now
- TV presenter voice — zero assumed knowledge, simple and compelling
- No fat — every word earns its place; no jargon or internal acronyms
- Problems ranked by pain severity (worst first)
- Internal FAQs = business thinking, not engineering specs
