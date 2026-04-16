# are_you_sure package

Portable critique module for agent decision quality.

## Files

- `models.py`: input/output schemas and enums
- `engine.py`: swappable critique engine contract + rule-based implementation
- `prompts.py`: LLM system prompt and prompt builder
- `__init__.py`: package exports

## Quick use

```python
from are_you_sure import CritiqueInput, ProposalType, RiskLevel, RuleBasedCritiqueEngine, Stage

engine = RuleBasedCritiqueEngine()
request = CritiqueInput(
    original_intent="Help the user build a safe release process.",
    current_context="Team converged quickly on skipping rollback tests.",
    proposal_type=ProposalType.DECISION,
    proposal="Ship without rollback rehearsal.",
    rationale="This is faster and likely okay.",
    constraints=["Minimize release risk"],
    risk_level=RiskLevel.HIGH,
    stage=Stage.CONVERGENCE,
    should_challenge=True,
)

result = engine.critique(request)
print(result.to_dict())
```

## Run examples and tests

```bash
python3 examples.py
python3 -m unittest discover -s tests -p 'test_*.py'
```
