# SentinelRx Robustness Benchmark

## Standard synthetic regression suite
- 120 cases
- SentinelRx F1: 1.000
- Exact-case accuracy: 1.000
- Naive baseline F1: 0.600

## Robustness / failure-handling suite
- 90 edge and incomplete synthetic cases
- Verified-finding exact accuracy: 1.000
- Abstention-behavior accuracy: 1.000
- Crash rate: 0.000

### Included failure modes
- unknown transition context
- missing medication identity
- missing dosage
- malformed Bundle entries
- duplicate discharge resources
- dose changes
- clean controls

These results demonstrate deterministic behavior over generated test conditions only. They are not clinical validation and must not be presented as real-world clinical performance.
