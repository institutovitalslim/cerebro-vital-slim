# Loop Spec: {{name}}

## Goal
{{goal}}

## Loop type
{{debug | improve | research | search-and-score | review | optimization | watchdog | continuation}}

## Owner and scope
- Owner:
- Agents involved:
- Source of truth:

## Starting state
{{known_context}}

## Actions allowed autonomously
- {{allowed_action}}

## Human gates
- {{approval_gate}}

## Observations required
- {{real_evidence_required}}

## Evaluation
{{deterministic_check_or_rubric}}

## Stop conditions
Success:
- {{success_stop}}

Failure or blocker:
- {{failure_stop}}

Budget:
- max iterations: {{max_iterations}}
- max time: {{max_minutes}}

Plateau:
- {{plateau_rule}}

Human gate:
- {{approval_gate}}

## Final output
- status
- stop_reason
- evidence
- iteration trace
- remaining risks
- next_action
