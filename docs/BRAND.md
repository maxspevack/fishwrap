# Digital Origami (Brand Bible)

## 1. Brand Mission & Vision
**Mission:** To empower individuals to reclaim agency over their information diet by providing transparent, auditable, and customizable news engines.
**Vision:** A future where the "feed that ends" is the norm, and every reader is their own Editor-in-Chief, free from algorithmic anxiety.

---

## 2. Core Philosophy: The Origami Paradox & The Anxiety of the Thumbs Down

Fishwrap stands on a deliberate paradox: we apply cutting-edge engineering to the humble, ephemeral nature of "fishwrap" (newsprint). Our inspiration is rooted in Neal Stephenson's "The Diamond Age," where a curated newspaper is a sign of societal advancement.

*   **The Problem (The Anxiety of the Thumbs Down):** Modern algorithmic feeds (Google News, social media) create fear. Users are afraid to give feedback because the "black box" consequences are opaque and potentially catastrophic. A "thumbs down" on a celebrity article might silence an entire political topic.
*   **The Fishwrap Solution (Granular Consent):** We don't ask for "thumbs down." We ask for an "Editor's Note." Our system empowers users with transparent rules: "Penalty: 'Golf' (-20). Boost: 'Executive Order' (+20)." This exposes the logic, makes it reversible, and restores agency.

---

## 3. Core Principles (The Pillars of the Glass Box)

*   **Transparency (The Glass Box):** Every decision is auditable. Trust through clarity.
*   **Agency (Granular Consent):** Users curate their reality without fear.
*   **Intentionality (The Anti-Feed):** Finiteness is a feature, not a limitation. Quality over infinite scroll.
*   **Empowerment (Editor-in-Chief):** The user defines their news, their way.

---

## 4. Persona & Tone of Voice: The Enlightened Architect (with a Knowing Wink)

Fishwrap.org is the voice of an experienced architect who, having mastered complex systems, now delights in revealing their elegant simplicity. We speak with:

*   **Intelligence & Insight:** Understanding the problem, offering thoughtful solutions.
*   **Empowerment & Respect:** Guiding users as capable collaborators.
*   **Transparency & Directness:** Demystifying complexity, making the "magic" visible.
*   **Confidence & Vision:** Pioneering a better way, articulating a bold vision for the future of news.
*   **Practicality & Action:** Providing tools for immediate implementation.
*   **Whimsy & Engagement:** Using metaphors, clever microcopy, and subtle visual cues to make the experience enjoyable and memorable.

**Tone:** Authoritative but never Arrogant. Principled but never Preachy. Evocative but Grounded. Direct, concise, and infused with a dry, witty humor.

---

## 5. Key Messages & Taglines

*   "Fishwrap: The algorithm you can read. The feed that ends."
*   "Take back control of your news. It's not magic, it's engineering."
*   "Your news. Your rules. No more algorithmic anxiety."
*   "Finiteness is the new luxury."
*   "Stop scrolling. Start reading. Start thinking."
*   "Become your own Editor-in-Chief. We built the presses for you."
*   *"The internet is a firehose of noise. We built a very precise nozzle. Wrap it up, read it, throw it away."*

---

## 6. Visual Language: The Glass Box

Every news aggregator on the open web hides what your interactions do. The opacity is the product. Fishwrap shows what your interactions do, lets you edit the policy behind them, and persists the edit. That is the only category difference that matters. The storefront's job is to be the working proof.

fishwrap.org's chrome IS the engine's output. Audit-log fragments, score breakdowns, policy decisions, and edition metadata are rendered as the page's actual furniture — not as illustrations of the engine, but as samples from it. The site is a working specimen of what every publication built on Fishwrap can choose to expose.

### 6.1 Wordmark

The wordmark is `[FISHWRAP]`. The brackets are part of the mark. They assert that Fishwrap is one element in a pipeline — input on the left, output on the right. The mark is set in IBM Plex Mono Bold at all caps with -1% letter tracking. An inline lowercase variant `[fishwrap]` is permitted in running prose. No other variants are sanctioned.

The previous wordmark — `FISHWRAP` in grey monospace with an orange cursor-block — is retired as of this revision.

### 6.2 Glyph and Favicon

A single opening square bracket `[`, set in IBM Plex Mono Bold with thickened terminal serifs for legibility at favicon size, centered in a 64×64 field of Audit Paper, rendered in Decision Ink. The empty bracket is the mark; nothing is enclosed inside it.

### 6.3 Palette

| Token | Hex | Use |
|---|---|---|
| Audit Paper | `#FAFAF7` | Backgrounds, page field |
| Decision Ink | `#111418` | Primary text, wordmark, rules |
| Boost Red | `#D94F3A` | Positive editorial scores, added emphasis |
| Penalty Green | `#2E7D5B` | Negative editorial scores, struck-through emphasis |
| Margin Grey | `#8C8478` | Metadata, dividers, secondary text |

Red codes for *added*; green codes for *removed*. This is the convention of an editor's pencil, not a financial ticker. Off-palette colors require explicit justification and are not permitted on storefront surfaces.

### 6.4 Typography

Two registers, no third:

- **IBM Plex Mono** (weights 400 / 600 / 700) for the wordmark, headlines, code, audit-log fragments, edition metadata, and any chrome that derives from engine output.
- **Inter** (weights 400 / 500 / 600) for body prose, longform documentation, and anything written by a human about the engine.

Both faces are SIL OFL. Both are self-hosted from `/docs/static/fonts/`. No Google Fonts loader. No fallback web faces beyond the system stack (`ui-monospace, SFMono-Regular, Menlo, monospace` for mono; `-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif` for body).

### 6.5 Layout Grammar

The page is a left-rule grid. A 1px Margin Grey rule at column-1 of every content block; a matching rule under every section heading. Audit-log fragments are rendered in Plex Mono at 13/20 with the Margin Grey rule treated as a frame element. Score deltas appear inline using Boost Red and Penalty Green; the integer sign (+/−) is always shown. Edition timestamps are absolute (ISO-8601 UTC with a localized parenthetical), never relative.

### 6.6 Voice

The engine's voice on fishwrap.org is declarative and log-shaped. Sentence fragments are acceptable when they parallel the structure of a log line. Every quantitative claim is auditable inside the artifact that makes the claim. No taglines that promise transformation; the storefront shows the mechanism instead.

Examples:

- *"This article scored +47. Three policies fired. Two were yours."*
- *"Forty-three feeds polled. Two failed. The log is here."*
- *"Mount a config. Run the container. Read the log."*

### 6.7 What This Brand Is Not

Fishwrap.org's brand is the engine's brand. It is not the brand of any publication built on the engine. Daily Clamour, fishwrap.me, and third-party forks each select their own visual identity and inherit only the engine's *capabilities* — reading the score breakdown, exposing the audit log, persisting editor preferences — not its aesthetics.

---

## 7. Generative Prompts (Brand Assets)

Three prompts, all tuned for Google AI Studio / Imagen / Gemini. Each asset must reproduce the locked palette and the locked type stack. Use the negative-prompt clauses verbatim; without them the model will pull toward the legacy "Digital Origami" semantics that this revision retires.

### 7.1 Wordmark — `[FISHWRAP]` lockup

```text
Render a typographic wordmark on a square canvas.

Text: the literal string [FISHWRAP] including both square brackets, in all
capitals, set in IBM Plex Mono Bold. Letter tracking -1%. The brackets are
part of the mark and must be rendered at the same weight and color as the
letters; they are flush with the F and the P with one mono-character of
internal padding on each side.

Color: Audit Paper background, hex #FAFAF7. Wordmark in Decision Ink, hex
#111418. No other colors.

Composition: the wordmark is horizontally and vertically centered, occupying
approximately 60% of the canvas width. No tagline, no underline, no
decorative rule, no background texture, no shadow, no gradient, no
illustration. Flat, ink-on-paper.

Negative prompt: no fish, no origami, no folded paper, no gears, no cogs,
no blueprint aesthetic, no patent-drawing illustration, no cursor block,
no blinking cursor, no terminal frame, no orange accent color, no salmon,
no coral, no deep ocean blue, no Neo-Victorian motif, no Diamond Age
reference, no steampunk, no newspaper masthead ornament, no decorative
serif, no script face, no logotype mascot, no character.

Output: SVG vector and a 2048×2048 PNG at 300dpi.
```

### 7.2 Glyph / Favicon — opening bracket

```text
Render a square 64×64 pixel glyph for use as a favicon and app icon.

Subject: a single opening square bracket character "[" centered in the
canvas, rendered in IBM Plex Mono Bold. The bracket stem is approximately
1.3 times the default Plex Bold stem weight to maintain legibility at
16×16 pixels. The bracket's top and bottom terminal serifs are slightly
thickened for the same reason. Visual capital height is approximately 44
pixels in the 64-pixel field.

Color: Audit Paper background, hex #FAFAF7. Bracket in Decision Ink, hex
#111418. No other colors.

Composition: the bracket is centered both horizontally and vertically. The
bracket encloses nothing — its interior is the bare background. The mark
is the empty bracket itself.

Negative prompt: no fish, no origami, no character inside the bracket, no
content enclosed by the bracket, no second bracket, no underscore, no
cursor block, no orange, no salmon, no coral, no gradient, no shadow, no
3D effect, no embossment, no decorative serif beyond the locked Plex
terminal-serif shape, no script, no illustration, no rounded corners on
the bracket itself.

Output: SVG vector, 64×64 PNG, 16×16 PNG, 32×32 PNG, 180×180 PNG (Apple
touch icon).
```

### 7.3 Open Graph card template

```text
Render a 1200×630 pixel Open Graph social-share card.

Background: Audit Paper, hex #FAFAF7.

Top-left, with 64px padding from both edges: the wordmark [FISHWRAP] in
IBM Plex Mono Bold at 64pt, Decision Ink (#111418).

Beneath the wordmark, separated by 32px of vertical space: a thin 1px
horizontal rule in Margin Grey (#8C8478), 240px wide, left-aligned.

Centered vertically below the rule, in IBM Plex Mono Regular at 28pt
Decision Ink: a single line of placeholder audit-log syntax styled to
look like real engine output, in the form:

    edition 0142 · 6 sections · 41 articles · +12 net score

The middle dots (·) are Margin Grey; the rest is Decision Ink. The +12
is rendered in Boost Red (#D94F3A). The numbers are placeholders; the
final asset will template-substitute real values per share.

Bottom-right, with 64px padding from both edges, in Inter Regular at
18pt Margin Grey: the literal text "fishwrap.org".

Composition: severe left alignment, generous negative space, log-shaped
rhythm. The card reads as a fragment from the engine's own output, not
as a marketing asset.

Negative prompt: no fish, no origami, no gears, no blueprint, no patent
drawing, no cursor block, no orange, no salmon, no coral, no photograph,
no illustration, no person, no character, no mascot, no gradient, no
texture, no paper grain effect, no shadow, no 3D, no skeuomorphism, no
newspaper masthead ornament.

Output: PNG 1200×630 at 72dpi, and an editable SVG with the audit-log
line marked as a text element for templating.
```
