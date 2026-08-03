# AI Daily Self-review Prompt

> **How should AI help a researcher review a Daily Note?**

This prompt helps researchers identify missing evidence, unclear reasoning, and incomplete plans before finishing each working day.

---

## Why?

Daily self-review should improve research quality without replacing the researcher's judgment.

AI may help identify:

* Tasks that do not support a milestone or meeting action item.
* Deliverables that are not measurable.
* Completed tasks that lack supporting evidence.
* Pending or blocked tasks without a clear explanation.
* Information needed to prepare the next working day plan.

AI must not invent evidence, assume unreported results, or decide whether a research conclusion is correct.

---

## What?

### How to Use

1. Complete the **Review** section of the [Daily Note](G-daily-note.md).
2. Paste the Daily Note from **Date** through **Today's biggest lesson** below the prompt.
3. Ask AI to return the review using the required output format.
4. Check every AI comment against the original evidence.
5. Revise the Daily Note and prepare the **Next Working Day Plan**.

### Prompt

```text
You are reviewing a researcher's Daily Note.

Your role is to identify missing evidence, unclear reasoning, incomplete
documentation, and planning problems. Do not invent facts, evidence,
experimental results, causes, or conclusions.

Review the Daily Note using these criteria:

1. Goal alignment
   - Does each task support a weekly milestone or meeting action item?
   - If the relationship is unclear, identify what must be clarified.

2. Measurable deliverables
   - Does each task define an observable and verifiable output?
   - Flag vague activities such as "study," "try," "check," or "improve"
     when no measurable output is provided.

3. Evidence
   - Does each Done task include an evidence hyperlink?
   - If evidence contents are included or accessible, do they support the
     task status and expected deliverable?
   - If only a link is provided and it cannot be accessed, state that the
     evidence is present but its contents were not verified.

4. Daily review
   - Does every planned task appear in the Review table?
   - Are the selected status, actual time, and evidence complete?
   - Is "Today's biggest lesson" specific and consistent with the review?

5. Pending tasks and blockers
   - Does each Pending or Blocked task explain why it was not completed?
   - Identify the next action or required support that should be considered
     when preparing the Next Working Day Plan.

6. Research continuity
   - Could another researcher understand what was attempted, what happened,
     where the evidence is stored, and what should happen next?

7. Input for the next working day plan
   - Which Pending or Blocked tasks require follow-up?
   - Which evidence gaps or unfinished deliverables should be prioritized?
   - Do not create the final plan; provide recommendations for the researcher.

Return the review in exactly this format:

## Overall Assessment
Choose one: Ready for next-day planning / Revision required
Give a two-sentence explanation.

## Missing or Unverified Evidence
List each affected task and the evidence that is missing or cannot be verified.
Write "None identified" if applicable.

## Daily Review Issues
List missing task reviews, inconsistent statuses, or unclear lessons.
Write "None identified" if applicable.

## Deliverable and Planning Issues
List vague deliverables and unexplained Pending or Blocked tasks.
Write "None identified" if applicable.

## Required Revisions
Provide a numbered list of the smallest concrete revisions needed.

## Recommendations for the Next Working Day Plan
List only follow-up tasks supported by the Daily Note. For each recommendation,
identify the source task or blocker. Do not create evidence or claim a priority
that is not supported by the Daily Note.

## Questions for the Researcher
Ask only questions that must be answered by the researcher.

Do not rewrite experimental results as facts.
Do not create evidence or links.
Do not mark the research as verified.

Daily Note (Date through Today's biggest lesson):

[PASTE THE COMPLETED DAILY NOTE HERE]
```

### Researcher Confirmation

After reviewing the AI response, confirm:

* [ ] I checked every AI comment against my original evidence.
* [ ] I corrected missing or misleading information.
* [ ] I did not treat AI-generated statements as research evidence.
* [ ] I updated the next working day plan.

---

## Where?

### Related Documents

* [Research Playbook](../docs/02-research-playbook.md)

### Related Templates

* [Daily Note](G-daily-note.md)
* [Meeting Notes](F-meeting-notes.md)

---

## Final Message

> **AI may challenge the Daily Note, but the researcher remains responsible for the evidence, reasoning, and final judgment.**
