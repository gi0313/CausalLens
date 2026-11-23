# Causal Inquiry Integration Contract

## Purpose

This prototype defines how the causal analysis component hands a causal
question to the Neo4j component before any causal method has evaluated
the relationship.

## Current status

The example record has the status `not_evaluated`. It must not be
converted into a `CAUSES` relationship. The selected P30 and T30
measurements are actual FD001 variables used to test the integration
path. Their selection does not assert that P30 causes T30.

## Neo4j mapping for this prototype

- Create one `CausalInquiry` node from the inquiry metadata.
- Create or match two `Measurement` nodes using the `key` property.
- Connect the inquiry to the proposed input with
  `HAS_CANDIDATE_SOURCE`.
- Connect the inquiry to the proposed target with `HAS_TARGET`.
- Create or match `EvidenceSource` nodes and connect them with
  `SUPPORTED_BY`.
- Preserve the status, assumptions, and limitations.
- Do not create `CAUSES` until a reviewed causal-analysis result
  supports that relationship.

## Future transition

After an appropriate method is selected, executed, and evaluated, a
later version of the contract may record the method, estimated effect,
stability evidence, counterfactual result, and review decision. The
relationship status can then move from `not_evaluated` to `candidate`,
`supported`, or `rejected`.