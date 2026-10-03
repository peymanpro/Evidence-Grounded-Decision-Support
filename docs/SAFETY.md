# Safety Boundary

WealthBrain is designed as a decision-intelligence system, not an autonomous action system.

The software may organize evidence, compare alternatives, calculate deterministic scores, surface risks, and produce structured analysis. It must not silently convert an analysis result into an irreversible external action.

## Required boundaries

- Human review remains required before consequential action.
- The system must distinguish evidence from assumptions.
- Missing evidence should be visible rather than replaced by invented certainty.
- Quantitative outputs are decision-support artifacts, not guarantees.
- External model output is treated as fallible.
- Credentials and private user data must remain outside source control.

As the system grows, these boundaries should become executable policy and regression tests rather than remaining documentation only.
