# SDK Helpers

## Python

Use `sdk/python/second_thought_sdk.py`:

```python
from sdk.python.second_thought_sdk import critique, critique_auto
result = critique(payload)
result_auto = critique_auto({"request": "We are about to deploy this now."})
```

## TypeScript

Use `sdk/ts/index.ts` types and helpers for HTTP integrations.
