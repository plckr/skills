---
name: reflect-and-prevent
description: Reflect on a specific user-supplied correction, confirm it against relevant context, and propose a concise, reusable prevention measure for approval. Invoke with what the agent did wrong or should have done differently.
disable-model-invocation: true
---

# Reflect and Prevent

Usage: `/skill:reflect-and-prevent <what the agent did wrong or should have done differently>`

The user supplies the correction. Use the conversation to understand and verify
that specific incident. Keep the investigation focused on the reported issue.

If the correction is missing or materially unclear, ask the user to specify it
before analyzing. Avoid searching the entire conversation for unrelated issues.

Invoking this skill authorizes reflection and a proposal. Changes require explicit
approval after a preview.

## 1. Confirm

- Read the supplied correction and consult relevant conversation or artifacts.
- Establish what happened and what the user expected.
- Use available context before asking questions. Ask a focused question only when
  ambiguity would materially change the analysis.

## 2. Explain

- Identify the supported decision error, assumption, or missed check.
- Distinguish existing requirements from expectations introduced afterward.
- Check whether the issue arose from missing guidance or failure to apply
  existing guidance.
- State uncertainty where evidence is insufficient. Avoid speculative claims
  about internal reasoning and generic apologies.

## 3. Propose

- Suggest the smallest actionable prevention measure that addresses the cause.
- Aim for ≤200 characters per proposed rule; cap each at 250, including spaces.
  If one rule cannot preserve the necessary meaning, split it into shorter,
  independently actionable rules on separate lines. Verify lengths before
  previewing. Count only persistent rule text; explanations and approval requests
  are outside the cap.
- Make the wording reusable across contexts where appropriate. State when the
  measure applies and what the agent should check or do.
- Check relevant existing guidance. Prefer refining an appropriate existing rule
  or verification step over adding duplicate instructions.
- Check that the measure would have helped in this incident while preserving
  legitimate alternatives and avoiding unnecessary questions or restrictions.
- Choose the appropriate owner and scope: personal guidance, project guidance,
  a skill, or a focused test or validation.
- Show the exact proposed change, its destination, and any guidance it would
  replace or amend. Exclude secrets and unnecessary incident details.
- Recommend no persistent change when one is unnecessary or unsupported.
- Use examples only when needed to resolve ambiguity.

Keep the response concise and proportional to the correction. Present the
confirmation, explanation, and proposal clearly, then ask for approval and stop.

## 4. Approve and apply

- Wait for explicit approval of the previewed change and destination before
  modifying instructions, code, configuration, or other artifacts.
- If the proposal changes materially, present the revised proposal for approval.
- Apply only the approved scope.
- Check for duplication, contradictions, and unintended changes. Run the smallest
  sufficient verification.
- Summarize what changed and what was verified. State material enforcement limits
  without promising that recurrence is impossible.
