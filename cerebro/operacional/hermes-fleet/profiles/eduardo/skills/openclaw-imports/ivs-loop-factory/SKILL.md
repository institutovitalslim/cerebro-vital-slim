---
name: ivs-loop-factory
description: Use when Tiaro, Maria or any IVS agent needs to create, run, review, continue, audit, or standardize a closed-loop workflow with state, trace, evaluation, stop reason, evidence gate, human gates, or cross-run continuation.
---

# IVS Loop Factory

## Overview

A loop is not a strong prompt. A loop is a control system:

```text
state -> observe -> act -> evaluate -> decide -> improve or stop
```

Use this skill to turn repeated IVS work into governed loops that carry state, record evidence, avoid false DONE, and stop cleanly on success, blocker, plateau, budget, or human gate.

## When to Use

Use for:

- leads/agendamentos/watchdogs;
- content/reels/ad creative iteration;
- SEO/AEO authority work;
- finance spend audits;
- repo/code/skill improvement;
- long jobs that cross sessions;
- any process where "continuar até concluir" needs evidence and state.

Do **not** use for a simple one-shot answer with no feedback signal.

## Mandatory IVS Loop Contract

Every IVS loop must define:

| Field | Required meaning |
|---|---|
| `goal` | target state, not vague activity |
| `state` | current facts, attempt count, blockers, best result |
| `allowed_actions` | what the agent may do alone |
| `human_gates` | send/publish/spend/write-sensitive actions |
| `eval` | deterministic check or rubric before iteration starts |
| `stop_conditions` | success, blocker, budget, plateau, risk |
| `trace` | action -> real observation -> eval -> decision |
| `final` | status, stop_reason, evidence, next_action |

## Status and Stop Reason

Allowed final statuses:

```text
DONE — delivered and verified with evidence
DONE_WITH_CONCERNS — delivered, with explicit risk/pendência
PARTIAL — some items validated, others not; never call complete
BLOCKED — real blocker verified, next step clear
NEEDS_APPROVAL — human gate reached
DELEGATED — owner/handoff created with acceptance criteria
```

Allowed stop reasons:

```text
success | plateau | blocked | budget_exhausted | human_gate | delegated
```

## Evidence Gate

The loop cannot say `DONE` without real evidence:

| Work type | Minimum evidence |
|---|---|
| file/report | path + file exists + readable content |
| code/script | py_compile/test/smoke/log output |
| cron/process | job/session id + status/output |
| message sent | real messageId + destination |
| API/integration | status/body/log sanitized |
| course/class | validated transcript; missing transcript = PARTIAL/BLOCKED |
| lead/patient | real conversation/log; no PII in report |
| finance/Omie | read-only evidence; writes need explicit gate |
| external publish | pre-approval + resulting URL/id |

## Human Gates IVS

Stop before:

- sending WhatsApp/Telegram/email/DM to lead, patient, partner, or external person;
- publishing content;
- spending money or changing ad budgets;
- writing to Omie, QuarkClinic, finance, permissions, access control;
- pausing/despausing Clara unless Tiaro explicitly ordered;
- making clinical/medical claims without Ana/Dra. Daniely validation;
- deleting/overwriting important records.

## Quick Start

```bash
python3 scripts/create_ivs_loop.py --preset clara-revenue-watchdog --out /tmp/ivs-loop-run
python3 scripts/validate_loop_trace.py /tmp/ivs-loop-run
```

Or manually copy:

- `templates/loop-spec.md`
- `templates/state.json`
- `templates/trace.md`
- `templates/stop-reason.md`

## Presets

| Preset | Owner | Use |
|---|---|---|
| `clara-revenue-watchdog` | Clara + Maria | leads/agendamentos, preço antes da jornada, no-reply |
| `joao-content-loop` | João | ingest content, detect spikes, generate/re-score safe variations |
| `seo-aeo-authority-loop` | João + Ana | authority content, local SEO, AI answer optimization |
| `partner-outbound-loop` | Maria + João | B2B partnerships; drafts only until approval |
| `pedro-finance-spend-loop` | Pedro | duplicate spend, renewals, unused tools, contractor spend |
| `repo-skillification-loop` | Maria + Jarvis | turn repeated failures/procedures into skills/scripts/rules |
| `continuation-handoff-loop` | all agents | state/trace across runs; prevent drift and false completion |

## How Agents Should Apply

1. Pick a preset or create a custom `loop-spec.md`.
2. Initialize `state.json` and `trace.md`.
3. Run one iteration at a time.
4. After each action, record real evidence and decision.
5. Stop only on an allowed stop reason.
6. Return final status with evidence and next action.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Calling a one-shot answer a loop | Require repeated observe/eval/decision or label it one-shot |
| No eval before action | Write deterministic check/rubric first |
| Claiming DONE from exit code only | Verify artifact/count/content/log |
| Endless polishing | Use plateau/budget stop |
| Sending/publishing automatically | Human gate |
| Carrying whole transcript | Carry compact state and paths |
| Hiding uncertainty | Use PARTIAL/BLOCKED and name missing evidence |

## Output Format

```text
Status: DONE | DONE_WITH_CONCERNS | PARTIAL | BLOCKED | NEEDS_APPROVAL | DELEGATED
Loop:
Stop reason:
Evidence:
Iterations:
Remaining risks:
Next action:
```
