# Safety Boundary

Evidence-Grounded Decision Support is designed as a decision-intelligence system, not an autonomous action system.

The software may organize evidence, compare alternatives, calculate deterministic scores, surface risks, and produce structured analysis. It must not silently convert an analysis result into an irreversible external action.

## Required boundaries

- Human review remains required before consequential action.
- The system must distinguish evidence from assumptions.
- Missing evidence should be visible rather than replaced by invented certainty.
- Quantitative outputs are decision-support artifacts, not guarantees.
- External model output is treated as fallible.
- Credentials and private user data must remain outside source control.

## Executable policy

The current safety policy is implemented in `src/wealthbrain/modules/safety/service.py` and exposed through the decision safety-check API.

- `analysis` is allowed as decision support while retaining human review.
- `recommendation` is blocked without acknowledgement, sufficient evidence, or when high-risk items remain.
- `external_action` is denied by the application boundary.

The policy is covered by automated regression tests in `tests/test_ai_safety_integration.py` and `tests/test_safety_contracts.py`.

Broader adversarial testing, sensitive-data controls, and final public-deployment review remain future hardening work.
