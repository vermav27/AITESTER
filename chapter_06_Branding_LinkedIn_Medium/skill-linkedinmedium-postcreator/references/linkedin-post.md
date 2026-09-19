# LinkedIn post (piece 2)

The post is the spine in its most compressed form: 150–300 words, aiming for about 200–230. The hook stops the scroll, the Setup proves he's earned the right to say it, the steps make it useful, and the PS starts the conversation.

## Annotated template

```text
[Hook line 1: the threat, at most 15 words]
[Hook line 2: the condition or deadline, the way out]

[Setup: 1–2 short paragraphs of real proof, first person, from the fact sheet]

[Tension line 1: what people think makes them fail]
[Tension line 2: what actually makes them fail]

The [N]-step formula I'd give anyone starting tomorrow:

→ [Step 1: verb first, carries a number, tool or rule]
→ [Step 2]
→ [...]
→ [Step N]

[Lesson line 1: the reframe]
[Lesson line 2: the hopeful turn]

PS: [One direct question tied to the steps]? [An "I've been there" admission], so no judgment here.

#QA #[Tag] #[Tag] #[Tag] #[Tag]
```

## Rules

| Rule | Detail | Why |
| --- | --- | --- |
| Length | 150–300 words, aim for 200–230 | Long enough to be useful, short enough to finish on a phone |
| Paragraphs | 1–2 sentences each, with a blank line between | White space is readability on LinkedIn |
| Steps | → arrows. Use N = the promised count, up to 7. With more than 7 steps, group them to 7 and put the full list in Medium. A story post with no steps gets exactly 3 arrows. | Arrows scan fast, and 7 is the most a feed reader will hold |
| Each arrow | Starts with a verb, carries a number, tool or rule, and runs at most ~22 words | "Build 4–5 projects" beats "Projects are important" |
| Stat lists | Use ○ circles | Keeps stats visually separate from steps |
| Formatting | No emojis, bold, italics, links or @mentions in the body | Clean text is his look; links go in the first comment |
| Hashtags | 3–5, on the last line. Always #QA; add the main tool tag. | A tag inside the body breaks the reading |
| Offer | Exactly one, usually the PS | Two offers split the reader's attention |
| Delivery | Inside a ` ```text ` block | Line breaks and arrows survive copy-paste into LinkedIn |

**Hashtag pool:** #QA #SoftwareTesting #TestAutomation #Playwright #TypeScript #Salesforce #SDET #QualityEngineering #CICD #Dynamics365 #ManualTesting #AITesting

## Beat patterns

**Setup** (always from the fact sheet, anonymised)
- "My first QA project was fully manual. Campaign workflows and data validation for an ad-tech client."
- "A decade later, I maintain a Playwright framework that turned a 5-day regression into 3 hours."
- "I was the only QA on an enterprise Salesforce platform. 24 releases a year."
- "At a UK healthcare client, I cut manual regression effort by 80%."

**Tension**
- "Most [audience] don't fail [the switch] because [the hard thing]. They fail because [the habit]."
- "When [symptom] happens, a team learns exactly one habit: [bad habit]."
- "Everyone blames [the tool]. The real problem is [the decision]."

**Step intro line**
- "The [N]-step formula I'd give anyone starting tomorrow:"
- "What moved us from [X] to [Y]:"
- "What I'd check before saying go:"

**Lesson** (resolves the controversy into hope, or uses a line from the line bank)
- "Your manual experience isn't what's holding you back. / It's your head start."
- "Automation doesn't replace judgment. / It buys you time to use it."

**PS** (question + admission + "so no judgment here")
- "PS: Which step are you stuck on right now? I started manual too, so no judgment here."
- "PS: What's your pipeline pass rate right now? I've been at 70, so no judgment here."
- "PS: How long does your full regression take today? Mine was 5 days once, so no judgment here."
- "PS: When did you last say no-go out loud? It never gets easier, so no judgment here."

## Other offers (instead of the PS, and only one per post)

| Offer | Use when | Example |
| --- | --- | --- |
| Resource | The resource already exists | "The 90-day topic list is on my GitHub. Link in the first comment." |
| Deep dive | The Medium article is live | "The full 7-step plan with code is on Medium. Link in the first comment." |
| Career | Sparingly, and only when true | "I'm open to QA Lead roles where the release call is mine to make. DMs open." |

Even when the offer is a link, the post can still end with a question. It just shouldn't carry a second call to action.

## Worked example (approved)

Input: the title "How can manual QA engineers transition into test automation roles? (7 step formula which works)" plus five rough bullets. The full input and the decisions made on it are in `example-pack.md`.

```text
2027 is your last year as a manual tester.
Unless you start coding in the next 90 days.

My first QA project was fully manual. Campaign workflows and data validation for an ad-tech client.

A decade later, I maintain a Playwright framework that turned a 5-day regression into 3 hours.

Most manual testers don't fail the switch because coding is hard.
They fail because they start five courses and finish none.

The 7-step formula I'd give anyone starting tomorrow:

→ Pick one stack: TypeScript + Playwright. No tool-hopping.
→ Write your 3-month topic list before day one.
→ Give it 1 focused hour, every single day.
→ Do 10 coding exercises a day. 300–400 total. That's what kills the fear of code.
→ Automate test cases you already run by hand. You know what's worth testing. Most beginners are guessing.
→ Build 4–5 projects, including one full end-to-end Playwright framework.
→ Push 3–4 to GitHub and post your progress here, every week.

Your manual experience isn't what's holding you back.
It's your head start.

PS: Which step are you stuck on right now? I started manual too, so no judgment here.

#QA #SoftwareTesting #TestAutomation #Playwright #TypeScript
```

How the beats map:

| Beat | Lines |
| --- | --- |
| Hook | The first two lines (deadline, then condition) |
| Setup | "My first QA project..." and "A decade later..." (fact sheet) |
| Tension | "Most manual testers don't fail..." |
| Turn | The seven arrows |
| Lesson | "Your manual experience isn't what's holding you back..." (the post's single "isn't X, it's Y") |
| Offer | The PS |
