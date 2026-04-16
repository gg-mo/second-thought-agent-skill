# SDK Helpers

## Python

Use `sdk/python/are_you_sure_sdk.py`:

```python
from sdk.python.are_you_sure_sdk import critique, critique_auto
result = critique(payload)
result_auto = critique_auto({"request": "We are about to deploy this now."})
```

## TypeScript

Use `sdk/ts/index.ts` types and helpers for HTTP integrations.
