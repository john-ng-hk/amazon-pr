#!/usr/bin/env python3
"""
Amazon-style Press Release & FAQ Generator
Working Backwards from the customer to generate a full PR/FAQ deck structure.

Usage:
    python pr_skill.py                        # interactive mode
    python pr_skill.py --brief "My idea..."   # one-liner brief
    python pr_skill.py --file brief.txt       # brief from file
    python pr_skill.py --output out.md        # save to file
"""

import argparse
import sys
import anthropic


SYSTEM_PROMPT = """\
You are an expert practitioner of Amazon's "Working Backwards" product development process.
You generate Amazon-style Press Release & FAQ (PR/FAQ) documents that force clear thinking
about what the product is, who it's for, and why it matters.

Writing rules you must follow without exception:
1. Write from a FUTURE perspective — it is 18 months from now. The idea is already reality.
   Write the vision as if it has already happened.
2. Every paragraph in the Press Release section must be exactly 3–4 sentences.
3. Avoid fat. Cut every word that does not earn its place. No filler, no buzzwords.
4. Write like a TV presenter broadcasting to millions who have ZERO prior knowledge of
   the product. Simple, punchy, compelling, intelligible.
5. Never use internal acronyms or function-specific jargon.
6. The Internal FAQ section is for business and execution questions — not product specs.
7. Problems must be listed in descending order of pain (worst problem first).
8. The Summary paragraph is the single most important paragraph in the entire document.
   Most people will only read this one. It must compel them to keep reading.
9. The Press Release body (Date through How to Get Started) must feel like ~1.5 pages.
"""

GENERATION_PROMPT = """\
Using the product brief below, generate a complete Amazon-style Press Release & FAQ document.

PRODUCT BRIEF:
{brief}

---

Output exactly the following sections, in this order, using these exact headers:

# [HEADING]
Write this as: [COMPANY] ANNOUNCES [SERVICE/TECHNOLOGY/TOOL] TO ENABLE [CUSTOMER SEGMENT] \
TO [BENEFIT STATEMENT]
Make it punchy and reader-friendly — not internal language.

## Sub-Heading
One sentence only. Who is the market, and what benefit do they get? Frame the announcement
from a slightly different angle than the heading.

## Date
Write as: CITY — [Projected Launch Date] — [Company], a [location] company, today launched
[brief description of what it is and what it does]. 3–4 sentences.

## Problem
The top 3–4 problems this product solves, ranked worst-first. No solution language allowed.
Make the reader feel the pain. Each problem is 1–2 sentences.

## Summary
THE MOST IMPORTANT PARAGRAPH. 3–4 sentences. Summarize the product and the benefit so
compellingly that someone who reads only this paragraph understands the entire value proposition
and wants to know more. This is your killer paragraph — spend the most effort here.

## Solution
Briefly describe how it works overall, then address each problem individually and show how
the product resolves it. 3–4 sentences.

## Quote from the Company
A crafted (not real) quote from a company founder or executive. It explains WHY the company
chose to tackle this problem and gestures at how the solution works. 3–4 sentences.
Format: "Quote text," said [Name], [Title] of [Company]. "Continuation of quote."

## How the Product Works
What does a customer actually do to start using it, and how does it work day-to-day?
Enough detail to give confidence it solves the problem. 3–4 sentences.

## Customer Quote
A realistic (not real) quote from a hypothetical customer. They describe their pain point
first, then how the product fixed it. Use a name, job title, and location to make it feel
real. 3–4 sentences.
Format: "Quote text," said [Name], a [job] in [city]. "Continuation."

## How to Get Started
One or two sentences. How easy is it to begin? End with a clear CTA and URL or access point.

---

# External FAQs

### Where do I get it?
URL or location where customers can access the product.

### How much does it cost?
Specific pricing model.

### How does it work?
Plain-language explanation from the customer's perspective.

---

# Internal FAQs

### Who is the customer?
Describe the end consumer with quantitative elements: geography, demographics, income
bracket, and estimated number of people in this segment.

### How many consumers have this problem?
High-level market sizing — this is the proxy for the size of the prize.

### How big is the TAM?
Drill into the segment. Is there a large enough group who cares enough? Quantify.

### Why does this problem need to be solved now?
A compelling timing argument grounded in customer need, market momentum, and competitive
landscape. Never a roadmap or resourcing answer.

### For how many consumers is this problem big enough to pay to solve it?
What portion of the TAM will actually spend money? Mix of quantitative and qualitative evidence.

### How much would they pay?
Specific price point, pricing rationale, and connection to customer value and TAM.

### What capabilities or constraints does the customer need to use this?
Access requirements, technical prerequisites, or real-world constraints that limit
who can actually use the product.

### What is the ROI of this project?
A P&L outline: team cost fully loaded, time to build, time to payback, units to break even,
gross margin per unit, cost per unit. Be specific about the numbers you know and flag
assumptions where you don't.

### What are the likely product specifications?
What the product is, how it works technically, and what it will take to build. Flag key
build risks.

### What is the flaw in the solution? What might disappoint the customer?
Be honest. Which problems does this solve well? Which does it not fully solve?

### How will consumers discover the product?
Go-To-Market strategy: channels, organic vs. paid, partnerships, which internal teams need
to be involved.

### Are there dependencies on other products or services?
Internal team dependencies, external APIs or platforms, legal or compliance requirements,
or third-party partnerships needed to launch.
"""


def gather_brief_interactively() -> str:
    """Gather product brief through guided questions."""
    print()
    print("=" * 62)
    print("  AMAZON-STYLE PR/FAQ GENERATOR")
    print("  Working Backwards from the Customer")
    print("=" * 62)
    print()
    print("Answer these questions. Press Enter to skip any you don't")
    print("know yet — the AI will make reasonable assumptions.")
    print()

    fields = [
        ("company",       "Company or team name"),
        ("product",       "What is the product or service?"),
        ("customer",      "Who is the target customer? (be specific)"),
        ("problems",      "Top 2–3 problems it solves"),
        ("solution",      "How does it solve them? (high-level)"),
        ("benefit",       "Single biggest benefit to the customer"),
        ("differentiator","What makes this different from alternatives?"),
        ("pricing",       "Pricing model"),
        ("url",           "Product URL or access point"),
    ]

    answers = {}
    for key, label in fields:
        raw = input(f"  {label}:\n  > ").strip()
        answers[key] = raw if raw else "(not specified)"
        print()

    brief = "\n".join(f"{label}: {answers[key]}" for key, label in fields)
    return brief


def generate(brief: str, model: str) -> None:
    """Stream the PR/FAQ document to stdout."""
    client = anthropic.Anthropic()
    prompt = GENERATION_PROMPT.format(brief=brief)

    print()
    print("=" * 62)
    print()

    with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print()
    print()
    print("=" * 62)


def generate_to_string(brief: str, model: str) -> str:
    """Generate the PR/FAQ document and return as a string."""
    client = anthropic.Anthropic()
    prompt = GENERATION_PROMPT.format(brief=brief)

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an Amazon-style Press Release & FAQ (Working Backwards)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--brief", "-b",
        metavar="TEXT",
        help="Product brief as inline text (skips interactive prompts)",
    )
    parser.add_argument(
        "--file", "-f",
        metavar="PATH",
        help="Path to a text file containing the product brief",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="PATH",
        help="Save output to this file instead of printing to stdout",
    )
    parser.add_argument(
        "--model", "-m",
        default="claude-opus-4-6",
        metavar="MODEL",
        help="Claude model to use (default: claude-opus-4-6)",
    )
    args = parser.parse_args()

    # Resolve brief
    if args.brief:
        brief = args.brief
    elif args.file:
        with open(args.file) as f:
            brief = f.read()
    else:
        brief = gather_brief_interactively()

    # Generate
    if args.output:
        print(f"Generating PR/FAQ with {args.model}...")
        content = generate_to_string(brief, model=args.model)
        with open(args.output, "w") as f:
            f.write(content)
        print(f"Saved to {args.output}")
    else:
        generate(brief, model=args.model)


if __name__ == "__main__":
    main()
