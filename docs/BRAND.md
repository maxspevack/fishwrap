# Fishwrap Brand Bible

**Scope:** the engine's storefront at fishwrap.org. Consumer publications (Daily Clamour, fishwrap.me, third-party forks) inherit the engine's capabilities, not its aesthetic.

---

## Preamble

One brand, two voice registers, one visual home.

**REFUSAL** is the posture: the broadsheet front page, the editor's mark built into the brand name, the membership line *the peasants scroll, the elite read*. **EDITOR** is the practice: the chair at the desk, the red pencil, the margin note that stays in effect. The reader walks in through REFUSAL because REFUSAL is the only door open. Once inside, the reader discovers EDITOR on the working surfaces. Those surfaces are reached by participating. The brand contains both.

Four locked calls:

**The wordmark is `Fishwra¶`.** The pilcrow is not a flanker, not an ornament. It IS the P. The pilcrow's morphology is a P with a doubled vertical stem, the medieval scribal mark for a new paragraph. The substitution rewards close looking the way the FedEx arrow does. Every appearance of the brand name carries the editor's mark literally embedded in it.

**The face is Libre Baskerville.** Free under SIL OFL, no procurement, no foundry license. Drawn for screen reading from the Baskerville lineage that anchors magazine mastheads. Variable weight axis; the wordmark sits at weight 700. The face's pilcrow has the closed-counter, double-stemmed shape the substitution requires.

**The mono face is iA Writer Mono.** Free under SIL OFL. Warmer than IBM Plex Mono and slightly humanist; reads as *typewriter at the editor's desk*, not as *terminal*. Used only for engine output: audit-log fragments, score deltas, edition metadata.

**No third face.** No sans. The voice differentiation between REFUSAL acquisition surfaces and EDITOR working surfaces comes from prose, not from a second body face. Libre Baskerville Regular sets the body on every register; iA Writer Mono sets engine output. Two faces, both free, no paid foundry.

**Production runs on extant tooling, not a generative model.** The wordmark, favicon, and OG card are produced from the live font using `fontTools` and ImageMagick. A brand whose thesis is *the algorithm you can read* cannot have its mark rendered by an opaque generative pipeline. The asset-generation script lives in the repo at `docs/static/brand/generate-assets.py` and is reproducible from source.

---

## 1. Mission and Vision

Fishwrap is for the readers who have already left.

The feed is not a medium; it is a posture, and the posture is over. The reader who arrives at this page has spent enough mornings staring at a thumb-shaped rectangle that scrolls without floor, and they are tired in a way no app has a remedy for. We do not propose moderation. We propose departure.

Our mission is to print the morning paper for the reader who has unplugged the wall. One edition a day. Eleven pages. A back page that says *the end*. The reader sets the policy in plain language; the engine sets the type. There is no recommendation surface. There is no inferred preference. There is no notification.

Our vision is a web in which the people who read are no longer confused with the people who scroll. The peasants scroll. The elite read. Fishwrap is the receipt for the exit, and the exit is real.

We do not measure your time on this page. We are not paid to. When the edition ends, go outside.

---

## 2. The Anxiety of the Thumbs Down

Every news aggregator has a thumbs-down button. Every news aggregator has a black box behind the button. The reader presses the thumbs-down on a celebrity divorce story and does not know whether they have just suppressed the celebrity, the divorce, the publication that ran the piece, the political coverage of the same celebrity in next week's edition, or the entire section the story sat under. The cost of feedback is opaque. The cost of opacity is silence. The reader stops pressing the button. The feed gets worse. The reader scrolls anyway.

The political-golf trap is the moat in plain speech. A reader who downvotes a Donald Trump golf story does not want to lose policy coverage of the Donald Trump administration. The algorithm does not distinguish between the two; the reader cannot ask it to. The thumbs-down is the half-gesture of a reader who has not been permitted to write a margin note. So the reader does not press the button. So the algorithm does not learn. So the feed circles back to the same celebrity and the same divorce and the same opaque consequence. This is not a UX problem. This is a category problem. Every aggregator on the open web operates this way because exposing the policy would expose the absence of one.

Fishwrap exposes the policy.

The Editor's Note replaces the thumbs-down because that is what editors write. *Penalty: Golf, −20.* *Boost: Executive Order, +20.* The note is a sentence, not a vote. The sentence is yours. It is named, dated, signed, and persisted; it stays in effect across editions until you strike it; and every story that fires it shows you which sentence fired and by how much. Mark it up. The edition obeys.

There is no recommendation surface because there is no anonymous editor. There is no inferred preference because every preference is a sentence the reader wrote. The thumbs-down is not redesigned; it is fired. The chair is yours.

---

## 3. Three reader-stakes

Three things the reader does, what stays in effect, and what the engine commits to. Concrete, verifiable inside the engine, not abstractions.

**The reader's daily act.** Open the proof. Read the edition. Write a margin note on any story that should have scored differently, or any pattern that should not have run, or any source that should run more often. The note is a sentence in plain English. The system files it as a policy and reports the file path. The act is the work.

**What stays in effect.** Every note the reader has written, with the date and the edition it was written against, named on a single audit page the reader can open at any time. Notes do not expire. Notes do not silently fall off when the engine updates. Notes are struck only when the reader strikes them; the strike is also a note, also dated, also filed. The policy file is the masthead.

**What the engine commits to.** Every story carries the score it received and the names of every policy that fired on it, in the order they fired, with the integer contribution of each. Every fired policy is the reader's, or it is named *default* and dated against the engine's last release. The engine never scores a story by a rule it cannot name. The audit log is the contract.

---

## 4. Persona and the two voice registers

Fishwrap speaks in two registers under one visual home. The registers are not a tonal range; they are two different voices firing on two different surfaces, and the rule is mechanical.

**REFUSAL register.** Broadsheet, declarative, slightly aristocratic without irony. It fires on acquisition surfaces: the home page, the README first viewport, social-share cards, the press kit, the masthead under the wordmark. Its job is to give the exhausted reader permission to leave the feed they already wanted to leave. The hill-defense sentence: *The peasants scroll. The elite read.* That sentence is the membership card. Any string in this register names a stance, not a feature. If a sentence in this register can be pasted into a Mailchimp template without modification, the sentence is wrong.

**EDITOR register.** Magazine-warm, second-person, instructive without being pedagogical. It fires on working surfaces: the audit log, the score breakdown, the policy editor, the Editor's Note composer, the edition metadata, the daily proof preview. Its job is to make the reader feel the chair they have just been promoted into. The hill-defense sentence: *Mark it up. The edition obeys.* Any string in this register addresses the reader as someone who has authority over the artifact in front of them. If a sentence in this register could be pasted into Linear's marketing site, the sentence is wrong.

Look up any string in the codebase. If it sits on a surface the reader has not yet earned, it is REFUSAL. If it sits on a surface the reader has reached by participating, it is EDITOR. The conversion event is §2.

What the brand does not do, in either register: it does not wink, it does not hedge, it does not narrate its own intentions, and it does not promise transformation. It states. It shows the working. It signs the masthead.

---

## 5. Taglines

Eight lines survive. The home for each is fixed; the rotation is not free.

**Acquisition surfaces (REFUSAL register).**

- *The algorithm you can read. The feed that ends.* Home page hero, README header, the press kit one-liner. The strongest line in the project. It is the door.
- *The peasants scroll. The elite read.* The masthead phrase, beneath the wordmark on the home page and on the Open Graph card. The membership card.
- *You did not quit the feed to find a better feed. You quit the feed.* The 404 page, the *what is this* explainer, the second viewport of the home page where the reader is deciding whether to scroll on. The line that closes the door behind the reader.
- *We do not measure your time on this page. We are not paid to.* The footer of every edition. The mission in the negative.

**Working surfaces (EDITOR register).**

- *Become your own Editor-in-Chief. We built the presses for you.* The onboarding page, the first-edition welcome. Identity claim and capability claim in one line.
- *Edited by you.* The signature line under the wordmark on every edition page. The lockup mate.
- *Sign the masthead. Run the press.* The call-to-action on the policy editor, the surface where the reader writes their first margin note.
- *We don't take thumbs. We take margin notes.* The header of the §2 explainer on the home page, and the empty-state of the Editor's Note composer.

Retired and not to return: *Finiteness is the new luxury* (X-is-the-new-Y tell), *Your news. Your rules. No more algorithmic anxiety.* (three commodity phrases stapled), *It's not magic, it's engineering.* (the category trap in one sentence), *The internet is a firehose of noise. We built a very precise nozzle.* (machinery-as-metaphor, off-register), *Stop scrolling. Start reading. Start thinking.* (imperatives in triplicate; reads as a wellness app).

---

## 6. Visual Language

The visual home is one. The wordmark, the glyph, the palette, the type stack, and the layout grammar are constant across the property; only the voice shifts between registers.

### 6.1 Wordmark

The wordmark is **`Fishwra¶`**: the word *Fishwrap* with the pilcrow taking the place of the closing P. The substitution is not decorative. The pilcrow is the editor's mark for a new paragraph; the brand name carries that mark literally embedded in it. Reading the wordmark out loud, the reader still says *Fishwrap*. Reading it on the page, the reader sees the editor at work.

The wordmark is set in **Libre Baskerville Bold** (variable weight axis at 700), mixed case, no brackets, no monospace, no all-caps, no flanking ornament. Optical kerning. Tracking at the default. The pilcrow renders at the same weight, color, and baseline as the surrounding letters; its descender sits below the baseline by approximately one quarter of the cap height.

The wordmark is rendered as a path-only SVG at `docs/static/images/fishwrap_logo.svg`. The SVG embeds the glyph outlines directly: no `@font-face`, no font dependency, no client-side text rendering. The file scales infinitely and renders identically in browsers, ImageMagick, librsvg, and OS previewers.

On the home page and the Open Graph card, the wordmark lockup carries a second line beneath it: a 1px Margin Ink rule the width of the wordmark, and under the rule, in **Libre Baskerville Italic** at 22% the cap height of the wordmark, the literal phrase *The peasants scroll. The elite read.* On every edition page, the same lockup carries the phrase *Edited by you.* under the rule instead. The rule between wordmark and phrase is the masthead bar; it is not a decorative element.

The bare `Fishwrap` (with a normal P, no pilcrow, no rule, no phrase) is permitted in **running prose only**: body copy, link text, sentence-internal references. It is not permitted as a logo on any surface.

The retired marks: `— Fishwrap —` (em-dash-flanked; retired before ship because the em-dash has become the typographic tell of AI-generated text), `[FISHWRAP]` in IBM Plex Mono (GLASS BOX, retired), and the earlier grey monospace with orange cursor-block (Digital Origami, retired before that). None return.

### 6.2 Glyph and favicon

The glyph is a bare **pilcrow `¶`** set in Libre Baskerville Bold, centered in a square field of Smoke Cream, rendered in Refusal Black. The pilcrow is the typographic mark for a new paragraph; the favicon claims *we are a new paragraph from the algorithm*.

Asset set (under `docs/static/images/`):

- `favicon.svg`: path-only SVG, the canonical glyph. Modern browsers prefer this.
- `favicon-180.png`: Apple touch icon (iOS).
- `favicon-192.png`: Android Chrome and manifest.
- `favicon-512.png`: large manifest icon.
- `/favicon.ico` (at site root): multi-resolution ICO containing 16, 32, and 48 pixel bitmaps. Legacy-browser fallback only; modern browsers ignore this when the SVG is declared.

At 16×16 the pilcrow's internal detail compresses. The bitmap is readable as the editorial mark but loses the double-stem character that's visible at 32+. This is acceptable; the favicon is a recognition aid, not a first-impression generator.

### 6.3 Palette

Seven colors. Five inherit from REFUSAL; two cross over from the EDITOR draft for the editorial-chrome and metadata layers.

| Token | Hex | Role |
|---|---|---|
| Smoke Cream | `#EBE6DC` | Field. Page background, the paper the broadsheet is printed on. |
| Refusal Black | `#0E0D0C` | Body, wordmark, pilcrow, rules at full weight. Near-true black; broadsheet contrast against Smoke Cream. |
| Cardinal Red | `#9C1B14` | The editor's pencil. Positive score deltas, the dateline, the page-end ornament, the *added* mark when the reader has imposed emphasis. Used inline at body weight; permitted at masthead size on the dateline and the page-end ornament only. |
| Lead | `#3B3A39` | Secondary text on REFUSAL surfaces. The lead in a No. 2 pencil. |
| Bone | `#D9D2C2` | Section dividers, the back-page mark. |
| Folio Gold | `#A8884A` | Section heads and edition number on EDITOR surfaces; the masthead bar when the edition number is printed beside it. One element per page maximum. |
| Margin Ink | `#5C5247` | Audit-log metadata, the masthead bar on non-edition surfaces, the rule beneath the wordmark, the pencil-grey that wrote the margin note before the red one. |

Cardinal Red is the only red. There is no second red, no Boost Red, no Penalty Red. The red codes for *added* in the editor's pencil convention; the absence of red codes for *struck*. A struck phrase is rendered with a Refusal Black strikethrough at body weight; no green appears anywhere on the brand. Green was a financial-ticker convention and the brand is not a financial ticker.

Banned: any near-white background colder than Smoke Cream; any blue; any green; any neon; any orange; any salmon or coral; any vibrant accent. Cold whites read as software. The newsroom is warm because paper is warm. Off-palette colors require explicit justification and are not permitted on storefront surfaces.

### 6.4 Type stack

Two faces, no third.

- **Libre Baskerville.** Variable weight axis. Weight 700 for the wordmark and section heads; weight 400 (Regular) for body copy on every surface; Italic at weight 400 for tagline lockups and editorial emphasis. SIL OFL, free, self-hosted from `/docs/static/fonts/`.
- **iA Writer Mono.** Regular and Italic for audit-log fragments, score deltas, edition metadata, policy file paths, and any string the engine emitted. SIL OFL, free, self-hosted.

No sans. No second serif. No Inter, no IBM Plex Mono, no GT Sectra, no Söhne, no monospace face other than iA Writer Mono. The voice differentiation between REFUSAL and EDITOR registers comes from prose, not from a body face.

System-stack fallbacks are permitted only where the licensed face cannot load: `Georgia, "Times New Roman", serif` for Libre Baskerville; `ui-monospace, SFMono-Regular, Menlo, monospace` for iA Writer Mono.

### 6.5 Layout grammar

The page is a broadsheet grid on REFUSAL surfaces and a magazine spread on EDITOR surfaces. The grid is constant: twelve columns, a generous outer margin, a vertical rhythm tied to the Libre Baskerville body cap height. The column allocation differs by register. REFUSAL surfaces give the headline six to eight columns and the deck two to three; EDITOR surfaces give the working content seven to nine columns and reserve the right rail for audit-log fragments at three columns.

Rules: a 1px Margin Ink rule at column-1 of every content block on EDITOR surfaces. A 1px Refusal Black rule under every REFUSAL headline at the width of the headline. Audit-log fragments are rendered in iA Writer Mono at 13/20 in a Margin Ink-bordered well. Score deltas appear inline using Cardinal Red for positive values and Refusal Black strikethrough for struck values; the integer sign (+/−) is always shown. Edition timestamps are absolute (ISO-8601 UTC with a localized parenthetical), never relative.

Folio Gold fires on the section head and the edition number, and on the masthead bar between them. Nowhere else.

### 6.6 What this brand is not

Fishwrap's brand is the engine's brand and the reader's chair. It is not the brand of any publication built on the engine. Daily Clamour and any third-party fork each select their own visual identity and inherit only the engine's capabilities: exposing the score breakdown, reading the audit log, persisting the reader's notes. Not the aesthetic. A publication built on Fishwrap that adopts Fishwrap's wordmark, palette, or type stack is not endorsed by Fishwrap and is asked to change.

---

## 7. Asset Production

Brand assets are produced from the live font using `fontTools` and ImageMagick. The production script lives in the repo at `docs/static/brand/generate-assets.py` and is reproducible from source.

### 7.1 Wordmark: `Fishwra¶`

Source font: `LibreBaskerville-variable.ttf` (committed under `docs/static/fonts/`), weight axis instanced at 700.

Method: open the variable font with `fontTools.ttLib.TTFont`, instance at weight 700 via `fontTools.varLib.instancer.instantiateVariableFont`, walk the characters of the string `Fishwra¶`, extract each glyph's outline via `fontTools.pens.svgPathPen.SVGPathPen`, position by advance width, and emit a single SVG with a coordinate-space flip from font-units-y-up to SVG-y-down.

Output: `docs/static/images/fishwrap_logo.svg`. Path-only, no `@font-face`, no font dependency at render time. The SVG renders identically in any conforming renderer.

### 7.2 Glyph and favicon: bare `¶`

Source font: same.

Method: extract only the pilcrow glyph (`U+00B6`) via the same path-extraction pipeline, compute the glyph's tight bounding box via `fontTools.pens.boundsPen.BoundsPen`, center the glyph in a square canvas with 60% additional padding around the larger dimension, emit as path-only SVG.

PNG rasterizations are produced via ImageMagick at every size in `{16, 32, 48, 64, 96, 128, 180, 192, 256, 512}`. The 16, 32, and 48 pixel rasters are assembled into a multi-resolution `favicon.ico` for legacy fallback.

Outputs:

- `docs/static/images/favicon.svg`
- `docs/static/images/favicon-180.png` (Apple touch icon)
- `docs/static/images/favicon-192.png` (Android manifest)
- `docs/static/images/favicon-512.png` (manifest)
- `docs/favicon.ico` (multi-resolution, served from the site root for legacy fallback)

### 7.3 Open Graph card

Canvas: 1200×630 pixels, Smoke Cream field.

Method: render the wordmark SVG to an intermediate PNG at the OG card's target height (150 pixels), then composite onto the Smoke Cream canvas via `magick composite` at top-center with 100 pixels of top padding. Annotate the tagline beneath in Libre Baskerville Italic at 26pt Margin Ink (centered, 260 pixels from top). Draw a 1px Margin Ink rule between wordmark and tagline. Annotate a placeholder edition line in iA Writer Mono Regular at 22pt Refusal Black (centered, 80 pixels below center). Annotate `fishwrap.org` in iA Writer Mono Regular at 16pt Margin Ink (bottom-right, 56px from each edge).

Output: `docs/static/images/og-card.png` at 1200×630.

The numbers in the edition line are placeholders. Templating real per-share values is a future job for a Liquid filter or a build step; the v1 card ships with the placeholder.

---

## Appendix A: Voice-register surface map

A future contributor looking at any string in the codebase should be able to determine its register from this table. The rule is mechanical: surface determines register.

| Surface | Register | Why |
|---|---|---|
| Home page hero, second viewport, footer | REFUSAL | Front door. The reader has not yet detoxed. Permission to leave is the only verb a Level-3 nervous system has the energy for. |
| README header and first paragraph | REFUSAL | The repo is an acquisition surface too. A developer landing here is a reader, not a user. |
| Open Graph cards, press kit, social posts | REFUSAL | Surfaces seen before the reader has clicked through. The masthead is the door. |
| 404 page, *what is this* explainer | REFUSAL | Re-entry surfaces. Re-state the stance, not the feature set. |
| §2 explainer block on the home page | HYBRID | The conversion event modeled as prose. Starts REFUSAL on the felt problem, transitions to EDITOR on the remedy. |
| Onboarding, first-edition welcome | EDITOR | The chair has been claimed. The reader is now in the role. |
| Daily edition pages | EDITOR | The working artifact. The reader is reading their own paper. |
| Audit log, score breakdown, policy file viewer | EDITOR | The contract surface. The engine is showing the working; the voice addresses the reader as the editor of record. |
| Editor's Note composer, policy editor | EDITOR | The act surface. The reader is writing the masthead. |
| Edition metadata, timestamps, file paths | EDITOR (mono) | Set in iA Writer Mono. Reads as the editor's typewriter, not the algorithm's log. |
| Error states on working surfaces | EDITOR | The reader is still in the chair. Failure is named at the editor's desk, not at the front door. |
| Documentation (CLI reference, configuration reference) | EDITOR | The reader is at the working surface by definition. |
| Status page, uptime page | REFUSAL | A reader checking status is checking whether the door is open. State the stance, then the numbers. |
