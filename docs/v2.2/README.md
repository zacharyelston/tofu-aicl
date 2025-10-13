# AICL CLI Spec v2.2: Contract-Based Testing

**Approach:** Define behavior contracts, not implementation details

## Philosophy

Test **WHAT** the code does, not **HOW** it does it.

Each contract specifies:
- Input/Output interface
- Expected behavior
- Edge cases
- Points for compliance

Freedom in:
- Architecture (monolithic vs modular)
- Libraries (any you want)
- Implementation style (OOP, functional, etc.)

## Contracts

| Contract | Behavior | Points | Validation |
|----------|----------|--------|------------|
| Configuration | Load settings | 25 | Behavioral tests |
| Logging | Structured output | 15 | Log inspection |
| Docker Execution | Run in container | 30 | Command validation |
| Local Execution | Run on host | 20 | Process execution |
| CLI Interface | User commands | 30 | End-to-end tests |
| State Management | Query state | 20 | Data verification |
| Error Handling | Graceful failures | 10 | Error scenarios |

**Total:** 150 points

## Contract Files

- `contract-1-configuration.md`
- `contract-2-logging.md`
- `contract-3-docker.md`
- `contract-4-local.md`
- `contract-5-cli.md`
- `contract-6-state.md`
- `contract-7-errors.md`

## Grading

```python
# Each contract is pass/fail
for contract in contracts:
    if all_behaviors_pass(contract):
        score += contract.points
        
# No partial credit per contract
# Either the contract is fulfilled or not
```

## Benefits

✅ **Maximum freedom** - Implement however you want  
✅ **Clear expectations** - Behavior is specified  
✅ **Black-box testing** - Only test interfaces  
✅ **Encourages creativity** - Find better solutions  
✅ **Language agnostic** - Could test Python, Go, Rust implementations

## Usage

```bash
# Test contract compliance
python test_contract.py config cli/config.py
python test_contract.py logging cli/logging_setup.py
python test_contract.py docker cli/

# Full validation
python validate_contracts.py --all
```
