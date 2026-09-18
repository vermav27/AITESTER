# Hooks (piece 1)

The hook is the only part most people will ever read. On LinkedIn it has to land before the "...see more" cut, which is roughly the first two lines. Vineet wants these hooks to be controversial: they should make a tester stop scrolling because the line feels a little too true.

Controversy works here because it points at a decision the reader can still change, and the post then shows them how to change it. A threat with a way out is a warning. A threat without one is just fear.

## The three-hook set

Always deliver all three types.

| Slot | Type | Formula | Example (manual → automation) |
| --- | --- | --- | --- |
| A | **Deadline** | "[Next year] is your last year as a [role]. Unless you [action] in the next [window]." | "2027 is your last year as a manual tester. Unless you start coding in the next 90 days." |
| B | **Identity flip** | "[Field] isn't dying. [The group that won't change] [is/are]." | "Manual testing isn't dying. Manual-only testers are." |
| C | **Evidence** | "I [real result with a number from the fact sheet]. [An uncomfortable implication or question]." | "I automated 80% of a client's manual regression. Ask yourself who was doing that 80% before." |

**Hook A is the default** for the post, the card and the Medium opening. The deadline carries the threat and the condition carries the way out, so the whole promise fits in two lines.

When the topic has no natural deadline (a flaky-test post, for example), lead with B or C instead. Tell him which hook you used.

**Hook C is his differentiator.** Other creators can write A and B. Only he can write C, because it stands on his own numbers. Note in one clause why it's the most "him" of the three.

**Year rule.** "Next year" means today's year + 1. In 2026 that's "2027 is your last year as...". Don't hard-code 2027.

**Window rule.** The window has to match the plan in the pack. A 3-month roadmap gets "90 days"; a 30-day challenge gets "30 days".

## Bench formulas

Use these when A, B or C doesn't fit the topic, or when he asks for more than three hooks.

| Type | Formula | Example |
| --- | --- | --- |
| Myth kill | "'[Popular belief]' is the most expensive lie in QA." | "'We'll automate it later' is the most expensive lie in QA." |
| The number that hurts | "[Real stat]. [What it really means]." | "Our pipeline passed 70% of the time. So nobody trusted it 100% of the time." |
| Conditional list | "If [symptom], one of these is true:" | "If your regression takes longer than your sprint review, one of these is true:" |
| Proof gap | "Your [credential] says [claim]. Your [evidence] says whether it's true." | "Your certificate says you know Playwright. Your GitHub says whether you do." |
| Wrong question | "Everyone asks [common question]. The real question is [better one]." | "Everyone asks which tool to learn. The real question is whether you'll still be typing in week 6." |

## Heat levels

| Level | When | Example |
| --- | --- | --- |
| Warm | He asks for "softer", or the topic is sensitive (layoffs, health) | "Manual testing skills still matter. Manual-only careers are getting shorter." |
| **Hot (default)** | Every pack unless told otherwise | "2027 is your last year as a manual tester. Unless you start coding in the next 90 days." |
| Very hot | He asks for "spicier" or "more controversial" | "Still only testing by hand in 60 days? You're training your own replacement." |

When he asks for more heat, raise the hook and the card only. The body stays calm. That contrast is what makes a very hot hook read as tough love rather than a rant.

## The defensibility test

Run these five checks on every hook before sending it.

1. **Target.** Does it attack a decision, a habit or a skill gap, and not a person's worth or intelligence?
2. **Way out.** Does the hook, or its second line, contain the escape ("unless...", "if you...")? Hook B is the exception: the post supplies its way out.
3. **Truth.** Are there no invented statistics? Is any prediction clearly his view rather than data? "2027 is your last year" works as rhetoric; "73% of manual testers will be laid off" is a fake stat.
4. **Comment-proof.** If someone pushes back in the comments, could he defend it from his own work?
5. **Mechanics.** Is line 1 at most 15 words? Are there no banned words and no emojis? Is it not a copy or close echo of another creator's line?

## Rewriting his raw hooks

He often sends drafts that have the right heat but the wrong mechanics. Keep the heat and fix the rest. These are the rewrites from the first approved pack:

| His draft | What's wrong | Rewrite |
| --- | --- | --- |
| "If you are not switching to automation in the next 2 months, your manual testing journey is gone." | "journey" is banned; 2 months didn't match the 3-month plan; the line was long | "2027 is your last year as a manual tester. Unless you start coding in the next 90 days." |
| "If you are staying in a manual testing role for the next 2 months, AI and automation people are going to replace you soon, my friend." | 27 words; the threat was buried at the end | "Manual testing isn't dying. Manual-only testers are." |
| "2027 will be the last manual tester year for you if you are not learning automation plus AI. 7 steps to save yourself" | Awkward grammar; the condition was buried | Merged into Hook A. The "7 steps" promise moved into the post body and the card's third line. |

## Hook examples by pillar

These are ready-made starting points. Adapt the numbers to the pack.

**Release ownership**
- "A green build is not a release decision. It's one input." (identity flip)
- "If you can't say 'no-go' out loud, you're not leading QA. You're watching it." (very hot)

**Automation that earns trust**
- "Rerunning a failed test isn't debugging. It's hoping." (myth kill)
- "Your 500 automated tests are worthless if nobody trusts the red." (hot)

**Manual → automation**
- "2027 is your last year as a manual tester. Unless you start coding in the next 90 days." (deadline)
- "You don't have a coding problem. You have a 300-exercise problem." (wrong question)

**Enterprise CRM & healthcare**
- "Salesforce updates your org three times a year. If your tests can't survive that, they're not tests." (hot)
- "Testing Salesforce like a normal website is how regressions reach your sales team." (myth kill)

**AI in testing, learned in public** (only once he has run the experiment)
- "An AI can write 100 tests in 10 minutes. It can't tell you which 10 matter." (identity flip)
- "If AI writes your tests and nobody reviews them, you've automated your blind spots." (hot)

**The long QA career**
- "11 years at one company isn't a red flag. Staying 11 years without learning is." (identity flip, from the fact sheet)
- "I was one of India's top 3 developers on a platform that no longer exists." (evidence)

## How to present the hooks

```
## Three controversial hooks

1. **"[Hook A]"** This is the one I used in the post and the image.
2. **"[Hook B]"**
3. **"[Hook C]"** This one is built on your real [number/fact], so it's the most "you" of the three.
```

If you changed his wording (a window or a banned word, for example), say so in the pack's opening line, not in the hook list.
