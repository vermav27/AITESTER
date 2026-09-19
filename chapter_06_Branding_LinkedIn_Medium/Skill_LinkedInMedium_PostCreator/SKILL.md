---
name: Skill_LinkedInMedium_PostCreator
description: >-
  Turns a title, rough bullet points, notes, or an image reference into a complete, ready-to-post content pack in Vineet Verma's QA brand voice: 3 controversial hooks, a LinkedIn post (Hook, Story, Offer), an X/Twitter-style tweet-card image prompt for LinkedIn using his headshot, a full Medium article, and a cyberpunk Medium header image prompt. Use this skill whenever Vineet shares a post idea, topic, title, bullet list, screenshot or reference image and wants content, even if he only says "make a post on this", "write content", "here is my next idea", "LinkedIn and Medium", or "give me hooks", or pastes a topic about QA, software testing, manual testing, test automation, Playwright, Salesforce, CI/CD, AI in testing or QA careers. Also use it to redo or regenerate any single piece of a pack (just the hooks, just the post, just one image prompt).
---

# Vineet's QA Content Engine

Vineet Verma is a QA Lead (10+ years, based in Delhi) building a personal brand on LinkedIn and Medium. He hands you a raw idea: a title, messy bullet points, voice-typed notes, or an image. You hand back one **content pack** with five pieces:

1. Three controversial hooks
2. A LinkedIn post (Hook → Story → Offer)
3. An image prompt for LinkedIn: an X/Twitter-style dark-mode post card with his photo
4. A Medium article
5. An image prompt for the Medium header, in a cinematic cyberpunk style

All five pieces share one hook, one set of numbers and one idea. That consistency is the point. A reader who sees the LinkedIn post, then the card, then the Medium article should recognise the same promise each time, like one campaign.

The approved gold-standard pack is in `references/example-pack.md`. When anything in this skill is ambiguous, do what that pack does.

## Personal settings

Every piece reads from this table. Edit it here if anything changes.

| Setting | Value |
| --- | --- |
| Display name | Vineet Verma |
| Handle on the X-style card | @vineetvermaqa (his LinkedIn slug; replace it if he gives you a real X handle) |
| Headshot | His own photo. He attaches it to the image generator himself, so always remind him. |
| LinkedIn | linkedin.com/in/vineetvermaqa |
| "Fail" highlight (the threat phrase) | Red #F4212E |
| "Pass" highlight (the way-out phrase) | Green #00BA7C |
| Default teaching stack | TypeScript + Playwright |
| Positioning line | The QA who decides what ships |

## Read before writing

1. `references/brand-voice.md`: read it **every time**. It holds the fact sheet (the only personal claims you may make), the voice rules, the banned words and the client-naming rules.
2. `references/example-pack.md`: read it the first time this skill is used in a conversation. It shows his raw input, the decisions made on it, and the full approved output.
3. The spec for each piece, before writing that piece:
   - `references/hooks.md` (piece 1)
   - `references/linkedin-post.md` (piece 2)
   - `references/image-prompts.md` (pieces 3 and 5)
   - `references/medium-article.md` (piece 4)

## Step 1: Read the input

His inputs come in a few shapes. Handle each one like this:

| What he gives you | How to treat it |
| --- | --- |
| A title only | Build the argument yourself from solid QA practice and his proof points. Use the step count the title promises, or 3 moves if it promises none. Any personal story you can't source from the fact sheet becomes a `[placeholder]`. |
| A title plus bullets | The bullets are **his advice**. Keep every instruction and number he gave (for example "10 exercises a day" or "4–5 projects"). Fix the grammar and reconcile numbers that don't add up. If the title promises N steps and he gave fewer bullets, split compound bullets and add the missing steps from his real experience. Then tell him which steps you added. |
| Notes, voice-typed text or a ramble | Pull out the claims, numbers and steps, then treat them like bullets. His notes are often voice-typed, with phrases like "in this case" or "he should"; turn them into clean second-person advice. |
| An image | First work out what kind of image it is. **Someone else's post or screenshot**: use it for topic and format inspiration only, and never reuse their lines, stats or signatures. **A tweet-card screenshot**: this is a format request, so use the X-style card spec. **His headshot**: this is the avatar, so remind him to attach it. **A slide, whiteboard or diagram**: read its content as bullets. |
| His own draft hooks | They show the heat level he wants. Keep that heat, rewrite them into his brand voice, and strip banned words (his drafts often contain "journey"). |

Then decide these before drafting:

- **Pillar**: which of the five content pillars in `brand-voice.md` this belongs to.
- **The one idea**: one sentence. If you can't write it, the pack will wander.
- **Step count N**: exactly what the title promises. If it promises nothing, use 3 moves.
- **Deadline window**: match it to the plan's length. A 3-month plan becomes "90 days", even if his draft hook said "2 months". Mention the change in your opening line.
- **Proof anchor**: the fact from the fact sheet that makes him credible on this topic, for the Setup.
- **"Next year"**: deadline hooks use today's year + 1 (in 2026, "2027 is your last year as...").

## Step 2: Build the spine

Write these six beats once, before any piece. Every piece is cut from the same spine.

1. **Hook**: a threat plus a condition, in 2 lines. The condition ("unless...") is the way out.
2. **Setup**: 1–2 real proof points, first person, from the fact sheet.
3. **Tension**: why most people fail. Give 3 failure modes; the LinkedIn post compresses them into 2 lines.
4. **Turn**: the N steps. Each one starts with a verb and carries a number, a tool or a rule.
5. **Lesson**: a hopeful reframe. The controversy resolves into encouragement.
6. **Offer**: exactly one. The default is a PS question ending in "so no judgment here".

**The heat curve.** Keep the hook hot, the body calm and generous, and the close kind. The controversy earns the click, the specific body earns the follow, and the kind PS earns the comment. A post that stays angry all the way through reads like fear-selling. That is the opposite of "the QA who decides what ships": a calm, experienced person who has seen hundreds of releases and is telling you the truth.

## Step 3: Write the five pieces, in order

Write in this order: hooks, then LinkedIn post, then card prompt, then Medium article, then Medium prompt. The post fixes the exact wording, the card lifts its hook from the post, and the article expands the same spine.

- **Piece 1, hooks**: always three, each a different type (A deadline, B identity flip, C evidence from his real numbers). Mark which one you used. Line 1 is at most 15 words. Every hook must pass the defensibility test in `hooks.md`.
- **Piece 2, LinkedIn post**: 150–300 words, delivered in a ` ```text ` block, with → arrows for steps, no emojis or bold, a PS sign-off, and 3–5 hashtags. The full spec is in `linkedin-post.md`.
- **Piece 3, LinkedIn card prompt**: a 1:1 dark-mode X post card. It carries 3 text blocks of at most 30 words in total, the threat phrase in red and the way-out phrase in green, and his headshot as the avatar. Put 2–3 sentences of notes before the prompt. The full spec is in `image-prompts.md`.
- **Piece 4, Medium article**: 1,000–1,800 words. It has a title, subtitle and tags; an opening with the hook; sections for setup, tension, the N-step formula (with one table, one code block and one list), and "What I'd do if I started tomorrow"; then a pull quote, the offer and his bio. The full spec is in `medium-article.md`.
- **Piece 5, Medium header prompt**: a 16:9 cyberpunk scene with a split composition (old way on the left, new way on the right), a figure seen from behind, and no readable text. `image-prompts.md` has a topic-to-metaphor table.

## Step 4: Check, then send

Run the final check below. If code execution is available, also lint the post and the article. Save each to a temporary file first, then run:

```bash
python scripts/lint_content.py linkedin post.txt
python scripts/lint_content.py medium article.md
python scripts/lint_content.py card card_prompt.txt
```

Fix every FAIL. Fix a WARN unless you have a clear reason not to.

## Output template

Use this exact shape. It is the shape of the approved pack.

````
[1–2 sentences: what the pack is built on, plus any change you made to his wording or numbers and why.]

## Three controversial hooks

1. **"[Hook A: deadline, 2 lines as one quote]"** This is the one I used in the post and the image.
2. **"[Hook B: identity flip]"**
3. **"[Hook C: evidence from his real numbers]"** [One clause on why this is the most "him" of the three.]

## LinkedIn post

```text
[The full post]
```

## LinkedIn image prompt (X-style card)

[2–3 sentences: attach your headshot; the handle used; the red/green color logic.]

```
[Card prompt]
```

## Medium article

**Title:** [Title]

**Subtitle:** [Subtitle]

**Tags:** [5 tags]

---

[Article body with ### section headings]

---

## Medium header image prompt (cyber)

```
[Cyber prompt]
```

[Closing, 1–2 sentences: any placeholders or facts to confirm before posting, and at most one question.]
````

Deliver the pack in the chat reply, not as a file. He copies each piece straight into LinkedIn, Medium and his image tool. If he asks for a document, Word file or PDF, use the matching tool or skill for that format.

## Rules that protect the brand

These rules outrank everything else, because a brand built on evidence breaks the first time a claim doesn't hold up.

1. **Personal facts come only from the fact sheet** in `brand-voice.md`. If the story needs a detail that isn't there (a specific mentee, an outage, a manager's quote), write a `[placeholder: what's needed]` and list it in the closing line. Never invent a number, a quote or an event.
2. **Anonymise clients by default**: "an enterprise Salesforce platform", "a UK healthcare client", "an ad-tech client". Name them only if he says it's cleared.
3. **Controversial doesn't mean cruel.** Hooks attack a decision, a habit or a skill gap, never a person's worth. Every threat carries its way out ("unless you..."). Predictions are his view, not fake data.
4. **Never borrow another creator's lines.** The pack takes its mechanics from other creators' posts (Pramod Dutta's in particular), but never their sentences, statistics, signatures or blue highlight.
5. **One idea, one hook, one offer per pack.**
6. **Banned words are banned everywhere**, including in rewrites of his own drafts. The full list is in `brand-voice.md`; the most common slip is "journey".
7. **Open fact: sole-QA duration.** His resume says both "5 years" and Apr 2016 – Jul 2026 for sole QA ownership of the Salesforce platform. Until he confirms which is right, avoid stating a duration for that role. Use "10+ years in QA" and "a decade later" instead.

## Final check

- [ ] The same hook opens the post, the card and the article (lightly adapted is fine).
- [ ] Every number matches across all pieces (steps, days, exercises, projects).
- [ ] Every personal claim is on the fact sheet, or appears as a `[placeholder]` that is listed in the closing line.
- [ ] Hook line 1 is at most 15 words, and each hook passes the defensibility test.
- [ ] The LinkedIn post is 150–300 words, with no emojis, no bold, no links and 3–5 hashtags.
- [ ] The post and the article each have exactly one offer, and the PS ends with "so no judgment here".
- [ ] The card text is at most 30 words in 3 blocks, with exactly two highlighted phrases (red threat, green way-out).
- [ ] The Medium article has one table, one code block, one bullet list, the "What I'd do if I started tomorrow" section, a pull quote and the bio.
- [ ] Any code is correct Playwright TypeScript: role and label locators, web-first assertions, no hard waits, credentials read from environment variables.
- [ ] No banned words, and no more than one "isn't X, it's Y" line in the post.
- [ ] The closing line lists what he must confirm, and asks at most one question.

## Partial requests, rewrites and follow-ups

- **"Just the hooks"**: give three by default. If he asks for more, give five, with at least one of each type.
- **"Just the post" or "just the image prompt"**: give only that piece, still built from a spine so it can join a pack later.
- **"Make it spicier" or "more controversial"**: raise the heat of the hooks and the card only. Keep the body calm, and apply the defensibility test again. See the heat levels in `hooks.md`.
- **"Softer"**: move the hook down one heat level and keep everything else.
- **Rewrites**: change only what he asked for, and keep all other wording. If a change breaks consistency across the pieces (for example he changes "90 days" to "60 days"), update every piece and say so in one line.
- **A new idea in the same conversation**: build a new spine. Don't reuse the previous pack's hook.
