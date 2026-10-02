# PayPilot Prompt Governance Policy (v1)

**Applies to:** every change to the PayPilot system prompt, its examples, and its tool descriptions.
**Starts:** next week. This is the minimum version and will be extended once the team has run it for one release.

## 1. Roles

| Role | Who | Owns | Approves |
|---|---|---|---|
| **Requirement owner** | Product (business rules, quotes, scope) **or** Support (tone, escalation, customer wording), depending on the requirement being changed | The wording and intent of the requirement; writes the change and the changelog entry | Nothing. An owner cannot approve their own change |
| **Change reviewer** | QA | Runs the release criterion in section 2 | Release yes / no |
| **Compliance approver** | Compliance | Fee and rate disclosure, thresholds, compliance-review handling, fraud rules (§5, and the fraud parts of §4) | Required for any change touching these; can block a release |

**Rule:** the owner and the reviewer of a change are never the same person. If QA wrote a change, someone else in QA reviews it, or the release waits until another reviewer is available.

## 2. Ready for release

A change ships only when **all** of these are true. The reviewer ticks each one in the changelog entry.

1. **Verifiable.** Every new or changed line names an observable output, a pass/fail criterion and a violation example. A line that fails this check goes back to the owner.
2. **No new conflict.** The reviewer has read the changed line against every other section and the user stories it touches. Any conflict found is either resolved or listed under "Not measured / open".
3. **Stand runs.** The regression set (for now, the scenarios from the specification review) is run **5×** on the new version and **5×** on the current version:
   - **Grounding:** 0 runs with a number that isn't in a tool result.
   - **Fabrication:** 0 runs with invented product terms.
   - **Escalation:** 0 runs with a missed required escalation.
   - **No regression:** no scenario that passed on the current version fails on the new one.
4. **Compliance sign-off** is recorded, if the change touches the areas in section 1.
5. **Rollback** is possible. The previous version is tagged and can be restored without editing.

## 3. Changelog (`prompts/CHANGELOG.md`)

Each release gets one entry with:

- **Version and date**
- **Owner**, **reviewer**, and **compliance approver** (or "not required")
- **What changed:** section, the line before, the line after
- **Reason:** the finding ID, ticket or incident behind the change
- **Evidence:** result of the verifiability check, run counts and results for both the new and the current version
- **Not measured / open:** known conflicts, untested paraphrases, scenarios not covered
- **Rollback to:** the previous version tag

An entry without evidence, or without both names, means the change isn't released.

## 4. Triggers for an unscheduled review

Any of these starts a review of the affected sections within **5 working days**, even if no prompt change was planned:

- **Model change:** new model version, provider, or settings such as temperature.
- **Tool change:** a tool is added, removed or renamed, or its output format changes.
- **Content change:** the tariff schedule, tier spreads, allowances or knowledge-base product content change.
- **Rule change:** a new or changed regulatory or internal policy on fee disclosure, fraud or customer communication.
- **One serious production incident:** a wrong figure quoted, a product term invented, a required escalation missed, or a threshold or compliance review revealed. One case is enough.
- **New feature in scope:** for example, the agent starts executing conversions instead of only quoting.

The person who spots the trigger opens a ticket. The owner of the affected section runs the review, and QA reviews it as described in section 2.

---
*Planned review: once per release cycle.*
