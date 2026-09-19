# Image prompts (pieces 3 and 5)

Vineet generates images in tools like ChatGPT and Grok, and attaches his own headshot for the card. Both prompts have to survive a model that is bad at rendering text, so the text stays short and exact, and the Medium image has no readable text at all.

---

## A. LinkedIn: the X-style card (piece 3)

### What it is

The card is a fake screenshot of a single dark-mode post on X (Twitter), showing his photo, name, handle and the hook. This is the "Twitter style" he asked for. It stops the scroll in a LinkedIn feed because it looks like a viral tweet, and it puts his face next to the controversial line so that people connect the idea to him.

### Card text formula

Use 3 blocks, at most 30 words in total, and at most about 12 words per block.

| Block | Content | Example |
| --- | --- | --- |
| 1 | Hook line 1: the threat | "2027 is your last year as a manual tester." |
| 2 | Hook line 2: the condition or deadline | "Unless you start coding in the next 90 days." |
| 3 | The plan in numbers, or for posts without steps the sharpest proof | "1 hour a day. 300 exercises. 7 steps." / "From 70% to 99%. Same suite." |

Image models garble text easily, so follow these rules:

- Write numbers as digits.
- Avoid symbols that models mangle: →, –, —, /, &, nested quotes, ellipses.
- Don't use hashtags or emojis.
- End each block with a full stop.

### Highlight rule: fail → pass

Highlight exactly two phrases:

- The **threat phrase** in red (#F4212E), for example "last year".
- The **way-out phrase** in green (#00BA7C), for example "90 days".

Red to green is a failing test turning into a passing one. That's his visual signature, and it's deliberately different from the blue highlight the reference creator uses. If the hook has no way-out phrase, highlight only the threat in red.

### Template

```
Create a square 1:1 image (1080 × 1080) styled as a screenshot of a single post on X (Twitter) in dark mode.

Background: flat dark navy (#15202B). No gradients, no texture.

Header (top left): a circular profile photo made from the attached headshot, cropped to face and shoulders. Use the attached photo exactly; do not redraw or alter the face. To its right, the name "Vineet Verma" in bold white sans-serif, and below it the handle "[HANDLE]" in muted grey (#8B98A5). No verification badge.

Body text: left-aligned, very large white sans-serif (similar to Inter or Chirp), generous line spacing, three short blocks separated by empty lines. Render this text exactly, word for word, with nothing added:

[BLOCK 1]

[BLOCK 2]

[BLOCK 3]

Color only these words: "[THREAT PHRASE]" in bright red (#F4212E) and "[WAY-OUT PHRASE]" in bright green (#00BA7C). Everything else stays white.

Footer: a row of four thin grey outline icons evenly spaced along the bottom: reply bubble, repost arrows, heart, view-count bars. No numbers next to them.

Style: crisp, high contrast, looks like a real phone screenshot. No logos, no watermarks, no hashtags, no emojis, no extra interface elements.
```

Fill `[HANDLE]` from the personal settings in SKILL.md (@vverma1992 unless he gives an X handle).

### Notes to put before the prompt (2–3 sentences)

1. Remind him to attach his headshot when he runs the prompt.
2. Name the handle used, and that he can swap it.
3. One clause on the color logic (red threat, green way out, fail → pass).

### Troubleshooting (share only if he reports a problem)

| Problem | Fix |
| --- | --- |
| Misspelled or garbled text | Shorten the blocks and regenerate. If it keeps failing, generate the card without body text and add the text in Canva. |
| His face looks different | Re-attach the headshot and keep the line "Use the attached photo exactly; do not redraw or alter the face." |
| Wrong colors highlighted | Put each highlighted phrase in quotes and keep it to 1–3 words. |
| Real X logos or UI clutter appear | Keep the "No logos... no extra interface elements" line, and add "no top navigation bar". |
| Not square | Put "square 1:1" in the first sentence (it already is) and set the aspect ratio in the tool's own settings. |

---

## B. Medium: the cyberpunk header (piece 5)

### What it is

A cinematic 16:9 cyberpunk illustration for the top of the article. It shows the article's idea as a before/after scene without any words. The figure is seen from behind, which keeps the image universal and avoids likeness problems.

### Scene formula

- **Figure:** a lone QA engineer seen from behind, at a desk, at night, facing a wide curved monitor.
- **Split composition:** the left half is the old way or the problem, desaturated and lit by a flickering red warning light, dissolving or glitching. The right half is the new way or the solution, in neon cyan and electric green, with code and green checkmarks.
- **World:** a rain-streaked window, a blurred night city skyline, volumetric haze, a glowing circuit-board floor.
- **Mood:** tense but hopeful, a turning point.
- **Palette:** a deep navy and black base, neon cyan and electric green on the right, a faint red on the left. This is the same fail → pass logic as the card.

### Topic → metaphor

| Topic | Left half (old way / problem) | Right half (new way / solution) |
| --- | --- | --- |
| Manual → automation | Paper test-case sheets and a clipboard checklist dissolving into grey pixels | Code and a column of green checkmarks scrolling upward like a passing test run |
| Flaky tests / pipeline trust | A wall of red test tiles glitching and flickering, a "retry" lever worn smooth | One calm column of steady green tiles, pipeline lights all green |
| Release go/no-go | A chaotic control room with red alarms and tangled cables | A single glowing gate with three green indicator lights, the engineer's hand on the switch |
| AI in testing | An unrestrained robotic arm rewriting code, sparks, red warnings | The same arm inside a transparent cage of glowing rule-lines, a human hand on an approve switch |
| Salesforce / CRM testing | A storm cloud raining broken UI fragments onto a city | A stable cloud city of holographic dashboards with green status lights |
| Regression time | A giant hourglass with sand pouring slowly, dust, stacked calendars | A holographic stopwatch and streaks of light racing across the monitor |
| QA career / growth | A dim old desk with outdated button phones and a dusty CRT monitor | A modern workstation with a glowing holographic skill tree branching upward |
| Mentoring | A lone figure lost in a maze of cables | Two figures at one desk, one pointing at a glowing path on the screen |

For a topic not listed, choose one concrete "old way" object and one concrete "new way" object, then place them in the same split scene.

### Template

```
Cinematic cyberpunk illustration, 16:9 (1600 × 900), for a tech article header.

Scene: a lone QA engineer seen from behind, sitting at a desk in a dark room at night, facing a wide curved monitor. The room is split down the middle.
- Left half, the past: [OLD WAY OBJECT], [HOW IT FAILS: dissolving into grey pixels / glitching / collapsing]. Dim and desaturated, lit by a single flickering red warning light.
- Right half, the future: [NEW WAY OBJECT ON OR AROUND THE MONITOR], [SIGN OF SUCCESS: bright green checkmarks / steady green lights]. Holographic browser windows float around it, linked by thin neon lines to a glowing circuit-board floor.

Lighting: deep navy and black base, neon cyan and electric green on the right, a faint red glow on the left. Volumetric haze. A rain-streaked window in the background shows a blurred night city skyline.

Mood: tense but hopeful, a turning point.

Style: high-detail digital art, cyberpunk, sharp focus on the monitor, cinematic depth of field. No readable text, no logos, no brand names, no watermarks.
```

### Approved example (manual → automation)

```
Cinematic cyberpunk illustration, 16:9 (1600 × 900), for a tech article header.

Scene: a lone QA engineer seen from behind, sitting at a desk in a dark room at night, facing a wide curved monitor. The room is split down the middle.
- Left half, the past: a stack of paper test-case sheets and a clipboard with a handwritten checklist, dissolving into drifting grey pixels and ash-like fragments. Dim and desaturated, lit by a single flickering red warning light.
- Right half, the future: the monitor glows with lines of code and a column of bright green checkmarks scrolling upward, like a passing test run. Holographic browser windows float around it, linked by thin neon lines to a glowing circuit-board floor.

Lighting: deep navy and black base, neon cyan and electric green on the right, a faint red glow on the left. Volumetric haze. A rain-streaked window in the background shows a blurred night city skyline.

Mood: tense but hopeful, a turning point.

Style: high-detail digital art, cyberpunk, sharp focus on the monitor, cinematic depth of field. No readable text, no logos, no brand names, no watermarks.
```

### Rules

- Include no readable text. Models garble it, and Medium shows the title right above the image anyway.
- Show no real logos, product UIs or brand names (no Salesforce cloud logo, no Playwright mask).
- Don't show his face. The header is about the idea; the card carries his face.
